from flask import request
from flask_restx import Namespace, Resource

from api import settings
from keycloak_interface.errors import MissingTokenError, KeycloakACError
from keycloak_interface.keycloakInterface import KeycloakInterface
from keycloak_interface.utils.functions import get_keycloak_organization_groups, create_keycloak_organisation_group, \
    get_keycloak_organisation_roles, create_keycloak_organisation_role, extract_header_token

api: Namespace = Namespace('Orgs', description='ExtremeXP Organisations Endpoints')

keycloak_interface = KeycloakInterface(
    server_url=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_SERVER_URL'),
    realm_name=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_REALM'),
    client_id=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_ID'),
    client_secret_key=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_SECRET_KEY')
)


@api.route("/groups")
class OrgGroupsView(Resource):
    @api.doc('list_orgs_groups')
    def get(self):
        token = extract_header_token(request)
        if not keycloak_interface.validate_request_token(token):
            return {'error': 'Invalid or missing token'}, 401

        # TODO: Implement logic to fetch policies from blockchain

        return {"message": "TODO"}, 200