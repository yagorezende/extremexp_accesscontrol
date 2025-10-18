import argparse
import os
from pathlib import Path
from time import sleep

from dotenv import load_dotenv

from blockchain_interface.helpers.testing import validate_on_behalf_of_permission, validate_user_attributes_management, \
    validate_resource_management, validate_resource_policy_management, validate_policy_evaluation
from blockchain_interface.helpers.utils import load_json_from_file
from blockchain_interface.interfaces.ABACContracts.PAP import PolicyAdministrationPoint
from blockchain_interface.interfaces.ABACContracts.PDP import PolicyDecisionPoint
from blockchain_interface.interfaces.ABACContracts.PIP import PolicyInformationPoint
from blockchain_interface.interfaces.HyperledgerBesu import HyperledgerBesu
from blockchain_interface.user import BlockchainUser
from blockchain_interface.deployer import SolidityDeployer

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class AccessControlCLI:

    POLICY_ADMINISTRATION_POINT_CONTRACT = "PAP.sol"
    POLICY_INFORMATION_POINT_CONTRACT = "PIP.sol"
    POLICY_DECISION_POINT_CONTRACT = "PDP.sol"

    def __init__(self, blockchain_rpc_url: str, contracts_root_path: str, **kwargs):
        self.blockchain_rpc_url = blockchain_rpc_url
        self.blockchain_interface = HyperledgerBesu(self.blockchain_rpc_url, HyperledgerBesu.DEFAULT_GAS_LIMIT)
        self.deployer = SolidityDeployer(self.blockchain_rpc_url, SolidityDeployer.DEFAULT_GAS_LIMIT)
        self.contracts_root_path = contracts_root_path
        self.is_blockchain_wallet_loaded = False
        self.running_args = kwargs

    def handle(self, command):
        if command == "start":
            return self._start_blockchain_workspace()
        elif command == "create_account":
            return self.create_account()
        elif command == "test_abac":
            return self._test_abac()
        elif self.running_args.get('command') == "on-behalf-of":
            user_private_key = self.running_args.get('user_private_key')
            wallet_address = self.running_args.get('wallet_address')
            if not user_private_key:
                raise Exception("Please provide both 'user_private_key' for granting on behalf of permission.")
            return self._grant_on_behalf_of_permission(user_private_key)
        elif command == "deploy":
            contract_name = self.running_args.get('deploy')
            deploy_args = self.running_args.get('deploy_args_file', [])
            if not contract_name:
                raise Exception("Please provide the contract name to deploy using --deploy <contract_name>")

            if deploy_args:
                deploy_args = load_json_from_file(f"{self.contracts_root_path}/{deploy_args}")
                if not isinstance(deploy_args.get("args"), list):
                    raise Exception("Please provide the deploy arguments as a list in the JSON file.\n"
                                    "Example: {\"args\": [\"arg1\", \"arg2\"]}")
                deploy_args = deploy_args.get("args")
            return self._deploy_contract(contract_name, *deploy_args)
        return None

    def load_wallet(self, user_pk: str):
        """
        Load a user account to the deployer.
        :param user_pk: str - the private key of the user account
        """
        self.blockchain_interface.connect(user_pk)
        self.deployer.load_from_evm_interface(self.blockchain_interface)
        self.is_blockchain_wallet_loaded = True

        print(f"Wallet loaded for account: {self.blockchain_interface.account_address}")


    def create_account(self) -> tuple:
        """
        Create a new blockchain account.
        :return: tuple - (address, private_key)
        """
        # Create a new blockchain user instance
        blockchain_user = BlockchainUser(self.blockchain_rpc_url)
        address, private_key = blockchain_user.create_account()
        print(f"New account created.")
        print(f"Address: {address}")
        print(f"Private Key: {private_key}")



        blockchain_admin_user = BlockchainUser(self.blockchain_rpc_url).load_from_evm_interface(self.blockchain_interface)
        print(f"Deployer Address: {blockchain_admin_user.account_address}")
        print(f"Deployer Balance: {blockchain_admin_user.get_balance()}")

        # Transfer some initial balance from the deployer account to the new account
        # blockchain_admin_user.transfer_to(address, 0.1)  # Transfer 1 / 10k Ether

        print(f"New User Balance: {blockchain_user.get_balance()}")
        return address, f"0x{private_key}"

    def _start_blockchain_workspace(self) -> dict:
        """
        Start the blockchain workspace, including deploying necessary smart contracts.
        :return: dictionary with contract addresses
        """

        if not self.is_blockchain_wallet_loaded:
            raise Exception("Blockchain wallet not loaded. Please load a wallet before starting the workspace.")

        response = dict()
        response['PIPAddress'] = self._deploy_contract(self.POLICY_INFORMATION_POINT_CONTRACT)
        response['PAPAddress'] = self._deploy_contract(self.POLICY_ADMINISTRATION_POINT_CONTRACT)

        pdp_input_data = (response['PAPAddress'], response['PIPAddress'])
        response['PDPAddress'] = self._deploy_contract(self.POLICY_DECISION_POINT_CONTRACT, *pdp_input_data)

        self._display_start_blockchain_output(response)
        return response

    def _deploy_contract(self, contract_name: str, *input_data) -> str:
        """
        Deploy a smart contract to the blockchain.
        :param contract_name: Name of the contract file
        :param input_data: Input data for the contract constructor
        :return: Address of the deployed contract
        """
        # load file content
        contract_path = f"{self.contracts_root_path}/{contract_name}"
        compiled_contract = self.deployer.compile_contract(contract_path, dump_compiled=True)
        contract_address = self.deployer.deploy_contract(contract_path, *input_data)
        return contract_address

    def _display_start_blockchain_output(self, output: dict):
        """
        Display the output of the start blockchain workspace command.
        :param output: dict - the output of the start blockchain workspace command
        """
        print("Blockchain workspace started successfully.")
        print("Deployed contract addresses:")
        for contract_name, contract_address in output.items():
            print(f"{contract_name}: {contract_address}")

    def _test_abac(self):
        """
        Test the ABAC system by interacting with the deployed contracts.
        """
        # Loading user for testing
        test_user_pk = self.running_args.get('environ').get('TEST_USER_PRIVATE_KEY')
        if not test_user_pk:
            raise Exception("TEST_USER_PRIVATE_KEY environment variable not set.")

        # create test user connection
        test_user_blockchain_interface = HyperledgerBesu(self.blockchain_rpc_url, HyperledgerBesu.DEFAULT_GAS_LIMIT)
        test_user_blockchain_interface.connect(test_user_pk)
        test_user = BlockchainUser(self.blockchain_rpc_url).load_from_evm_interface(test_user_blockchain_interface)
        test_user.load_account(test_user_pk)

        print(f"Test User Address: {test_user.account_address}")
        print(f"Test User Balance: {test_user.get_balance()}")
        print("Connected:", self.blockchain_interface.web3.is_connected())
        print("Network ID:", self.blockchain_interface.web3.eth.chain_id)

        print("\n\n ########## VALIDATE PIP ########## \n\n")

        # Testing PIP
        pip_address = self.running_args.get('environ').get('POLICY_INFORMATION_POINT_ADDRESS')
        pip_file_path = f"{self.contracts_root_path}/{self.POLICY_INFORMATION_POINT_CONTRACT}"
        pip_interface = PolicyInformationPoint(self.blockchain_interface, pip_address, pip_file_path).load()

        print("Contract address:", pip_interface.contract_address)
        print("Code at contract:", self.blockchain_interface.web3.eth.get_code(pip_interface.contract_address).hex())

        if not validate_on_behalf_of_permission(self.blockchain_interface, pip_interface, test_user):
            raise Exception("On behalf of permission test failed.")

        # Add on behalf of permission for test user again
        pip_interface.evm_interface = test_user.evm_interface
        pip_interface.grant_on_behalf_of_token(self.blockchain_interface.account_address)
        pip_interface.evm_interface = self.blockchain_interface

        if not validate_user_attributes_management(pip_interface, test_user):
            raise Exception("User attributes management test failed.")

        if not validate_resource_management(pip_interface):
            raise Exception("Resource management test failed.")

        print("\n\n ########## VALIDATE PAP ########## \n\n")

        # Testing PAP
        pap_address = self.running_args.get('environ').get('POLICY_ADMINISTRATION_POINT_ADDRESS')
        sample_policy_address = self.running_args.get('environ').get('SAMPLE_POLICY_ADDRESS')
        pap_file_path = f"{self.contracts_root_path}/{self.POLICY_ADMINISTRATION_POINT_CONTRACT}"
        pap_interface = PolicyAdministrationPoint(self.blockchain_interface, pap_address, pap_file_path).load()

        print("Contract address:", pap_interface.contract_address)
        print("Code at contract:", self.blockchain_interface.web3.eth.get_code(pap_interface.contract_address).hex())

        if not validate_resource_policy_management(pap_interface, sample_policy_address):
            raise Exception("Resource policy management test failed.")

        print("\n\n ########## VALIDATE PDP ########## \n\n")
        # Testing PDP
        pdp_address = self.running_args.get('environ').get('POLICY_DECISION_POINT_ADDRESS')
        pdp_file_path = f"{self.contracts_root_path}/{self.POLICY_DECISION_POINT_CONTRACT}"
        pdp_interface = PolicyDecisionPoint(self.blockchain_interface, pdp_address, pdp_file_path).load()

        # Prepare PDP by registering the sample policy
        pap_interface.register_resource("resource_1", sample_policy_address)

        if not validate_policy_evaluation(pdp_interface, pip_interface, test_user):
            raise Exception("Policy evaluation test failed.")

        return "SUCCESS"

    def _grant_on_behalf_of_permission(self, user_private_key: str):
        """
        Grant on behalf of permission to a wallet address.
        :param user_private_key: str - the private key of the user account
        :param to_grant_wallet_address: str - the wallet address to grant permission to
        """
        # create user connection
        user_blockchain_interface = HyperledgerBesu(self.blockchain_rpc_url, HyperledgerBesu.DEFAULT_GAS_LIMIT)
        user_blockchain_interface.connect(user_private_key)

        print("Connected:", self.blockchain_interface.web3.is_connected())
        print("Network ID:", self.blockchain_interface.web3.eth.chain_id)

        # Loading PIP
        pip_address = self.running_args.get('environ').get('POLICY_INFORMATION_POINT_ADDRESS')
        pip_file_path = f"{self.contracts_root_path}/{self.POLICY_INFORMATION_POINT_CONTRACT}"
        # Load pip from the user interface
        pip_interface = PolicyInformationPoint(user_blockchain_interface, pip_address, pip_file_path).load()

        print("Contract address:", pip_interface.contract_address)
        print("Code at contract:", self.blockchain_interface.web3.eth.get_code(pip_interface.contract_address).hex())

        # Grant on behalf of permission
        pip_interface.grant_on_behalf_of_token(self.blockchain_interface.account_address)
        # Return to organisation account to check the grant permission
        pip_interface.evm_interface = self.blockchain_interface

        print(f"Granted on behalf of permission to {self.blockchain_interface.account_address}.")

        # validating permission
        has_permission = pip_interface.organisation_has_access(user_blockchain_interface.account_address, self.blockchain_interface.account_address)
        print(f"Organisation account has onBehalfOf permission: {has_permission}")

        if not has_permission:
            print(f"❌ Organisation account has not onBehalfOf permission: {has_permission}")
            print("❌ FAILURE")
            return False

        print("✅ Organisation account has onBehalfOf permission as expected.")

        return "🌟 SUCCESS"




