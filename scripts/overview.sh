#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

MINER_WALLET=${MINER_WALLET:-miner}
VALIDATOR_WALLET=${VALIDATOR_WALLET:-validator}

# Ensure both the miner and validator keys are successfully registered.
#echo "Listing subnets"
btcli subnet show  --netuid $netuid --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking owner wallet"
btcli wallet overview --wallet.name owner --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking validator wallet"
btcli wallet overview --wallet.name $VALIDATOR_WALLET --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking miner wallet"
btcli wallet overview --wallet.name $MINER_WALLET --subtensor.chain_endpoint ${chain_endpoint}