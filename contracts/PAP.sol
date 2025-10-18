// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract PolicyAdministrationPoint{
    // string: URI => address Policy
    mapping(string => address) public resourcePolicies;
    // owner address => policy address
    mapping(address => address[]) public registeredPolicies;

    function registerResource(string memory uri, address policyAddress) public{
        resourcePolicies[uri] = policyAddress;
    }

    function getResourcePolicy(string memory uri) public view returns (address) {
        return resourcePolicies[uri];
    }

    function removeResourcePolicy(string memory uri) public {
        delete resourcePolicies[uri];
    }

    function registerPolicy(address policyAddress) public {
        // Check if already registered
        address[] storage policies = registeredPolicies[msg.sender];
        for (uint i = 0; i < policies.length; i++) {
            if (policies[i] == policyAddress) return; // Already registered
        }
        policies.push(policyAddress);
    }

    function getRegisteredPolicy() public view returns (address[] memory){
        return registeredPolicies[msg.sender];
    }

    function unregisterPolicy(address policyAddress) public {
        address[] storage policies = registeredPolicies[msg.sender];
        for (uint i = 0; i < policies.length; i++) {
            if (policies[i] == policyAddress) {
                policies[i] = policies[policies.length - 1]; // Move last to current
                policies.pop(); // Remove last
                return;
            }
        }
    }
}