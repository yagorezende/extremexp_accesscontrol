from .SmartContract import SmartContract


class PolicyDecisionPoint(SmartContract):
    def __init__(self, evm_interface, contract_address: str, contract_address_path: str):
        super().__init__(evm_interface, contract_address, contract_address_path)

    def evaluate_request(self, user: str, user_email: str, user_ip_address: str, user_request_scope: str, user_lat: int, user_long: int, resource_uri: str) -> bool:
        """
        Evaluate an access request against the policy.
        :param user: str - the address of the user making the request
        :param user_email: str - the email of the user making the request
        :param user_ip_address: str - the IP address of the user making the request
        :param user_request_scope: str - the scope of the user's request
        :param user_lat: int - the latitude of the user's location
        :param user_long: int - the longitude of the user's location
        :param resource_uri: str - the URI of the resource being accessed
        :return: bool - True if access is granted, False otherwise
        """

        user_address = self.evm_interface.web3.to_checksum_address(user)

        return self.call_read_function("evaluateRequest", user_address, user_email, user_ip_address, user_request_scope, user_lat, user_long, resource_uri)


    def set_pip(self, pip_address: str):
        """
        Set the address of the Policy Information Point (PIP) contract.
        :param pip_address: str - the address of the PIP contract
        :return: transaction hash
        """

        address = self.evm_interface.web3.to_checksum_address(pip_address)

        return self.call_write_function("setPIP", address)

    def get_pip(self) -> str:
        """
        Get the address of the Policy Information Point (PIP) contract.
        :return: str - the address of the PIP contract
        """
        return self.call_read_function("getPIP")

    def set_pap(self, pap_address: str):
        """
        Set the address of the Policy Administration Point (PAP) contract.
        :param pap_address: str - the address of the PAP contract
        :return: transaction hash
        """

        address = self.evm_interface.web3.to_checksum_address(pap_address)

        return self.call_write_function("setPAP", address)

    def get_pap(self) -> str:
        """
        Get the address of the Policy Administration Point (PAP) contract.
        :return: str - the address of the PAP contract
        """
        return self.call_read_function("getPAP")