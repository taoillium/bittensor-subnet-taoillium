#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

echo "VALIDATOR_WALLET: $VALIDATOR_WALLET"

# Ensure both the miner and validator keys are successfully registered.
echo "Listing subnets"
btcli subnet list --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking owner wallet"
btcli wallet overview --wallet.name owner --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking validator wallet"
btcli wallet overview --wallet.name validator --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking miner wallet"
btcli wallet overview --wallet.name miner --subtensor.chain_endpoint ${chain_endpoint}