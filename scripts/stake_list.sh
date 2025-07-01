#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

MINER_WALLET=${MINER_WALLET:-miner}
VALIDATOR_WALLET=${VALIDATOR_WALLET:-validator}

# Ensure both the miner and validator keys are successfully registered.
echo "btcli stake list --wallet.name $MINER_WALLET --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}"
btcli stake list --wallet.name $MINER_WALLET --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}

echo "btcli stake list --wallet.name $VALIDATOR_WALLET --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}"
btcli stake list --wallet.name $VALIDATOR_WALLET --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}
