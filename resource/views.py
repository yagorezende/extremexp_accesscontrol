from flask import request
from flask_restx import Namespace, Resource

from api import settings
from blockchain_interface.helpers.utils import transaction_to_dict
from blockchain_interface.interfaces.ABACContracts.PAP import PolicyAdministrationPoint
from blockchain_interface.interfaces.ABACContracts.PDP import PolicyDecisionPoint
from blockchain_interface.interfaces.ABACContracts.PIP import PolicyInformationPoint
from blockchain_interface.interfaces.HyperledgerBesu import HyperledgerBesu
from keycloak_interface.keycloakInterface import KeycloakInterface
from keycloak_interface.utils.functions import extract_header_token

api: Namespace = Namespace('Resources', description='ExtremeXP Resource Management Endpoints')

keycloak_interface = KeycloakInterface(
    server_url=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_SERVER_URL'),
    realm_name=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_REALM'),
    client_id=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_ID'),
    client_secret_key=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_SECRET_KEY')
)

evm_interface_instance = HyperledgerBesu(settings.BLOCKCHAIN_CONFIG.get('BLOCKCHAIN_RPC_URL')).connect(
    settings.BLOCKCHAIN_CONFIG.get('BLOCKCHAIN_PRIVATE_KEY')
)

PIPSmartContract = PolicyInformationPoint(
    evm_interface_instance,
    settings.BLOCKCHAIN_CONFIG.get('POLICY_INFORMATION_POINT_ADDRESS'),
    f"{settings.BLOCKCHAIN_CONFIG.get('BLOCKCHAIN_CONTRACTS_ROOT_PATH')}/PIP.sol"
).load()

PAPSmartContract = PolicyAdministrationPoint(
    evm_interface_instance,
    settings.BLOCKCHAIN_CONFIG.get('POLICY_ADMINISTRATION_POINT_ADDRESS'),
    f"{settings.BLOCKCHAIN_CONFIG.get('BLOCKCHAIN_CONTRACTS_ROOT_PATH')}/PAP.sol"
).load()

PDPSmartContract = PolicyDecisionPoint(
    evm_interface_instance,
    settings.BLOCKCHAIN_CONFIG.get('POLICY_DECISION_POINT_ADDRESS'),
    f"{settings.BLOCKCHAIN_CONFIG.get('BLOCKCHAIN_CONTRACTS_ROOT_PATH')}/PDP.sol"
).load()

@api.route("/protect")
class ProtectResourceView(Resource):
    @api.doc('protect', params={
        'uri': 'Resource URI',
        'content_hash': 'Resource Content Hash (can be 0x0 if not applicable)',
        'policy_address': 'Policy address hash in the blockchain'
    })
    def post(self):
        token = extract_header_token(request)
        if not keycloak_interface.validate_request_token(token):
            return {'error': 'Invalid or missing token'}, 401
        try:
            payload = request.json

            if not payload.get('uri') or not payload.get('content_hash') or not payload.get('policy_address'):
                return {'error': 'Missing required fields'}, 400

            response = {}

            # add resource to PIP
            tx = PIPSmartContract.add_resource(
                payload.get('uri'),
                payload.get('content_hash'),
            )

            response['PIP_transaction'] = transaction_to_dict(tx)

            # register resource in PAP
            tx = PAPSmartContract.register_resource(
                payload.get('uri'),
                payload.get('policy_address')
            )

            response['PAP_transaction'] = transaction_to_dict(tx)

            return response, 201
        except Exception as e:
            return {'error': str(e)}, 401

    @api.doc('protect', params={
        'uri': 'Resource URI'
    }, methods=['GET'])
    def get(self, *args, **kwargs):
        token = extract_header_token(request)
        if not keycloak_interface.validate_request_token(token):
            return {'error': 'Invalid or missing token'}, 401
        try:
            payload = dict(request.args)

            if not payload.get('uri'):
                return {'error': 'Missing required fields'}, 400

            # get resource from PAP
            policy_address = PAPSmartContract.get_resource_policy(payload.get('uri'))
            response = {
                'policy_address': policy_address
            }

            return response, 200 if int(policy_address, 16) else 404
        except Exception as e:
            return {'error': str(e)}, 401

@api.route("/access")
class AccessResourceView(Resource):
    @api.doc('access', params={
        'uri': 'Resource URI',
        'origin_ip': 'Origin IP Address',
        'scope': 'Scope or Action to be performed',
    })
    def post(self):
        token = extract_header_token(request)
        if not keycloak_interface.validate_request_token(token):
            return {'error': 'Invalid or missing token'}, 401
        try:
            payload = request.json

            if not payload.get('uri') or not payload.get('origin_ip') or not payload.get('scope'):
                return {'error': 'Missing required fields'}, 400

            user_info, status_code = keycloak_interface.userinfo(token)
            if status_code != 200:
                return {'error': 'Invalid token'}, 401

            access_granted = PDPSmartContract.evaluate_request(
                user_info.get('user_wallet_address'),
                user_info.get('email'),
                payload.get('origin_ip'),
                payload.get('scope'),
                user_info.get('user_location_lat'),
                user_info.get('user_location_long'),
                payload.get('uri')
            )

            return {"grant": access_granted}, 200 if access_granted else 403
        except Exception as e:
            return {'error': str(e)}, 403