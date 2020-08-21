from web3 import Web3
import json

# Copy this part into your main file
web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545")) # Verify if your Ganache is at 7545 too, should be
with open('contract1.json') as f:
    contractDetails = json.load(f)
    contractAddress = (contractDetails["address"])
    abi = contractDetails["abi"]

Contract = web3.eth.contract(bytecode=contractAddress, abi=abi)


def updateStatus(dest_lat, dest_long, curr_lat, curr_long):    
    _company = web3.eth.accounts[1]
    _cost = 1000000000000000000
    _lat = dest_lat
    _long = dest_long
    
    tx_hash = Contract.constructor(_company=_company, _cost=_cost, _lat = _lat, _long = _long).transact(
        transaction={'from': web3.eth.accounts[0], 'gas': 410000})
    
    # Get tx receipt to get contract address
    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    contract = web3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi,
    )    
    contract.functions.updateStatus(curr_lat, curr_long).transact(transaction={'from': web3.eth.accounts[0], 'gas': 410000, 'value':10000000000000000000})
