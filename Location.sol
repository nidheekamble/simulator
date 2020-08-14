pragma solidity >=0.4.22 <0.7.0;

/**
 * @title Location
 * @dev Trigger update upon reaching location
 */
contract Location {

    // the message received by the contract is in 'currentStatus'

    function updateStatus(bool currentStatus) public returns (string) {
        if currentStatus == true
        {
            return "reachedLocation";
        }
        else
            return "deliveryPending";
    }

}