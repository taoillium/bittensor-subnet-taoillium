#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

echo "VALIDATOR_WALLET: $VALIDATOR_WALLET"

# Ensure both the miner and validator keys are successfully registered.
echo "btcli stake list --wallet.name miner --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}"
btcli stake list --wallet.name miner --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}

echo "btcli stake list --wallet.name validator --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}"
btcli stake list --wallet.name validator --network local --verbose --subtensor.chain_endpoint ${chain_endpoint}
