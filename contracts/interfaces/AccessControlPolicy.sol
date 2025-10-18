// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;



interface AccessControlPolicy {

    struct PolicyMetadata {
        address createdBy;
        string readableName;
        uint createdAt;
    }

    struct Location {
        int256 lat;
        int256 long;
    }

    // Area is a 4 pont region, where the points are ordered
    struct Area {
        Location x;
        Location y;
        Location z;
        Location w;
    }

    struct RequestContext {
        address userWalletAddress;
        string userRole;
        string userEmail;
        string[] userGroups;
        Location userLocation; // [lat, long]
        string userIPAddress;
        string userRequestScope;
        string resourceURI;
        string resourceContentHash;
    }

    function evaluateRequest(RequestContext memory context) external view returns (bool);
}