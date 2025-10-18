import datetime

from .SmartContract import SmartContract


class PolicyInformationPoint(SmartContract):
    def __init__(self, evm_interface, contract_address: str, contract_address_path: str):
        super().__init__(evm_interface, contract_address, contract_address_path)

    def add_group_to_user(self, user: str, group: str):
        """
        Add a group to a user.
        :param user: str - the address of the user
        :param group: str - the name of the group
        :return: transaction hash
        """
        return self.call_write_function("addGroupToUser", user, group)

    def get_user_groups(self, user: str):
        """
        Get the groups of a user.
        :param user: str - the address of the user
        :return: list of groups
        """

        user_hex = self.evm_interface.web3.to_checksum_address(user)

        return self.call_read_function("getUserGroups", user_hex)

    def remove_group_from_user(self, user: str, group: str):
        """
        Remove a group from a user.
        :param user: str - the address of the user
        :param group: str - the name of the group
        :return: transaction hash
        """
        return self.call_write_function("removeGroupFromUser", user, group)

    def set_user_role_attribute(self, user: str, role: str):
        """
        Set the role attribute of a user.
        :param user: str - the address of the user
        :param role: str - the role to set
        :return: transaction hash
        """

        user_hex = self.evm_interface.web3.to_checksum_address(user)

        return self.call_write_function("setUserRoleAttribute", user_hex, role)

    def get_user_role_attribute(self, user: str):
        """
        Get the role attribute of a user.
        :param user: str - the address of the user
        :return: role
        """

        user_hex = self.evm_interface.web3.to_checksum_address(user)

        return self.call_read_function("getUserRoleAttribute", user_hex)

    def add_resource(self, uri: str, contentHash: str):
        """
        Add a resource.
        :param uri: str - the URI of the resource
        :param contentHash: str - the content hash of the resource
        :return: transaction hash
        """
        return self.call_write_function("addResource", uri, contentHash)

    def update_resource_content_hash(self, uri: str, contentHash: str):
        """
        Update the content hash of a resource.
        :param uri: str - the URI of the resource
        :param contentHash: str - the new content hash of the resource
        :return: transaction hash
        """
        return self.call_write_function("updateResourceContentHash", uri, contentHash)

    def get_resource_attributes(self, uri: str) -> dict:
        """
        Get the attributes of a resource.
        :param uri: str - the URI of the resource
        :return: dict of attributes
        """

        raw_attributes = self.call_read_function("getResourceAttributes", uri)
        # IN: check PIP.sol for the order of attributes
        attributes = {
            "owner": raw_attributes[0],
            "uri": raw_attributes[1],
            "contentHash": raw_attributes[2],
            "createdAt": datetime.datetime.fromtimestamp(raw_attributes[3]).isoformat(),
            "updatedAt": datetime.datetime.fromtimestamp(raw_attributes[4]).isoformat()
        }

        # Convert timestamps to ISO 8601 format
        return attributes


    def grant_on_behalf_of_token(self, organisation: str):
        """
        Grant on behalf of token to an organisation.
        :param organisation: the wallet address of the organisation
        :return: None
        """

        organisation_hex = self.evm_interface.web3.to_checksum_address(organisation)

        return self.call_write_function("grantOnBehalfOfToken", organisation_hex)

    def organisation_has_access(self, user: str, organisation: str) -> bool:
        """
        Check if an organisation has access.
        :param user: the wallet address of the user to check
        :param organisation: the wallet address of the organisation to check
        :return: bool - True if the organisation has access, False otherwise
        """

        user_hex = self.evm_interface.web3.to_checksum_address(user)
        organisation_hex = self.evm_interface.web3.to_checksum_address(organisation)
        return self.call_read_function("organisationHasAccess", user_hex, organisation_hex)

    def revoke_access(self, user: str):
        """
        Revoke access for an organisation.
        :param user: the wallet address of the user to revoke access from
        :return: None
        """

        user_hex = self.evm_interface.web3.to_checksum_address(user)

        return self.call_write_function("revokeAccess", user_hex)