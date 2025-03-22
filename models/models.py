from flask_restx import fields


class PolicyDAO(object):
    structure = {
        'id': fields.Integer(readonly=True, description='The policy unique identifier'),
        'address': fields.String(readonly=True, description='The policy blockchain address'),
        'policy': fields.String(required=True, description='The policy JSON content'),
    }

    def __init__(self):
        self.counter = 0
        self.policies = []

    def get(self, id: int):
        for policy in self.policies:
            if policy['id'] == id:
                return policy
        return None

    def create(self, data):
        policy = data
        policy['id'] = self.counter = self.counter + 1
        # temporary line to simulate blockchain address
        policy['address'] = "0x" + policy['policy'].encode('utf-8').hex()
        self.policies.append(policy)
        return policy

    def update(self, id: int, data):
        policy = self.get(id)
        policy.update(data)
        return policy

    def delete(self, id: int):
        policy = self.get(id)
        self.policies.remove(policy)


class PersonDAO(object):
    structure = {
        'sub': fields.Integer(readonly=True, description='The user Keycloak UUID'),
        'email_verified': fields.Boolean(readonly=True, description='Is email verified by Keycloak'),
        'name': fields.String(readonly=True, description='The user full name'),
        'preferred_username': fields.String(readonly=True, description='The username used to login'),
        'given_name': fields.String(readonly=True, description='The user given name'),
        'family_name': fields.String(readonly=True, description='The user family name'),
        'email': fields.String(required=True, description='The email registered in Keycloak'),
    }

    def get(self, access_token: str):
        return {
            'sub': 1234567890,
            'email_verified': True,
            'name': 'John Doe',
            'preferred_username': 'jdoe',
            'given_name': 'John',
            'family_name': 'Doe',
            'email': 'johndoe@'
        }

    def create(self, data):
        return data

    def update(self, access_token: str, data):
        """
        Only user given name, family name and email can be updated.
        :param access_token:
        :param data:
        :return: updated user data
        """


    def delete(self, access_token: str):
        """
        Delete user from the database is not allowed.
        :param access_token:
        :return:
        """
        return None

    def validate_data(self, user_data: dict):
        return set(user_data.keys()) == set(self.structure.keys())
