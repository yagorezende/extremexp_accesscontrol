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
        try:
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                raise MissingTokenError()
            else:
                token = token.split(' ')[1]
            org_groups = get_keycloak_organization_groups()
            response = {
                'orgs_groups': org_groups
            }

            return response, 200
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code

    @api.doc('create_orgs_groups')
    def post(self):
        try:
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                raise MissingTokenError()
            else:
                token = token.split(' ')[1]
            payload = request.json
            group_name = payload.get('name')

            if not group_name:
                return {'error': 'Group name is required'}, 400

            # Validate group name
            if not isinstance(group_name, str) or not group_name.isalnum() or ' ' in group_name\
                    or len(group_name) < 3 or len(group_name) > 50:
                return {'error': 'Invalid group name! The group name cannot have special characters and must have at least three characters.'}, 400

            group_id = create_keycloak_organisation_group(group_name)
            if group_id is None:
                return {'error': f'Group {group_name} already exists'}, 400
            group = {
                "id": group_id,
                "name": group_name,
                "path": f"/{group_name}",
                "subGroups": []
            }
            return {'message': f'Group {group_name} created successfully', "group": group}, 201
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code

@api.route("/roles")
class OrgGroupsView(Resource):
    @api.doc('list_orgs_roles')
    def get(self):
        try:
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                raise MissingTokenError()
            else:
                token = token.split(' ')[1]
            roles = get_keycloak_organisation_roles()
            if not roles:
                return {'message': 'No roles found'}, 404
            return {"roles": list(roles.values())}, 200
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code

    @api.doc('create_orgs_groups')
    def post(self):
        try:
            if not keycloak_interface.validate_request_token(extract_header_token(request)):
                return {'error': 'Invalid or missing token'}, 401

            payload = request.json
            role_name = payload.get('name')

            if not role_name:
                return {'error': 'Role name is required'}, 400

            # Validate group name
            if not isinstance(role_name, str) or ' ' in role_name\
                    or len(role_name) < 3 or len(role_name) > 50:
                return {'error': 'Invalid role name! The role name cannot have special characters and must have at least three characters.'}, 400

            role_id = create_keycloak_organisation_role(role_name)
            if role_id is None:
                return {'error': f'Group {role_name} already exists'}, 400
            return {'message': f'Role {role_name} created successfully'}, 201
        except MissingTokenError as e:
            return {'error': e.message}, 401
        except KeycloakACError as e:
            return {'error': str(e)}, e.error_code
