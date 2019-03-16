from collections import namedtuple

Token = namedtuple(
    'Token',
    [
        'name',
        'symbol',
        'decimals',
        'exchange_rate',  # Initial price of token when populating liquidity pools
        'initial_balance',  # Amount of tokens to mint (per test account)
        'initial_liquidity'  # Amount of tokens to deposit to liquidity pools
    ]
)

tokens = [
    Token('Alpha', 'ALP', 18, 0.00001, 1000000, 500000),
    Token('Bravo', 'BRA', 18, 0.00002, 1000000, 500000),
    Token('Charlie', 'CHA', 18, 0.00003, 1000000, 500000),
]
