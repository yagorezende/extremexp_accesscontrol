import sys

from web3 import Web3, HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware

from blockchain_interface.interfaces.EVMInterface import EVMInterface


class HyperledgerBesu(EVMInterface):
    BLOCKCHAIN = "Hyperledger Besu"
    DEFAULT_GAS_LIMIT = 4100000  # Default gas limit for transactions

    def __init__(self, blockchain_address: str, gas_limit: int = DEFAULT_GAS_LIMIT):
        super().__init__(blockchain_address, self.BLOCKCHAIN)
        # Initialize any specific attributes or configurations for Hyperledger Besu
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.gas_limit = gas_limit



if __name__ == "__main__":
    # get arguments
    user_pk = sys.argv[1]

    blockchain = HyperledgerBesu('http://localhost:8555')
    blockchain.connect(user_pk)
    contract = blockchain.get_contract()
