from flask import request
from flask_restx import Namespace, Resource
from requests import HTTPError

from api import settings
from keycloak_interface.errors import KeycloakACError, MissingTokenError
from keycloak_interface.keycloakInterface import KeycloakInterface
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
class PersonLoginView(Resource):
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
            return response, status_code
        except HTTPError as e:
            return {'error': str(e)}, 401
