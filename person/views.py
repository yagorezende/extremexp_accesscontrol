from flask import request
from flask_restx import Namespace, Resource
from requests import HTTPError

from api import settings
from keycloak_interface.errors import KeycloakACError, MissingTokenError
from keycloak_interface.keycloakInterface import KeycloakInterface
from keycloak_interface.utils.functions import get_keycloak_user, get_keycloak_user_by_email, \
    extract_header_token
from keycloak_interface.utils.handlers import KeyCloakRootConnection
from models.models import PersonDAO

api: Namespace = Namespace('Person', description='ExtremeXP Person Endpoints')

person_model = api.model('Person', PersonDAO.structure)

DAO = PersonDAO()

keycloak_interface = KeycloakInterface(
    server_url=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_SERVER_URL'),
    realm_name=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_REALM'),
    client_id=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_ID'),
    client_secret_key=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_SECRET_KEY')
)


@api.route("/login")
class PersonLoginView(Resource):
    @api.doc('login', params={
        'username': 'Username',
        'password': 'Password'
    })
    def post(self):
        # get username and password
        username = api.payload['username']
        password = api.payload['password']

        try:
            response, status_code = keycloak_interface.authenticate(username, password)

            if status_code != 200:
                if get_keycloak_user(username) is not None:
                    response["error_description"] = f"Invalid password"
                    response["error_code"] = 4011
                else:
                    response["error_description"] = f"User not found"
                    response["error_code"] = 4012

            return response, status_code
        except HTTPError as e:
            return {'error': str(e)}, 401


@api.route("/userinfo")
class PersonInfoView(Resource):
    @api.doc('userinfo', security='bearerAuth')
    def get(self):
        try:
            token = request.headers.get('Authorization')

            if not token or not token.startswith('Bearer '):
                raise MissingTokenError()
            else:
                token = token.split(' ')[1]
            response, status_code = keycloak_interface.userinfo(token)
            return response, status_code
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code
        except MissingTokenError as e:
            return {'error': e.message}, 401


@api.route("/register")
class PersonRegisterView(Resource):
    @api.doc('register', params={
        'username': 'Username',
        'password': 'Password',
        'email': 'Email',
        'name': 'User Full Name'
    })
    def post(self):
        # get username and password
        username = api.payload['username']
        password = api.payload['password']
        email = api.payload['email']
        name = api.payload['name']

        try:
            response, status_code = keycloak_interface.create_user(
                username,
                password,
                email,
                name
            )

            if status_code != 201:
                response = {"error": "Register conflict"}
                status_code = 409
                if get_keycloak_user(username) is not None:
                    response["error_description"] = "Username already registered"
                    response["error_code"] = 4091
                elif get_keycloak_user_by_email(email) is not None:
                    response["error_description"] = "Email already registered"
                    response["error_code"] = 4092
            return response, status_code
        except Exception as e:
            return {'error': "Internal server error", "error_description": str(e), "error_code": 500}, 500

@api.route("/user")
class PersonView(Resource):
    @api.doc('list_person', params={'page': 'Page number to retrieve', 'size': 'Number of users per page'})
    def get(self):
        try:
            token = extract_header_token(request)
            if not keycloak_interface.validate_request_token(token):
                return {'error': 'Invalid or missing token'}, 401

            first = request.args.get('page', 1, type=int)
            max = request.args.get('size', 10, type=int)
            params = dict(request.args)

            query = {
                'first': ((first - 1) * max) if first > 1 else 1,
                'max': max
            }
            query.update(params)

            if 'exact' in query:
                query['exact'] = query['exact'] == 'true'

            users_count = KeyCloakRootConnection().get_keycloak_user_list_count(query)
            users = KeyCloakRootConnection().get_keycloak_user_list(query)
            current_url = request.base_url + '?'

            # Remove pagination parameters from the URL to avoid duplication
            if 'page' in params:
                params.pop('page')
            if 'size' in params:
                params.pop('size')
            params_str = '&'.join([f"{key}={value}" for key, value in params.items()])
            if params_str:
                current_url += params_str

            response = {
                "count": users_count,
                "next": current_url + f'&page={first + 1}&size={max}' if (first * max) < users_count else None,
                "previous": current_url + f'&page={first - 1}&size={max}' if first > 1 else None,
                "results": users,
            }

            return response, 200
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code

@api.route("/user/<string:uuid>")
class PersonView(Resource):
    @api.doc('get_person', params={'uuid': 'UUID of the person'})
    def get(self, uuid):
        try:
            token = extract_header_token(request)
            if not keycloak_interface.validate_request_token(token):
                return {'error': 'Invalid or missing token'}, 401
            response, status_code = keycloak_interface.userinfo(token)
            return response, status_code
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code

    def patch(self, uuid):
        try:
            if not keycloak_interface.validate_request_token(extract_header_token(request)):
                return {'error': 'Invalid or missing token'}, 401

            payload = request.json
            keycloak_root_connection = KeyCloakRootConnection()

            # TODO: integrate with the blockchain to update the user groups
            if payload.get('groups'):
                group_ids = []
                for group in payload['groups']:
                    group_data = keycloak_root_connection.get_group(group)
                    if group_data is None:
                        return {'error': f'Group {group} does not exist'}, 404
                    group_ids.append(group_data.get('id'))

                for group_id in group_ids:
                    keycloak_root_connection.set_user_group(uuid, group_id)

            # TODO: integrate with the blockchain to update the user role
            if payload.get('role'):
                role = payload.get('role')
                role_obj = keycloak_root_connection.get_realm_role(role)
                if role_obj is None:
                    return {'error': f'Role {role} does not exist'}, 404
                keycloak_root_connection.set_user_role(uuid, role_obj)

            if payload.get('attributes'):
                attributes = payload.get('attributes')
                # TODO: Validate attributes format
                keycloak_root_connection.set_user_attributes(uuid, attributes)

            return {"message": "TODO", "payload": payload}, 200
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code
