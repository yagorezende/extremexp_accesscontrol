from typing import List

from .SmartContract import SmartContract


class PolicyAdministrationPoint(SmartContract):
    def __init__(self, evm_interface, contract_address: str, contract_address_path: str):
        super().__init__(evm_interface, contract_address, contract_address_path)

    def register_resource(self, uri: str, policy_address: str):
        """
        Register a resource with its associated policy contract address.
        :param uri: str - the URI of the resource
        :param policy_address: str - the address of the associated policy contract
        :return: transaction hash
        """

        address = self.evm_interface.web3.to_checksum_address(policy_address)

        return self.call_write_function("registerResource", uri, address)

    def get_resource_policy(self, uri: str):
        """
        Get the policy contract address associated with a resource.
        :param uri: str - the URI of the resource
        :return: policy contract address
        """
        return self.call_read_function("getResourcePolicy", uri)

    def remove_resource_policy(self, uri: str):
        """
        Remove the policy contract association for a resource.
        :param uri: str - the URI of the resource
        :return: transaction hash
        """
        return self.call_write_function("removeResourcePolicy", uri)


    def register_policy(self, policy_address):
        """
        Register a policy contract.
        :param policy_address: str - the address of the policy contract
        :return: transaction hash
        """

        address = self.evm_interface.web3.to_checksum_address(policy_address)

        return self.call_write_function("registerPolicy", address)

    def get_registered_policy(self) -> List[str]:
        """
        Get the list of resources associated with the sender policy list.
        :return: list of resource URIs
        """
        return self.call_read_function("getRegisteredPolicy")

    def unregister_policy(self, policy_address):
        """
        Unregister a policy contract.
        :param policy_address: str - the address of the policy contract
        :return: transaction hash
        """

        address = self.evm_interface.web3.to_checksum_address(policy_address)

        return self.call_write_function("unregisterPolicy", address)