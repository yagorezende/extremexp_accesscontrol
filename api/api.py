import logging

from flask_restx import Namespace, Resource
from models.models import PolicyDAO
from middleware import decorators

api: Namespace = Namespace('Translator', description='ExtremeXP Translator Endpoints')

policy_model = api.model('Policy', PolicyDAO.structure)

DAO = PolicyDAO()

@api.route("/")
# @oidc.accept_token(require_token=True, scopes_required=['openid'])
class TranslatorEndpointsList(Resource):
    @api.doc('list_policies')
    @api.marshal_list_with(policy_model)
    @decorators.require_token(require_token=True, scopes_required=['openid'])
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