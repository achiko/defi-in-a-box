import json
import logging
import os
import time

from jinja2 import Template
from web3 import Web3
from web3.auto import w3

from config import Token
from utils import deploy_contract


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


base_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(base_dir, '../uniswap-contracts-vyper/abi/uniswap_exchange.json')) as f:
    exchange_abi = json.load(f)

with open(os.path.join(base_dir, '../uniswap-contracts-vyper/abi/uniswap_factory.json')) as f:
    factory_abi = json.load(f)

with open(os.path.join(base_dir, '../uniswap-contracts-vyper/bytecode/exchange.txt')) as f:
    exchange_bc = f.read().strip()

with open(os.path.join(base_dir, '../uniswap-contracts-vyper/bytecode/factory.txt')) as f:
    factory_bc = f.read().strip()


def write_uniswap_addresses(factory_address, tokens, token_exchange_map):
    """ Write the addresses.js file to insert our tokens into the frontend
    """
    with open(os.path.join(base_dir, 'uniswap_addresses.js.tpl')) as f:
        template = Template(f.read())

    exchange_addresses = []
    from_token = {}
    token_addresses = []

    for token in tokens:
        token_contract, exchange_contract = token_exchange_map[token.symbol]
        exchange_addresses.append([token.symbol, exchange_contract.address])
        from_token[token_contract.address] = exchange_contract.address
        token_addresses.append([token.symbol, token_contract.address])

    addresses_file = template.render(
        network_name='GANACHE',
        factory_address=factory_address,
        exchange_addresses=exchange_addresses,
        from_token=from_token,
        token_addresses=token_addresses
    )
    logger.info(f'Writing Uniswap addresses.js file')
    with open(os.path.join(base_dir, '../uniswap-addresses.js'), 'wb') as f:
        f.write(addresses_file.encode('utf-8'))


def create_factory():
    """ Create and initialise the factory contract """
    # Deploy the exchange template contract
    exchange_template = deploy_contract(
        abi=exchange_abi, bytecode=exchange_bc
    )
    # Get uniswap factory and initialise it
    factory = deploy_contract(
        abi=factory_abi, bytecode=factory_bc
    )
    factory.functions.initializeFactory(
        template=Web3.toChecksumAddress(exchange_template.address)
    ).transact()
    return factory


def create_exchange(token: Token, token_contract, factory):
    """ Create an exchange for the token and add liquidity """

    eth_value = token.initial_liquidity * token.exchange_rate
    logger.info(
        f'Creating Uniswap exchange for {token.name} with rate {token.exchange_rate}'
        f' and initial liquidity {token.initial_liquidity} {token.symbol}/{eth_value} ETH'
    )
    factory.functions.createExchange(
        token=Web3.toChecksumAddress(token_contract.address)
    ).transact()

    token_exchange_address = factory.functions.getExchange(
        token=Web3.toChecksumAddress(token_contract.address)
    ).call()

    # Approve the exchange contract to send tokens
    token_contract.functions.approve(
        spender=token_exchange_address,
        value=token.initial_liquidity * 10 ** token.decimals
    ).transact()

    token_exchange = w3.eth.contract(
        address=token_exchange_address,
        abi=exchange_abi,
    )

    token_exchange.functions.addLiquidity(
        min_liquidity=0,
        max_tokens=token.initial_liquidity * 10 ** token.decimals,
        deadline=int(time.time()) + 3600
    ).transact({'value': Web3.toWei(eth_value, 'ether')})

    return token_exchange
