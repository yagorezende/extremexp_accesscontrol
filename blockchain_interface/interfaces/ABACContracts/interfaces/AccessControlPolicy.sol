// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;



interface AccessControlPolicy {

    struct Location {
        int256 lat;
        int256 long;
    }

    struct RequestContext {
        address userWalletAddress;
        string userRole;
        string[] userGroups;
        Location userLocation; // [lat, long]
        string userIPAddress;
        string userRequestScope;
        string resourceURI;
        string resourceContentHash;
    }

    function evaluateRequest(RequestContext memory context) external view returns (bool);
}