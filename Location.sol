pragma solidity >=0.4.22 <0.7.0;

/**
 * @title Location
 * @dev Trigger update upon reaching location
 */
contract Location {
    
    uint256 lat;
    uint256 long;
    
    //constructor defines location values
    constructor (uint256 _lat, uint256 _long) public {
        lat = _lat;
        long = _long;
    }
    
    // the message received by the contract is in 'currentStatus'
    function updateStatus(string memory currentStatus) public returns (string memory) {
        if (keccak256(bytes(currentStatus)) == keccak256(bytes("true")))
        {
            return "reachedLocation";
        }
        else
            return "deliveryPending";
    }

}
