from web3.auto import w3


def deploy_contract(abi, bytecode, constructor_kwargs=None):
    """ Deploy the specified contract, and return an instantiated Contract object. """
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract.constructor(
        **constructor_kwargs if constructor_kwargs else {}
    ).transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi
    )
