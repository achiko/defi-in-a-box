import json
import logging
import os

from web3 import Web3
from web3.auto import w3

from config import tokens, Token
from uniswap import create_factory, create_exchange, write_uniswap_addresses
from utils import deploy_contract


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

ERC20_BC = '0x60806040523480156200001157600080fd5b50604051620012e0380380620012e0833981018060405260608110156200003757600080fd5b8101908080516401000000008111156200005057600080fd5b828101905060208101848111156200006757600080fd5b81518560018202830111640100000000821117156200008557600080fd5b50509291906020018051640100000000811115620000a257600080fd5b82810190506020810184811115620000b957600080fd5b8151856001820283011164010000000082111715620000d757600080fd5b50509291906020018051906020019092919050505062000106336200010f640100000000026401000000009004565b505050620002d1565b62000133816003620001796401000000000262000e74179091906401000000009004565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614151515620001b657600080fd5b620001d182826200023c640100000000026401000000009004565b151515620001de57600080fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff16141515156200027a57600080fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff16905092915050565b610fff80620002e16000396000f3fe608060405234801561001057600080fd5b50600436106100d1576000357c010000000000000000000000000000000000000000000000000000000090048063983b2d561161008e578063983b2d56146103045780639865027514610348578063a457c2d714610352578063a9059cbb146103b8578063aa271e1a1461041e578063dd62ed3e1461047a576100d1565b8063095ea7b3146100d657806318160ddd1461013c57806323b872dd1461015a57806339509351146101e057806340c10f191461024657806370a08231146102ac575b600080fd5b610122600480360360408110156100ec57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506104f2565b604051808215151515815260200191505060405180910390f35b610144610509565b6040518082815260200191505060405180910390f35b6101c66004803603606081101561017057600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610513565b604051808215151515815260200191505060405180910390f35b61022c600480360360408110156101f657600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506105c4565b604051808215151515815260200191505060405180910390f35b6102926004803603604081101561025c57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610669565b604051808215151515815260200191505060405180910390f35b6102ee600480360360208110156102c257600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610693565b6040518082815260200191505060405180910390f35b6103466004803603602081101561031a57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506106db565b005b6103506106fb565b005b61039e6004803603604081101561036857600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610706565b604051808215151515815260200191505060405180910390f35b610404600480360360408110156103ce57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506107ab565b604051808215151515815260200191505060405180910390f35b6104606004803603602081101561043457600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506107c2565b604051808215151515815260200191505060405180910390f35b6104dc6004803603604081101561049057600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506107df565b6040518082815260200191505060405180910390f35b60006104ff338484610866565b6001905092915050565b6000600254905090565b60006105208484846109c9565b6105b984336105b485600160008a73ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610b9590919063ffffffff16565b610866565b600190509392505050565b600061065f338461065a85600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008973ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610bb790919063ffffffff16565b610866565b6001905092915050565b6000610674336107c2565b151561067f57600080fd5b6106898383610bd8565b6001905092915050565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b6106e4336107c2565b15156106ef57600080fd5b6106f881610d2c565b50565b61070433610d86565b565b60006107a1338461079c85600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008973ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610b9590919063ffffffff16565b610866565b6001905092915050565b60006107b83384846109c9565b6001905092915050565b60006107d8826003610de090919063ffffffff16565b9050919050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905092915050565b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff16141515156108a257600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156108de57600080fd5b80600160008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508173ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925836040518082815260200191505060405180910390a3505050565b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1614151515610a0557600080fd5b610a56816000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610b9590919063ffffffff16565b6000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610ae9816000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610bb790919063ffffffff16565b6000808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508173ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040518082815260200191505060405180910390a3505050565b6000828211151515610ba657600080fd5b600082840390508091505092915050565b6000808284019050838110151515610bce57600080fd5b8091505092915050565b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1614151515610c1457600080fd5b610c2981600254610bb790919063ffffffff16565b600281905550610c80816000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610bb790919063ffffffff16565b6000808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508173ffffffffffffffffffffffffffffffffffffffff16600073ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040518082815260200191505060405180910390a35050565b610d40816003610e7490919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b610d9a816003610f2490919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167fe94479a9f7e1952cc78f2d6baab678adc1b772d936c6583def489e524cb6669260405160405180910390a250565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1614151515610e1d57600080fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff16905092915050565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614151515610eb057600080fd5b610eba8282610de0565b151515610ec657600080fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614151515610f6057600080fd5b610f6a8282610de0565b1515610f7557600080fd5b60008260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff021916908315150217905550505056fea165627a7a72305820501e29e334c6a2edceb1ffab1bf45e62ae065818aba2933a2900fdbf8979d83f0029'
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "spender",
                "type": "address"
            },
            {
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0x095ea7b3"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
        "signature": "0x18160ddd"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "from",
                "type": "address"
            },
            {
                "name": "to",
                "type": "address"
            },
            {
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0x23b872dd"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "spender",
                "type": "address"
            },
            {
                "name": "addedValue",
                "type": "uint256"
            }
        ],
        "name": "increaseAllowance",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0x39509351"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "to",
                "type": "address"
            },
            {
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "mint",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0x40c10f19"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
        "signature": "0x70a08231"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "account",
                "type": "address"
            }
        ],
        "name": "addMinter",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0x983b2d56"
    },
    {
        "constant": False,
        "inputs": [],
        "name": "renounceMinter",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0x98650275"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "spender",
                "type": "address"
            },
            {
                "name": "subtractedValue",
                "type": "uint256"
            }
        ],
        "name": "decreaseAllowance",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0xa457c2d7"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "to",
                "type": "address"
            },
            {
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0xa9059cbb"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "account",
                "type": "address"
            }
        ],
        "name": "isMinter",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
        "signature": "0xaa271e1a"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "owner",
                "type": "address"
            },
            {
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
        "signature": "0xdd62ed3e"
    },
    {
        "inputs": [
            {
                "name": "name",
                "type": "string"
            },
            {
                "name": "symbol",
                "type": "string"
            },
            {
                "name": "decimals",
                "type": "uint8"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "constructor",
        "signature": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "account",
                "type": "address"
            }
        ],
        "name": "MinterAdded",
        "type": "event",
        "signature": "0x6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f6"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "account",
                "type": "address"
            }
        ],
        "name": "MinterRemoved",
        "type": "event",
        "signature": "0xe94479a9f7e1952cc78f2d6baab678adc1b772d936c6583def489e524cb66692"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event",
        "signature": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event",
        "signature": "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
    }
]


