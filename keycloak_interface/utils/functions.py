from keycloak_interface.utils.handlers import KeycloakHandler, KeyCloakRootConnection


def get_keycloak_user(username):
    return KeyCloakRootConnection().get_keycloak_user_id(username)


def get_keycloak_user_roles(user_id):
    roles = [role['name'] for role in KeyCloakRootConnection().get_user_role(user_id)]
    return roles


def get_or_create_keycloak_user(username, email, name, password, role):
    keycloak_user_id = get_keycloak_user(username)
    keycloak_root_connection = KeyCloakRootConnection()
    created = False
    if keycloak_user_id is None:
        created = True
        keycloak_user_id = keycloak_root_connection.create_keycloak_user({"username": username, "email": email, "name": name})
        keycloak_root_connection.set_user_password(keycloak_user_id, password, False)
    # role_obj = keycloak_root_connection.get_realm_role(role)
    # keycloak_root_connection.set_user_role(keycloak_user_id, role_obj)
    keycloak_user = keycloak_root_connection.get_user(keycloak_user_id)
    return keycloak_user, created
