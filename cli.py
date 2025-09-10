import argparse

from blockchain_interface.user import BlockchainUser


class AccessControlCLI:
    def __init__(self):
        pass

    def run(self):
        pass

    def handle(self, command):
        pass


if __name__ == '__main__':
    # Construct the argument parser
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-cc", "--create_account", required=False, help="Create a new account")
    args = vars(ap.parse_args())

    if args.get("create_account") == 'create_account':
        # Example usage
        blockchain_user = BlockchainUser('http://localhost:8555')
        address, private_key = blockchain_user.create_account()
        print(f"Address: {address}")
        print(f"Private Key: {private_key}")

        print(f"New User Balance: {blockchain_user.get_balance()}")