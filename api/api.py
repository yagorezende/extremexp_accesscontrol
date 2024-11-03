import json
import logging

from flask_restx import Namespace, Resource

from models.models import PolicyDAO

api = Namespace('Translator', description='ExtremeXP Translator Endpoints')

policy_model = api.model('Policy', PolicyDAO.structure)

DAO = PolicyDAO()

@api.route("/")
class TranslatorEndpointsList(Resource):
    @api.doc('list_policies')
    @api.marshal_list_with(policy_model)
    def get(self):
        """
        List all policies
        """
        answer = DAO.policies
        logging.info(answer)
        return answer

    @api.doc('create_policy')
    @api.expect(policy_model)
    @api.marshal_with(policy_model, code=201)
    def post(self):
        """
        Create a new policy
        """
        data = api.payload
        answer = DAO.create(data)
        logging.info(answer)
        return answer, 201