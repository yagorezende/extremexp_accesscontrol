// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "contracts/interfaces/AccessControlPolicy.sol";

contract SamplePolicy is AccessControlPolicy {
    string[] allowedRoles; // data-processor, admin
    Area[] allowedLocations; // Array of allowed Areas
    string [] allowedGroups;
    bytes32[] allowedIPs;
    uint256 radiusMetersSquared;
    uint8 userShiftStart; // e.g.: 9h
    uint8 userShiftEnd; // e.g: 17h
    uint8 userWorkingDayStart; // e.g.: 1 -> monday
    uint8 userWorkingDayEnd; // e.g.: 5 -> friday
    bytes32 resourceContentValidHash;
    PolicyMetadata public policyMetadata;

    constructor (
        string memory policyReadableName,
        string[] memory allowedRoles_,
        int256[] memory allowedLocations_, // every 2 is a location object or int256[] with [lat, long]
        string[] memory allowedGroups_,
        string[] memory allowedIPs_,
        string memory resourceContentValidHash_,
        uint8 userShiftStart_,
        uint8 userShiftEnd_,
        uint8 userWorkingDayStart_,
        uint8 userWorkingDayEnd_
    ) {
        allowedRoles = allowedRoles_;
        allowedGroups = allowedGroups_;
        resourceContentValidHash = keccak256(abi.encodePacked(resourceContentValidHash_));
        userShiftStart = userShiftStart_;
        userShiftEnd = userShiftEnd_;
        userWorkingDayStart = userWorkingDayStart_;
        userWorkingDayEnd = userWorkingDayEnd_;
        policyMetadata = PolicyMetadata(msg.sender, policyReadableName, block.timestamp);

        for(uint i = 0; i < allowedIPs_.length; i++){
            allowedIPs.push(keccak256(abi.encodePacked(allowedIPs_[i])));
        }

        require(allowedLocations_.length % 8 == 0, "Allowed locations should have at least 4 points");
        assembleAreas(allowedLocations_);
    }

    function assembleAreas(int256[] memory points) private {
        for (uint8 i = 0; i < points.length; i += 8) {
            Area memory polygon = Area(
                Location(points[i+0], points[i+1]),
                Location(points[i+2], points[i+3]),
                Location(points[i+4], points[i+5]),
                Location(points[i+6], points[i+7]));
            allowedLocations.push(polygon);
        }
    }

    function isDuringWorkHours() public view returns (bool) {
        // add role test
        uint8 hour = uint8((block.timestamp / 60 / 60) % 24); // Hours since midnight UTC
        uint8 weekday = uint8((block.timestamp / 86400 + 4) % 7);
        return (hour >= userShiftStart && hour <= userShiftEnd) && (weekday >= userWorkingDayStart && weekday <= userWorkingDayEnd);
    }

    function isIPWhitelisted(string memory ip) public view returns (bool) {
        bytes32 ipHash = keccak256(abi.encodePacked(ip));
        for (uint i = 0; i < allowedIPs.length; i++) {
            if (allowedIPs[i] == ipHash) {
                return true;
            }
        }
        return false;
    }

    /// @notice Checks if a point is inside a polygon (4 points)
    /// @param polygon with 4 points defining the area (must be convex or concave)
    /// @param targetPoint The point to test
    /// @return True if inside, false otherwise
    function isPointInPolygon(Area memory polygon, Location memory targetPoint) public pure returns (bool) {
        uint8 crossings = 0;

        if ((polygon.x.lat > targetPoint.lat) != (polygon.y.lat > targetPoint.lat)) {
            int256 x = (polygon.y.long - polygon.x.long) * (targetPoint.lat - polygon.x.lat) / (polygon.y.lat - polygon.x.lat) + polygon.x.long;
            if (targetPoint.long < x) crossings++;
        }

        if ((polygon.y.lat > targetPoint.lat) != (polygon.z.lat > targetPoint.lat)) {
            int256 x = (polygon.z.long - polygon.y.long) * (targetPoint.lat - polygon.y.lat) / (polygon.z.lat - polygon.y.lat) + polygon.y.long;
            if (targetPoint.long < x) crossings++;
        }

        if ((polygon.z.lat > targetPoint.lat) != (polygon.w.lat > targetPoint.lat)) {
            int256 x = (polygon.w.long - polygon.z.long) * (targetPoint.lat - polygon.z.lat) / (polygon.w.lat - polygon.z.lat) + polygon.z.long;
            if (targetPoint.long < x) crossings++;
        }

        if ((polygon.w.lat > targetPoint.lat) != (polygon.x.lat > targetPoint.lat)) {
            int256 x = (polygon.x.long - polygon.w.long) * (targetPoint.lat - polygon.w.lat) / (polygon.x.lat - polygon.w.lat) + polygon.w.long;
            if (targetPoint.long < x) crossings++;
        }

        return (crossings % 2 == 1); // Odd crossings = inside
    }

    function isUserNearApprovedLocation(Location memory userLocation) public view returns (bool) {
        for (uint8 i = 0; i < allowedLocations.length; i++){
            if(!isPointInPolygon(allowedLocations[i], userLocation)){
                return false;
            }
        }
        return true;
    }

    function hasAllowedRole(string memory userRole) public view returns (bool) {
        for (uint i = 0; i < allowedRoles.length; i++) {
            if (keccak256(abi.encodePacked(allowedRoles[i])) == keccak256(abi.encodePacked(userRole))) {
                return true;
            }
        }
        return false;
    }

    function hasAllowedGroup(string[] memory userGroups) public view returns (bool) {
        for (uint i = 0; i < userGroups.length; i++) {
            for(uint j = 0; j < allowedGroups.length; j++){
                if(keccak256(abi.encodePacked(userGroups[i])) == keccak256(abi.encodePacked(allowedGroups[j]))){
                    return true;
                }
            }
        }
        return false;
    }

    function isResourceValid(string memory resourceContentHash) public view returns (bool){
        return keccak256(abi.encodePacked(resourceContentHash)) == resourceContentValidHash;
    }

    function evaluateRequest(RequestContext memory context) external view returns (bool) {
        return
        isResourceValid(context.resourceContentHash) &&
        hasAllowedRole(context.userRole) &&
        hasAllowedGroup(context.userGroups) &&
        isDuringWorkHours() &&
        isIPWhitelisted(context.userIPAddress) &&
        isUserNearApprovedLocation(context.userLocation);
    }
}
