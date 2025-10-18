from blockchain_interface.interfaces.ABACContracts.PAP import PolicyAdministrationPoint
from blockchain_interface.interfaces.ABACContracts.PDP import PolicyDecisionPoint
from blockchain_interface.interfaces.ABACContracts.PIP import PolicyInformationPoint
from blockchain_interface.interfaces.EVMInterface import EVMInterface
from blockchain_interface.user import BlockchainUser


def validate_on_behalf_of_permission(blockchain_interface: EVMInterface, pip_interface: PolicyInformationPoint, test_user: BlockchainUser) -> bool:
    """
    Validate the on behalf of permission functionality.
    :param blockchain_interface: evm interface instance
    :param pip_interface: ABAC PIP contract instance
    :param test_user: blockchain user instance
    :return: Bool - True if the test passed, False otherwise
    """

    # add on behalf of permission
    print(f"Adding main account onBehalfOf permission for test user")
    pip_interface.evm_interface = test_user.evm_interface

    tx_hash = pip_interface.grant_on_behalf_of_token(blockchain_interface.account_address)
    print(f"grant_on_behalf_of_token transaction hash: {tx_hash}")
    pip_interface.evm_interface = blockchain_interface

    # Check permission
    has_permission = pip_interface.organisation_has_access(test_user.account_address, blockchain_interface.account_address)
    print(f"Main account has onBehalfOf permission: {has_permission}")

    if not has_permission:
        print(f"❌ Main account has not onBehalfOf permission: {has_permission}")
        return False

    print("✅ Main account has onBehalfOf permission as expected.")

    # Revoke permission by deploying a new instance of the contract (simulating a reset)
    print(f"Revoking main account onBehalfOf permission by deploying a new instance of the contract")
    pip_interface.revoke_access(test_user.account_address)

    # Now check permission again
    has_permission = pip_interface.organisation_has_access(test_user.account_address, blockchain_interface.account_address)
    print(f"Main account don't have onBehalfOf permission after revocation: {has_permission}")
    if has_permission:
        print(f"❌ Main account still has onBehalfOf permission after revocation: {has_permission}")
        return False

    print("✅ Main account does not have onBehalfOf permission after revocation as expected.")

    print("🌟 Test passed: On behalf of permission functionality works as expected.")
    return True

def validate_user_attributes_management(pip_interface: PolicyInformationPoint, test_user: BlockchainUser) -> bool:
    """
    Validate the user attributes management functionality.
    :param pip_interface: PIP contract instance
    :param test_user: test user instance
    :return: Bool - True if the test passed, False otherwise
    """

    print("Testing user group management functionality.")
    # Get user groups
    print(f"User groups before adding any group:")
    groups = pip_interface.get_user_groups(test_user.account_address)
    print(f"\t- User groups: {groups}")

    # Remove all groups if any
    for group in groups:
        tx_hash = pip_interface.remove_group_from_user(test_user.account_address, group)
        print(f"\t- remove_group_from_user transaction hash: {tx_hash}")

    print(f"User groups after removing all groups:")
    groups = pip_interface.get_user_groups(test_user.account_address)
    print(f"\t- User groups: {groups}")
    # groups must be empty now
    if groups:
        print("❌ Failed to remove all groups from user.")
        return False

    print("✅ All groups removed from user as expected.")

    # Add group to user
    tx_hash = pip_interface.add_group_to_user(test_user.account_address, "admin")
    print(f"add_group_to_user transaction hash: {tx_hash}")
    # Get user groups
    groups = pip_interface.get_user_groups(test_user.account_address)
    print(f"User groups: {groups}")

    if len(groups) != 1 or groups[0] != "admin":
        print("❌ Failed to add group to user.")
        return False

    print("✅ Group added to user as expected.")

    # Remove group from user
    tx_hash = pip_interface.remove_group_from_user(test_user.account_address, "admin")
    print(f"remove_group_from_user transaction hash: {tx_hash}")
    # Get user groups
    groups = pip_interface.get_user_groups(test_user.account_address)
    print(f"User groups after removal: {groups}")

    if groups:
        print("❌ Failed to remove group from user.")
        return False

    print("✅ Group removed from user as expected.")

    print("🌟 Everything looks good so far. Now testing user role attribute management.")

    # Set user role attribute
    tx_hash = pip_interface.set_user_role_attribute(test_user.account_address, "manager")
    print(f"set_user_role_attribute transaction hash: {tx_hash}")
    # Get user role attribute
    role = pip_interface.get_user_role_attribute(test_user.account_address)
    print(f"User role attribute: {role}")
    if role != "manager":
        print("❌ Failed to set user role attribute.")
        return False

    print("✅ User role attribute set as expected.")

    print("🌟 Test passed: User attributes management functionality works as expected.")
    return True

def validate_resource_management(pip_interface: PolicyInformationPoint) -> bool:
    """
    Validate the resource management functionality.
    :param pip_interface: PIP contract instance
    :return: Bool - True if the test passed, False otherwise
    """
    # Add resource
    tx_hash = pip_interface.add_resource("resource_1", "hash_123")
    print(f"add_resource transaction hash: {tx_hash}")

    # Initial resource attributes
    attributes = pip_interface.get_resource_attributes("resource_1")
    print(f"Initial resource attributes: {attributes}")
    if attributes.get("uri") != "resource_1" or attributes.get("contentHash") != "hash_123":
        print("❌ Failed to add resource with correct attributes.")
        return False

    print("✅ Resource added with correct attributes as expected.")

    # Update resource content hash
    tx_hash = pip_interface.update_resource_content_hash("resource_1", "hash_456")
    print(f"update_resource_content_hash transaction hash: {tx_hash}")
    # Get resource attributes
    attributes = pip_interface.get_resource_attributes("resource_1")
    print(f"Resource attributes: {attributes}")
    if attributes.get("contentHash") != "hash_456":
        print("❌ Failed to update resource content hash.")
        return False

    print("✅ Resource content hash updated as expected.")

    print("🌟 Test passed: Resource attributes management functionality works as expected.")
    return True

