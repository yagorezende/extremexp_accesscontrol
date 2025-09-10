import json
import logging
from typing import Tuple

import requests
from requests import HTTPError

from keycloak_interface.utils.functions import get_or_create_keycloak_user

LOGGER = logging.getLogger(__name__)


class KeycloakInterface:
    RESOURCES_CACHE = []

    def __init__(self, server_url, realm_name, client_id, client_secret_key=None):
        """Create Keycloak Instance.

        Args:
            server_url (str):
                URI auth server
            realm_name (str):
                Realm name
            client_id (str):
                Client ID
            client_secret_key (str, optional):
                Client secret credencials.
                For each 'access type':
                    - bearer-only -> Optional
                    - public -> Mandatory
                    - confidencial -> Mandatory

        Returns:
            object: Keycloak object
        """

        self.server_url = server_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret_key = client_secret_key

        # Keycloak useful Urls
        self.well_known_endpoint = (
                self.server_url
                + "/realms/"
                + self.realm_name
                + "/.well-known/openid-configuration"
        )
        self.token_endpoint = (
                self.server_url
                + "/realms/"
                + self.realm_name
                + "/protocol/openid-connect/token"
        )
        self.token_introspection_endpoint = (
                self.server_url
                + "/realms/"
                + self.realm_name
                + "/protocol/openid-connect/token/introspect"
        )
        self.userinfo_endpoint = (
                self.server_url
                + "/realms/"
                + self.realm_name
                + "/protocol/openid-connect/userinfo"
        )

    @staticmethod
    def _send_request(method, url, **kwargs) -> Tuple[dict, int]:
        """Send request by method and url.
         Raises HTTPError exceptions if status >= 400

         Returns:
             json: Response body
         """
        response = requests.request(method, url, **kwargs)
        return response.json(), response.status_code

    def authenticate(self, username, password, raise_exception=False) -> Tuple[dict, int]:
        """
        Authenticate user on Keycloak

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            dict: The response of the authentication.
        """
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret_key,
            "grant_type": "password",
            "scope": "openid profile email",
            "username": username,
            "password": password,
        }

        logging.error(f"{payload}")

        headers = {"content-type": "application/x-www-form-urlencoded"}

        return self._send_request('POST', self.token_endpoint, data=payload, headers=headers)

    def well_known(self, raise_exception=True):
        """Lists endpoints and other configuration options
        relevant to the OpenID Connect implementation in Keycloak.

        Args:
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            [type]: [list of keycloak endpoints]
        """
        try:
            response, status_code = self._send_request("GET", self.well_known_endpoint)
        except HTTPError as ex:
            LOGGER.error(
                "Error obtaining list of endpoints from endpoint: "
                f"{self.well_known_endpoint}, response error {ex}"
            )
            if raise_exception:
                raise
            return {}
        return response

    def get_jwt_from_token(self, token):
        introspect_token = self.introspect(token)
        return {
            "access_token": token,
            "expires_in": 36000,
            "refresh_expires_in": 36000,
            "refresh_token": token,
            "token_type": "Bearer",
            "id_token": token,
            "not-before-policy": 0,
            "session_state": introspect_token.get("session_state", ""),
            "scope": introspect_token.get("scope", ""),
        }

    def introspect(self, token, token_type_hint=None, raise_exception=True):
        """
        Introspection Request token
        Implementation: https://tools.ietf.org/html/rfc7662#section-2.1

        Args:
            token (string):
                REQUIRED. The string value of the token.  For access tokens, this
                is the "access_token" value returned from the token endpoint
                defined in OAuth 2.0 [RFC6749], Section 5.1.  For refresh tokens,
                this is the "refresh_token" value returned from the token endpoint
                as defined in OAuth 2.0 [RFC6749], Section 5.1.  Other token types
                are outside the scope of this specification.
            token_type_hint ([string], optional):
                OPTIONAL.  A hint about the type of the token submitted for
                introspection.  The protected resource MAY pass this parameter to
                help the authorization server optimize the token lookup.  If the
                server is unable to locate the token using the given hint, it MUST
                extend its search across all of its supported token types.  An
                authorization server MAY ignore this parameter, particularly if it
                is able to detect the token type automatically.  Values for this
                field are defined in the "OAuth Token Type Hints" registry defined
                in OAuth Token Revocation [RFC7009].
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            json: The introspect token
        """
        payload = {
            "token": token,
            "client_id": self.client_id,
            "client_secret": self.client_secret_key,
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "authorization": "Bearer " + token,
        }
        try:
            response, status_code = self._send_request(
                "POST", self.token_introspection_endpoint, data=payload, headers=headers)
        except HTTPError as ex:
            LOGGER.error(
                "Error obtaining introspect token from endpoint: "
                f"{self.token_introspection_endpoint}, data {payload}, "
                f" headers {headers}, response error {ex}"
            )
            if raise_exception:
                raise
            return {}
        return response

    def is_token_active(self, token, raise_exception=True):
        """Verify if introspect token is active.

        Args:
            token (str): The string value of the token.
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            boolean: Token valid (True) or invalid (False)
        """

        introspect_token = self.introspect(token, raise_exception)
        # print(f"Introspect token: {introspect_token}")
        is_active = introspect_token.get("active", None)
        # print(f"Token is active: {is_active}")
        return is_active is not None

    def validate_request_token(self, token, assert_group=None, raise_exception=True) -> bool:
        """
        Validate request token

        Args:
            token (str): The string value of the token.
            assert_group (str, optional): The group to assert for the token.
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            bool: True if the token is valid and belongs to the specified group, False otherwise.
        """
        introspect_token = self.introspect(token, raise_exception)
        if not introspect_token.get("active", False):
            return False

        if assert_group:
            groups = introspect_token.get("groups", [])
            return assert_group in groups
        return True


    def roles_from_token(self, token, raise_exception=True):
        """
        Get roles from token

        Args:
            token (string): The string value of the token.
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            list: List of roles.
        """
        token_decoded = self.introspect(token, raise_exception)

        realm_access = token_decoded.get("realm_access", None)
        resource_access = token_decoded.get("resource_access", None)
        client_access = (
            resource_access.get(self.client_id, None)
            if resource_access is not None
            else None
        )

        client_roles = (
            client_access.get("roles", None) if client_access is not None else None
        )
        realm_roles = (
            realm_access.get("roles", None) if realm_access is not None else None
        )

        if client_roles is None:
            return realm_roles
        if realm_roles is None:
            return client_roles
        return client_roles + realm_roles

    def userinfo(self, token, raise_exception=True):
        """Get userinfo (sub attribute from JWT) from authenticated token

        Args:
            token (str): The string value of the token.
            raise_exception: Raise exception if the request ended with a status >= 400.

        Returns:
            json: user info data
        """
        headers = {"authorization": "Bearer " + token}
        try:
            response, status_code = self._send_request(
                "GET", self.userinfo_endpoint, headers=headers)
        except HTTPError as ex:
            LOGGER.error(
                "Error obtaining userinfo token from endpoint: "
                f"{self.userinfo_endpoint}, headers {headers}, "
                f"response error {ex}"
            )
            if raise_exception:
                raise
            return {}
        return response, status_code

    def create_user(self, username: str, password: str, email: str, name: str):
        try:
            user, created = get_or_create_keycloak_user(username, email, name, password, None)
            if created:
                return user, 201
            return user, 200
        except Exception as e:
            return {"error": "Internal Server Error",
                    "error_description": "Unable to create user. Please check the date and try again."}, 500
