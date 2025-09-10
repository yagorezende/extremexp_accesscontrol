// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract PolicyAdministrationPoint{

    // string: URI => address Policy
    mapping(string => address) public resourcePolicies;

    function registerResource(string memory uri, address policyAddress) public{
        resourcePolicies[uri] = policyAddress;
    }

    function getResourcePolicy(string memory uri) public view returns (address) {
        return resourcePolicies[uri];
    }

    function removeResourcePolicy(string memory uri) public{
        delete resourcePolicies[uri];
    }
}