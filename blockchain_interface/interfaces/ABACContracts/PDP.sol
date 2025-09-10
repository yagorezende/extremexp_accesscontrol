// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "PAP.sol";
import "PIP.sol";
import "interfaces/AccessControlPolicy.sol";

contract PDP {
    PolicyAdministrationPoint private pap;
    PolicyInformationPoint private pip;

    constructor(address papAddress, address pipAddress) {
        pap = PolicyAdministrationPoint(papAddress);
        pip = PolicyInformationPoint(pipAddress);
    }

    function evaluateRequest(
        address user,
        string memory userIPAddress,
        string memory userRequestScope,
        int256 userLat, int256 userLong,    
        string memory resourceURI) public view returns (bool) {

        PolicyInformationPoint.ResourceAttributes memory resourceAttribute = pip.getResourceAttributes(resourceURI);

        // assemble context
        AccessControlPolicy.RequestContext memory reqContext = AccessControlPolicy.RequestContext(
            user,
            pip.getUserRoleAttribute(user),
            pip.getUserGroups(user),
            AccessControlPolicy.Location(userLat, userLong),
            userIPAddress,
            userRequestScope,
            resourceURI,
            resourceAttribute.contentHash
        );

        address policyAddress = pap.getResourcePolicy(resourceURI);
        return AccessControlPolicy(policyAddress).evaluateRequest(reqContext);
    }

}