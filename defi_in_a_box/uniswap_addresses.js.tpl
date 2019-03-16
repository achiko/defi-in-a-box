const {{ network_name }} = {
  factoryAddress: '{{ factory_address }}',
  exchangeAddresses: {
    addresses: {{ exchange_addresses }},
    fromToken: {{ from_token }}
  },
  tokenAddresses: {
    addresses: {{ token_addresses }},
  },
};

const MAIN = {};
const RINKEBY = {};

const SET_ADDRESSES = 'app/addresses/setAddresses';
const ADD_EXCHANGE = 'app/addresses/addExchange';

const initialState = {{ network_name }};

export const addExchange = ({label, exchangeAddress, tokenAddress}) => (dispatch, getState) => {
  const { addresses: { tokenAddresses, exchangeAddresses } } = getState();

  if (tokenAddresses.addresses.filter(([ symbol ]) => symbol === label).length) {
    return;
  }

  if (exchangeAddresses.fromToken[tokenAddresses]) {
    return;
  }

  dispatch({
    type: ADD_EXCHANGE,
      payload: {
      label,
        exchangeAddress,
        tokenAddress,
    },
  });
};

export const setAddresses = networkId => {
  switch(networkId) {
    // Main Net
    case 1:
    case '1':
      return {
        type: SET_ADDRESSES,
        payload: MAIN,
      };
    // Rinkeby
    case 4:
    case '4':
      return {
        type: SET_ADDRESSES,
        payload: MAIN,
      };
    default:
      return {
        type: SET_ADDRESSES,
        payload: GANACHE,
      };
  }
};


export default (state = initialState, { type, payload }) => {
  switch (type) {
    case SET_ADDRESSES:
      return payload;
    case ADD_EXCHANGE:
      return handleAddExchange(state, { payload });
    default:
      return state;
  }
}

function handleAddExchange(state, { payload }) {
  const { label, tokenAddress, exchangeAddress } = payload;

  if (!label || !tokenAddress || !exchangeAddress) {
    return state;
  }

  return {
    ...state,
    exchangeAddresses: {
      ...state.exchangeAddresses,
      addresses: [
        ...state.exchangeAddresses.addresses,
        [label, exchangeAddress]
      ],
      fromToken: {
        ...state.exchangeAddresses.fromToken,
        [tokenAddress]: exchangeAddress,
      },
    },
    tokenAddresses: {
      ...state.tokenAddresses,
      addresses: [
        ...state.tokenAddresses.addresses,
        [label, tokenAddress]
      ],
    },
  };
}