def initialise_token(token: Token):
    """ Deploy the ERC20 contract, create uniswap exchange, add liquidity

        Returns deployed token_contract
    """
    logger.info(f'Deploying contract for {token.name}')
    token_contract = deploy_contract(
        abi=ERC20_ABI,
        bytecode=ERC20_BC,
        constructor_kwargs=dict(
            name=token.name,
            symbol=token.symbol,
            decimals=token.decimals
        )
    )
    # Mint tokens for the first three accounts
    logger.info(f'Minting {token.initial_balance} {token.symbol} for {", ".join([a for a in w3.eth.accounts[:3]])}')
    for address in w3.eth.accounts[:3]:
        token_contract.functions.mint(
            to=Web3.toChecksumAddress(address),
            value=token.initial_balance * 10 ** token.decimals
        ).transact()

    return token_contract


def main():
    """ Initialise tokens. Create Uniswap exchanges.
    """
    w3.eth.defaultAccount = w3.eth.accounts[0]
    token_contracts = {}
    uniswap_factory = create_factory()

    output = {
        'tokens': {},
        'uniswap': {
            'factory': uniswap_factory.address,
            'exchanges': {}
        }
    }

    for token in tokens:
        token_contract = initialise_token(token=token)

        exchange_contract = create_exchange(token, token_contract, factory=uniswap_factory)
        token_contracts[token.symbol] = token_contract, exchange_contract

        output['tokens'][token.symbol] = token_contract.address
        output['uniswap']['exchanges'][token.symbol] = exchange_contract.address

    # write uniswap addresses.js file
    write_uniswap_addresses(uniswap_factory.address, tokens, token_contracts)

    # write address output file - addresses for tokens, uniswap exchanges, etc
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../contract-addresses.json'), 'wb') as f:
        f.write(json.dumps(output).encode('utf-8'))


if __name__ == '__main__':
    main()