def validate_resource_policy_management(pap_interface: PolicyAdministrationPoint, test_policy_address: str) -> bool:
    """
    Validate the resource policy management functionality.
    :param pap_interface: the SmartContract instance of the PAP contract
    :param test_policy_address: the address of a test policy contract to register
    :return: Bool - True if the test passed, False otherwise
    """

    # Register resource with policy
    tx_hash = pap_interface.register_resource("resource_1", test_policy_address)
    print(f"register_resource transaction hash: {tx_hash}")

    # Get resource policy
    policy_address = pap_interface.get_resource_policy("resource_1")
    print(f"Policy address for resource_1: {policy_address}")
    if policy_address != test_policy_address:
        print("❌ Failed to register resource with correct policy address.")
        return False

    print("✅ Resource registered with correct policy address as expected.")

    # Remove resource policy
    tx_hash = pap_interface.remove_resource_policy("resource_1")
    print(f"remove_resource_policy transaction hash: {tx_hash}")
    # Get resource policy
    policy_address = pap_interface.get_resource_policy("resource_1")
    print(f"Policy address for resource_1 after removal: {policy_address}")
    if policy_address is not None and policy_address != "0x0000000000000000000000000000000000000000":
        print("❌ Failed to remove resource policy.")
        return False

    print("✅ Resource policy removed as expected.")

    # Register policy with metadata
    tx_hash = pap_interface.register_policy(test_policy_address)
    print(f"register_policy transaction hash: {tx_hash}")

    # Get registered policies
    policies = pap_interface.get_registered_policy()
    print(f"Registered policies: {policies}")
    if test_policy_address not in policies:
        print("❌ Failed to register policy.")
        return False

    print("✅ Policy registered as expected.")

    # Unregister policy
    tx_hash = pap_interface.unregister_policy(test_policy_address)
    print(f"unregister_policy transaction hash: {tx_hash}")
    # Get registered policies
    policies = pap_interface.get_registered_policy()
    print(f"Registered policies after unregistration: {policies}")
    if test_policy_address in policies:
        print("❌ Failed to unregister policy.")
        return False
    print("✅ Policy unregistered as expected.")

    print("🌟 Test passed: Resource policy management functionality works as expected.")
    return True


def validate_policy_evaluation(pdp_interface: PolicyDecisionPoint, pip_interface: PolicyInformationPoint, test_user: BlockchainUser) -> bool:
    """
    Validate the policy evaluation functionality.
    :param pdp_interface: the SmartContract instance of the PDP contract
    :param pip_interface: the SmartContract instance of the PIP contract
    :param test_user: the BlockchainUser instance representing the user making the request
    :return: Bool - True if the test passed, False otherwise
    """

    # Add on behalf of permission for test user again
    keep_evm_interface = pip_interface.evm_interface
    pip_interface.evm_interface = test_user.evm_interface
    pip_interface.grant_on_behalf_of_token(pdp_interface.evm_interface.account_address)
    pip_interface.evm_interface = keep_evm_interface

    # Add user attributes
    pip_interface.add_group_to_user(test_user.account_address, "admin")
    pip_interface.set_user_role_attribute(test_user.account_address, "admin")

    # Save the resource hash
    pip_interface.add_resource("resource_1", "0x3e19fc037c6ced7075bbbb8e3163c92a")

    # Evaluate a valid access request
    access_granted = pdp_interface.evaluate_request(
        test_user.account_address,
        "johndoe@tudelft.nl",
        "127.0.0.1",
        "read:data",
        51999279,
        4377257,
        "resource_1"
    )

    print(f"Access granted for valid request: {access_granted}")
    if not access_granted:
        print("❌ Access not granted for valid request.")
        return False

    print("✅ Access granted for valid request as expected.")

    # Evaluate an invalid access request (should be denied)
    print("Testing user out of location scenario.")
    access_granted = pdp_interface.evaluate_request(
        test_user.account_address,
        "johndoe@tudelft.nl",
        "127.0.0.1",
        "read:data",
        51999279,
        5377257,
        "resource_1"
    )

    print(f"Access granted for invalid request: {access_granted}")
    if access_granted:
        print("❌ Access granted for invalid request.")
        return False

    print("✅ Access denied for invalid request as expected.")

    print(f"Testing user without required role scenario.")
    # Remove admin role attribute
    pip_interface.set_user_role_attribute(test_user.account_address, "user")
    access_granted = pdp_interface.evaluate_request(
        test_user.account_address,
        "johndoe@tudelft.nl",
        "127.0.0.1",
        "read:data",
        51999279,
        4377257,
        "resource_1"
    )

    print(f"Access granted for user without required role: {access_granted}")
    if access_granted:
        print("❌ Access granted for user without required role.")
        return False

    print("✅ Access denied for user without required role as expected.")

    print("🌟 Test passed: Policy evaluation functionality works as expected.")
    return True
