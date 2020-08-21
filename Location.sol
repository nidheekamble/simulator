pragma solidity >=0.4.22 <0.7.0;

/**
 * @title Location
 * @dev Trigger update upon reaching location
 */
contract Location {
    
    uint256 lat;
    uint256 long;
    uint256 cost;
    address payable company;
    
    //constructor defines location values
    constructor (uint256 _lat, uint256 _long, uint _cost, address payable _company) public {
        lat = _lat;
        long = _long;
        cost = _cost;
        company = _company;
    }
    
    // the message received by the contract is in 'currentStatus'
    function updateStatus(uint256 curr_lat, uint256 curr_long) payable public returns (string memory) {
        require(msg.value>cost, "client does not have enough money to pay for the delivery");
        if (curr_lat==lat && curr_long==long )
        {
            company.transfer(cost);                 //transfer money to company on reaching location.
            msg.sender.transfer(msg.value-cost);    //transfer the remaining value for msg back to user, if any
            return "reachedLocation";
        }
        else{
             msg.sender.transfer(msg.value); 
             return "deliveryPending";
        }
           
    }

}
