// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;


contract PolicyInformationPoint {
    // Duration: 24 hours for onBehalfOfToken permission
    uint256 private constant DURATION = 24 hours;

    struct UserAttributes {
        string[] groups; // or teams
        string role;
        mapping(address => uint256) onBehalfOfToken; // On behalf of token
    }

    struct ResourceAttributes {
        address owner;
        string uri;
        string contentHash;
        uint256 createdAt;
        uint256 updatedAt;
    }

    mapping (address => UserAttributes) private userAttributes;
    mapping (string => ResourceAttributes) private resourceAttributes;

    // Event when access is granted
    event AccessGranted(address organisation, uint256 expiresAt);

    // Function to grant access for 24 hours from now (Executed by the User)
    function grantOnBehalfOfToken(address organisation) public {
        UserAttributes storage attrs = userAttributes[msg.sender];
        uint256 expiresAt = block.timestamp + DURATION;
        attrs.onBehalfOfToken[organisation]  = expiresAt;
        emit AccessGranted(organisation, expiresAt);
    }

    // Function to check if access is still valid for the issuer
    function organisationHasAccess(address user, address organisation) public view returns (bool) {
        return userAttributes[user].onBehalfOfToken[organisation] != 0 && block.timestamp <= userAttributes[user].onBehalfOfToken[organisation];
    }

    // Optional: revoke access early
    function revokeAccess(address user) public {
        delete userAttributes[user].onBehalfOfToken[msg.sender];
    }

    /// @notice Adds a group to a user's attributes, creating a new entry if necessary.
    function addGroupToUser(address user, string memory group) public {
        UserAttributes storage attrs = userAttributes[user];

        // Check if group already exists (to avoid duplicates)
        for (uint i = 0; i < attrs.groups.length; i++) {
            if (keccak256(bytes(attrs.groups[i])) == keccak256(bytes(group))) {
                return; // Group already exists; do nothing
            }
        }

        // Otherwise, add the group
        attrs.groups.push(group);
    }

    // here is where we check if the organisation has access to the user attributes
    function getUserGroups(address user) public view returns (string[] memory){
        return userAttributes[user].groups;
    }

    /// @notice Removes the group from the user groups list
    function removeGroupFromUser(address user, string memory group) public {
        UserAttributes storage attrs = userAttributes[user];
        uint index = 0;
        for (index; index < attrs.groups.length; index++) {
            if (keccak256(bytes(attrs.groups[index])) == keccak256(bytes(group))) break ;// and break out of loop
        }
        
        require(keccak256(bytes(attrs.groups[index])) == keccak256(bytes(group)), "Group does not exist");
        attrs.groups[index] = attrs.groups[attrs.groups.length - 1]; // Replace with last
        attrs.groups.pop();
    }

    /// @notice Set the user role attribute
    function setUserRoleAttribute(address user, string memory role) public {
        UserAttributes storage attrs = userAttributes[user];
        attrs.role = role;
    }

    /// @notice Get the user role attribute
    function getUserRoleAttribute(address user) public view returns (string memory role) {
        if (bytes(userAttributes[user].role).length != 0) return userAttributes[user].role;
        return "default-role";
    }

    function addResource(string memory uri, string memory contentHash) public{
        ResourceAttributes storage attr = resourceAttributes[uri];
        attr.owner = msg.sender;
        attr.uri = uri;
        attr.contentHash = contentHash;
        attr.createdAt = block.timestamp;
        attr.updatedAt = block.timestamp;
    }

    function updateResourceContentHash(string memory uri, string memory contentHash) public{
        resourceAttributes[uri].contentHash = contentHash;
        resourceAttributes[uri].updatedAt = block.timestamp;
    }

    function getResourceAttributes(string memory uri) public view returns (ResourceAttributes memory){
        return resourceAttributes[uri];
    }
}