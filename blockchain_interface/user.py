import sys
from time import sleep

from web3 import Web3, HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware


class BlockchainUser:
    def __init__(self, blockchain_address: str, gas_limit: int = 4100000):
        self.web3 = Web3(HTTPProvider(blockchain_address))
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.gas_limit = gas_limit
        self.account_private_key = None
        self.account_address = None

    def load_account(self, account_pk: str):
        """
        Loads an account to the Web3 instance.
        :param account_pk: str - the private key of the account
        """
        self.web3.eth.default_account = self.web3.eth.account.from_key(account_pk)
        self.account_private_key = account_pk
        self.account_address = self.web3.eth.account.from_key(account_pk).address
        return self.account_address

    def create_account(self):
        """
        Creates a new account and returns the address and private key.
        :return: tuple - (address, private_key)
        """
        account = self.web3.eth.account.create()
        self.account_private_key = account._private_key.hex()
        self.account_address = account.address
        return self.account_address, self.account_private_key

    def get_balance(self):
        """
        Gets the balance of an account.
        :return: float - the balance in Ether
        """
        balance_wei = self.web3.eth.get_balance(self.account_address)
        return self.web3.from_wei(balance_wei, 'ether')

    def transfer_to(self, to_address: str, amount: float):
        """
        Transfers Ether from the current account to another address.
        :param to_address: str - the address to transfer to
        :param amount: float - the amount to transfer in Ether
        """
        if self.account_private_key is None:
            raise ValueError("Account private key not loaded.")

        nonce = self.web3.eth.get_transaction_count(self.account_address)
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': self.web3.to_wei(amount, 'ether'),
            'gas': self.gas_limit,
            'gasPrice': self.web3.eth.gas_price
        }

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash


if __name__ == '__main__':
    user_pk = sys.argv[1]

    # Example usage
    blockchain_user = BlockchainUser('http://localhost:8555')
    address, private_key = blockchain_user.create_account()
    print(f"Address: {address}")
    print(f"Private Key: {private_key}")

    default_user = BlockchainUser('http://localhost:8555')
    default_user.load_account(user_pk)
    print(f"Default User Address: {default_user.account_address}")
    transaction = default_user.transfer_to(address, 1)
    print(f"Transaction Hash: {transaction}")
    print("Waiting for transaction to be mined...")
    while True:
        sleep(1)
        tx_receipt = blockchain_user.web3.eth.get_transaction_receipt(transaction)
        if tx_receipt is not None:
            print(f"Transaction mined: {tx_receipt}")
            break

    print(f"New User Balance: {blockchain_user.get_balance()}")