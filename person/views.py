import json

from flask import request
from flask_restx import Namespace, Resource
from keycloak import KeycloakPutError
from requests import HTTPError

from api import settings
from keycloak_interface.errors import KeycloakACError, MissingTokenError
from keycloak_interface.keycloakInterface import KeycloakInterface
from keycloak_interface.utils.functions import get_keycloak_user, get_keycloak_user_by_email
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
