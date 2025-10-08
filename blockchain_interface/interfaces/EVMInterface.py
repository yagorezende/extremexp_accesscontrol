from typing import Type

from web3 import Web3, HTTPProvider
from web3.contract import Contract


class EVMInterface:
    def __init__(self, blockchain_address: str, blockchain_type: str):
        self.web3 = Web3(HTTPProvider(blockchain_address))
        self.blockchain_type = blockchain_type
        self.gas_limit = None
        self.account_private_key = None
        self.account_address = None

    def connect(self, account_pk: str):
        """
        Loads an account to the Web3 instance.
        :param account_pk: str - the private key of the account
        :return: self - the EVMInterface instance
        """
        self.web3.eth.default_account = self.web3.eth.account.from_key(account_pk)
        self.account_private_key = account_pk
        self.account_address = self.web3.eth.account.from_key(account_pk).address
        return self

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

    def get_contract(self, contract_address, abi, bytecode) -> Type[Contract]:
        """
        Returns a contract instance for the given contract address.
        :param contract_address: String - the address of the smart contract
        :param abi: Dict - the ABI of the smart contract
        :param bytecode: String - the bytecode of the smart contract
        :return: Contract - a web3 Contract instance
        """
        return self.web3.eth.contract(address=contract_address, abi=abi)

    def deploy_contract(self, contract_data):
        raise NotImplementedError("This method should be overridden by subclasses")

    def call_contract_read_function(self, contract, function_name, *args):
        """
        Calls a function of a smart contract.
        :param contract: web3.Contract - the smart contract instance to call the function on
        :param function_name: String - the name of the function to call
        :param args: List - the arguments to pass to the function
        :return: Any - the result of the function call
        """

        params = {
            "from": self.account_address,
            "to": contract.functions[function_name].address
        }

        response = contract.functions[function_name](*args).call(params)
        return response

    def call_contract_write_function(self, contract, function_name, *args) -> dict:
        """
        Calls a write function of a smart contract.
        :param contract web3.Contract - the smart contract instance to call the function on
        :param function_name: String - the name of the function to call
        :param args: List - the arguments to pass to the function
        :return: receipt dict - the transaction receipt
        """
        function = contract.functions[function_name](*args)

        params = {
            "from": self.account_address,
            "gas": self.gas_limit,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account_address)
        }

        transaction = function.build_transaction(params)
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.account_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = dict(self.web3.eth.wait_for_transaction_receipt(tx_hash))
        tx_receipt['transactionHash'] = tx_hash

        # load the transaction details
        tx_details = self.web3.eth.get_transaction(tx_hash)
        tx_receipt['transactionDetails'] = dict(tx_details)
        return tx_receipt

    def call_contract_write_function_directly(self, contract, function_name, *args) -> dict:
        """
        Calls a write function of a smart contract directly without building the transaction.
        :param contract web3.Contract - the smart contract instance to call the function on
        :param function_name: String - the name of the function to call
        :param args: List - the arguments to pass to the function
        :return: receipt dict - the transaction receipt
        """
        tx_hash = contract.functions[function_name](*args).transact()
        return dict(self.web3.eth.wait_for_transaction_receipt(tx_hash))

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

