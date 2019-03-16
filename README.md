# DeFi in a Box

One day, @Alexintosh [had a dream](https://twitter.com/Alexintosh/status/1106200673509625856). He dreamed of a world where a #buidler could use all of the latest and greatest #DeFi protocols on the locally or on the same testnet, without having to test code on main net with real funds.

Many people shared this dream, so here is a repository containing the first draft of Defi in a Box - a self-contained project which will (hopefully) simplify the process of experimenting with DeFi protocols in a testing environment.

## Included Apps and Protocols

- [x] Ganache
- [x] Uniswap exchanges
- [ ] Uniswap front-end
- [ ] Kyber Network
- [ ] 0x
- [ ] Compound Finance
- [ ] Aave
- [ ] MakerDAO
- [ ] Dharma
- [ ] bZx
- [ ] dYdX
- [ ] Nuo


## Getting Started

0. Install [Docker Compose](https://docs.docker.com/compose/install/) and Python 3
1. Clone this repository: `git clone git@github.com:mikery/defi-in-a-box.git && cd defi-in-a-box`
2. Initialise git submodules: `git submodule init && git submodule update`
3. Start Ganache: `docker-compose up -d ganache`
4. View Ganache logs to retrieve private keys: `docker-compose logs ganache`
5. Run the deployment script: `docker-compose run deploy`
6. Start the Uniswap front-end: `docker-compose up -d uniswap-frontend`
7. Configure MetaMask to use `http://localhost:8545`, and import test accounts
8. Open the Uniswap front-end: [localhost:3000](http://localhost:3000)


## How Does it Work?

Ganache is run in a Docker container. A Python script deploys all required contracts and executes transactions to set up the testing environment. Upon completion the script writes a file (`contract-addresses.json`) containing all token addresses, Uniswap exchange addresses, etc. 

## Ganache

Ganache data is stored in `./ganache`. Remove this directory and restart the Ganache container to reset the chain state:

```bash
docker-compose stop ganache
docker-compose rm --force ganache
rm -rf ./ganache
docker-compose up -d ganache
```

The mnemonic is `candy maple cake sugar pudding cream honey rich smooth crumble sweet treat`.

```
Available Accounts
==================
(0) 0x627306090abab3a6e1400e9345bc60c78a8bef57 (~100 ETH)
(1) 0xf17f52151ebef6c7334fad080c5704d77216b732 (~100 ETH)
(2) 0xc5fdf4076b8f3a5357c5e395ab970b5b54098fef (~100 ETH)

Private Keys
==================
(0) 0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3
(1) 0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f
(2) 0x0dbbe8e4ae425a6d2687f1a7e3ba17bc98c673636790f1b8ad91193c05875ef1
```

### Tokens

Three test ERC20 tokens are created. The token uses OpenZeppelin's [Mintable](https://docs.openzeppelin.org/docs/token_erc20_mintabletoken) token, and the first three test accounts are issued with one million of each token.

| Name      | Symbol    | Decimals  | Initial Exchange Rate | Uniswap Liquidity |
| ---       | ---       | ---       | ---                   | ---               | 
| Alpha     | ALP       | 18        | 0.00001               | 500000            |
| Bravo     | BRA       | 18        | 0.00002               | 500000            |
| Charlie   | CHA       | 18        | 0.00003               | 500000            |

### Uniswap

Exhanges are created for each of the test tokens. The main account (`web3.eth.accounts[0]`) creates a liquidity pool for each token using the `exchange_rate` and `initial_liquidity` parameters defined in `defi_in_a_box/config.py`.

Test tokens are added to the front-end by generating a custom version of `uniswap-frontend/src/ducks/addresses.js` containing the correct exchange/token addresses.

Live-reload is enabled and the local working directory is mounted into the `uniswap-frontend` container, so changes to the front-end's JS files should be immediately reflected in your browser.

Note: The front-end is not yet working correctly (`Maximum update depth exceeded`).

# Contributing

Contributions are welcome. To add a new project:

- add a new submodule, referencing the Git repo for the project's smart contracts
- using `defi_in_a_box/uniswap.py` as an example, add a `<project>.py` file containing functions required to deploy the project's contracts and set the desired development state
- call these functions in `defi_in_a_box/uniswap.py`'s `main()`
- update the output file to include any relevant contract addresses


# Alternatives

- [defi-test-stack](https://github.com/dekz/defi-test-stack)

