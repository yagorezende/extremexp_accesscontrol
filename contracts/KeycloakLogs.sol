// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract KeycloakLogs {
    string[] logs;

    // Function to add a new log to the logs list
    function push(string memory log) public {
        logs.push(log);
    }

    // Function to get the current log
    function getLastLog() public view returns (string memory) {
        if(logs.length > 0) return logs[logs.length-1];
        return '';
    }

    function length() public view returns (uint){
        return logs.length;
    }
}
