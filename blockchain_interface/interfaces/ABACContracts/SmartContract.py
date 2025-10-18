import os

import solcx

from blockchain_interface.interfaces.EVMInterface import EVMInterface

_solc_version = "0.8.18"
solcx.install_solc(_solc_version)
solcx.set_solc_version(_solc_version)

class SmartContract:
    def __init__(self, evm_interface: EVMInterface, contract_address: str, contract_file_path: str):
        self.evm_interface = evm_interface
        self.contract_address = self.evm_interface.web3.to_checksum_address(contract_address)
        self.contract_file_path = contract_file_path
        self.contract = None
        self.abi = None
        self.bytecode = None

    def load(self):
        """
        Load the smart contract from the blockchain.
        :return: SmartContract - self
        """

        # Code to load the smart contract using the EVM interface
        self._load_abi(self.contract_file_path)
        self._load_bytecode(self.contract_file_path)
        self.contract = self.evm_interface.get_contract(self.contract_address, self.abi, self.bytecode)
        return self

    def _load_abi(self, contract_path: str):
        """
        Load the ABI of the smart contract from a file.
        :param contract_path: the path to the contract file
        :return: None
        """

        try:
            with open(f'{contract_path.split(".")[0]}.abi', 'r') as abi_file:
                self.abi = abi_file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'Contract file {contract_path} not found')
        except Exception as e:
            raise Exception(f'Error loading contract ABI: {str(e)}')

    def _load_bytecode(self, contract_path: str):
        """
        Load the bytecode of the smart contract from a file.
        :param contract_path: the path to the contract file
        :return: None
        """

        try:
            with open(f'{contract_path.split(".")[0]}.bin', 'r') as bytecode_file:
                self.bytecode = bytecode_file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'Contract file {contract_path} not found')
        except Exception as e:
            raise Exception(f'Error loading contract bytecode: {str(e)}')

    def call_read_function(self, function_name, *args):
        # Code to call a function of the smart contract
        return self.evm_interface.call_contract_read_function(self.contract, function_name, *args)

    def call_write_function(self, function_name, *args):
        # Code to call a write function of the smart contract
        return self.evm_interface.call_contract_write_function(self.contract, function_name, *args)

    def call_dry_read_function(self, function_name, *args):
        data = self.contract.encode_abi("organisationHasAccess", args=args)
        raw = self.evm_interface.web3.eth.call({"to": self.contract_address, "data": data})

        # await the result
        receipt = self.evm_interface.web3.to_checksum_address(raw)

        print("Raw return:", raw.hex())