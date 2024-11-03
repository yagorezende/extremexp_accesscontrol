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