if __name__ == '__main__':
    # Construct the argument parser
    ap = argparse.ArgumentParser()
    subparsers = ap.add_subparsers(dest="command")

    # Add the arguments to the parser
    ap.add_argument("-cc", "--create_account", nargs="?", const=True, required=False, help="Create a new account")
    ap.add_argument("-s", "--start", nargs="?", const=True, required=False, help="Start workspace and deploy contracts")
    ap.add_argument("-d", "--deploy", nargs="?", const=True, required=False, help="Deploy .sol contract and return the address")
    ap.add_argument("--deploy-args-file", nargs="?", required=False, help="Deploy .sol contract and return the address")
    ap.add_argument("-t", "--test_abac", nargs="?", const=True, required=False, help="Run ABAC test suite")

    # ap.add_argument("-o", "--on-behalf-of", nargs=2, metavar=('USER_PRIVATE_KEY', 'WALLET_ADDRESS'), required=False,
    #                 help="Grant on behalf of permission to a wallet address")

    on_behalf_of_parser = subparsers.add_parser('on-behalf-of', help="Grant on behalf of permission to a wallet address")
    on_behalf_of_parser.add_argument('-upk', '--user_private_key', help="The private key of the user account")

    args = vars(ap.parse_args())
    print(args)

    # load environment variables
    blockchain_rpc_url = os.environ.get("BLOCKCHAIN_RPC_URL")
    contracts_root_path = os.environ.get("CONTRACTS_ROOT_PATH", BASE_DIR / "contracts")

    args.update({"environ": os.environ})

    app_cli = AccessControlCLI(blockchain_rpc_url, contracts_root_path, **args)
    app_cli.load_wallet(os.environ.get("BLOCKCHAIN_PRIVATE_KEY"))

    for arg, value in args.items():
        if value and arg not in ['environ', 'user_private_key', 'wallet_address', 'deploy_args_file', 'contract_args']:
            print(f"Argument {arg} is set to {value}")
            result = app_cli.handle(arg)
            print(f"Result: {result}")


    # if args.get("create_account") == 'create_account':
    #     # Example usage
    #     blockchain_user = BlockchainUser('http://localhost:8555')
    #     address, private_key = blockchain_user.create_account()
    #     print(f"Address: {address}")
    #     print(f"Private Key: {private_key}")
    #
    #     print(f"New User Balance: {blockchain_user.get_balance()}")