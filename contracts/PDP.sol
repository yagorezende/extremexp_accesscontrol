// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "contracts/PAP.sol";
import "contracts/PIP.sol";
import "contracts/interfaces/AccessControlPolicy.sol";

contract PDP {
    PolicyAdministrationPoint private pap;
    PolicyInformationPoint private pip;

    constructor(address papAddress, address pipAddress) {
        pap = PolicyAdministrationPoint(papAddress);
        pip = PolicyInformationPoint(pipAddress);
    }

    function evaluateRequest(
        address user,
        string memory userEmail,
        string memory userIPAddress,
        string memory userRequestScope,
        int256 userLat, int256 userLong,
        string memory resourceURI) public view returns (bool) {

        // check if caller has access on behalf of user
        require(pip.organisationHasAccess(user, msg.sender), "Organisation does not have access on behalf of user");

        // get policy for resource
        address policyAddress = pap.getResourcePolicy(resourceURI);

        // get resource attributes
        PolicyInformationPoint.ResourceAttributes memory resourceAttribute = pip.getResourceAttributes(resourceURI);

        // assemble request context
        AccessControlPolicy.RequestContext memory reqContext = AccessControlPolicy.RequestContext(
            user,
            pip.getUserRoleAttribute(user),
            userEmail,
            pip.getUserGroups(user),
            AccessControlPolicy.Location(userLat, userLong),
            userIPAddress,
            userRequestScope,
            resourceURI,
            resourceAttribute.contentHash
        );

        // evaluate request against policy
        return AccessControlPolicy(policyAddress).evaluateRequest(reqContext);
    }

    function setPAP(address papAddress) public {
        pap = PolicyAdministrationPoint(papAddress);
    }

    function setPIP(address pipAddress) public {
        pip = PolicyInformationPoint(pipAddress);
    }

    function getPAP() public view returns (address) {
        return address(pap);
    }

    function getPIP() public view returns (address) {
        return address(pip);
    }
}