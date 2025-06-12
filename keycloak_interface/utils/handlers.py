from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection

from api import settings


class KeycloakHandler:
    def __init__(self, environ):
        self.environ = environ
        self.connection = None
        self.keycloak_admin = None

    def connect(self, user, password):
        if self.environ is None:
            raise Exception("Environment variables not found")
        self.connection = KeycloakOpenIDConnection(
            server_url=self.environ.KEYCLOAK_CONFIG.get("KEYCLOAK_SERVER_URL") + "/realms",
            username=user,
            password=password,
            realm_name=self.environ.KEYCLOAK_CONFIG.get("KEYCLOAK_REALM"),
            client_id="admin-cli",
            user_realm_name="master",
        )
        self.keycloak_admin = KeycloakAdmin(connection=self.connection)
        return self

    def get_realm_roles(self):
        roles = self.keycloak_admin.get_realm_roles()
        to_dict = {}
        for role in roles:
            if role['description'] == '${role_b2blue-roles}':
                to_dict[role['name']] = role
        return to_dict

    def get_realm_role(self, role_name):
        return self.keycloak_admin.get_realm_role(role_name)

    def get_user(self, user_id):
        return self.keycloak_admin.get_user(user_id)

    def get_user_role(self, user_id):
        return self.keycloak_admin.get_realm_roles_of_user(user_id)

    def set_user_role(self, user_id, role):
        self.keycloak_admin.assign_realm_roles(user_id, role)

    def get_keycloak_user_by_email(self, email):
        try:
            users = self.keycloak_admin.get_users(query={"email": email, "max": 1, "exact": True})
            return users[0] if len(users) == 1 else None
        except Exception as e:
            return None

    def get_keycloak_user(self, username):
        try:
            return self.keycloak_admin.get_user(self.keycloak_admin.get_user_id(username))
        except Exception as e:
            return None

    def get_keycloak_user_id(self, username):
        return self.keycloak_admin.get_user_id(username)

    def create_keycloak_user(self, data):
        try:
            return self.keycloak_admin.create_user({
                "email": data['email'],
                "username": data['username'],
                "enabled": True,
                "firstName": data['name'].split(' ')[0],
                "lastName": ' '.join(x for x in data['name'].split(' ')[1::]),
                "emailVerified": True,
                "attributes": {
                    "locale": ["en"]
                }
            })
        except Exception as e:
            return self.keycloak_admin.get_user_id(data['email'])

    def set_user_password(self, user_id, password, temporary=True):
        return self.keycloak_admin.set_user_password(user_id, password, temporary)


class KeyCloakRootConnection(KeycloakHandler):
    def __init__(self):
        super().__init__(settings)
        super().connect(settings.KEYCLOAK_ADMIN_USERNAME, settings.KEYCLOAK_ADMIN_PASSWORD)
