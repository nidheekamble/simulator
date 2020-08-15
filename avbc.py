from web3 import Web3
import json

web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
with open('contract1.json') as f:
    contractDetails = json.load(f)
    contractAddress = (contractDetails["address"])
    abi = contractDetails["abi"]

Contract = web3.eth.contract(bytecode=contractAddress, abi=abi)

_company = web3.eth.accounts[1]
_cost = 1000000000000000000
_lat = 10
_long = 10

tx_hash = Contract.constructor(_company=_company, _cost=_cost, _lat = _lat, _long = _long).transact(
    transaction={'from': web3.eth.accounts[0], 'gas': 410000})

# Get tx receipt to get contract address
tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']
contract = web3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=abi,
)

# while input is received from sensors. for now values are hardcoded.
contract.functions.updateStatus(10, 10).transact(transaction={'from': web3.eth.accounts[0], 'gas': 410000, 'value':10000000000000000000})