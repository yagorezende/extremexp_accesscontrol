from typing import Type

from web3.contract import Contract


class EVMInterface:
    def __init__(self, blockchain_type):
        self.blockchain_type = blockchain_type
        self.web3 = None
        self.gas_limit = None
        self.account_private_key = None

    def connect(self, account_pk: str):
        """
        Loads an account to the Web3 instance.
        :param account_pk: str - the private key of the account
        """
        self.web3.eth.default_account = self.web3.eth.account.from_key(account_pk)
        self.account_private_key = account_pk

    def disconnect(self):
        """
        Disconnects the account from the Web3 instance.
        This is a placeholder as Hyperledger Besu does not require explicit disconnection.
        """
        self.web3.eth.default_account = None
        self.account_private_key = None

    def get_balance(self, address):
        raise NotImplementedError("This method should be overridden by subclasses")

    def send_transaction(self, from_address, to_address, amount):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_contract(self, contract_address) -> Type[Contract]:
        """
        Returns a contract instance for the given contract address.
        :param contract_address: String - the address of the smart contract
        :return: Contract - a web3 Contract instance
        """
        return self.web3.eth.contract(address=self.web3.toChecksumAddress(contract_address))

    def deploy_contract(self, contract_data):
        raise NotImplementedError("This method should be overridden by subclasses")

    def call_contract_read_function(self, contract_address, function_name, *args):
        """
        Calls a function of a smart contract.
        :param contract_address: String - the address of the smart contract
        :param function_name: String - the name of the function to call
        :param args: List - the arguments to pass to the function
        :return: Any - the result of the function call
        """
        contract = self.get_contract(contract_address)
        function = contract.functions[function_name](*args)
        return function.call()



    def listen_to_events(self, contract_address, event_name, callback):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_transaction_receipt(self, transaction_hash):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_block(self, block_number):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_latest_block(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_transaction(self, transaction_hash):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_network_info(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_account_info(self, address):
        raise NotImplementedError("This method should be overridden by subclasses")

