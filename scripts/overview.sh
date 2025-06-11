#!/bin/bash
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi
# Ensure both the miner and validator keys are successfully registered.
echo "Listing subnets"
btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9944

echo "Checking owner wallet"
btcli wallet overview --wallet.name owner --subtensor.chain_endpoint ws://127.0.0.1:9944

echo "Checking validator wallet"
btcli wallet overview --wallet.name validator --subtensor.chain_endpoint ws://127.0.0.1:9944

echo "Checking miner wallet"
btcli wallet overview --wallet.name miner --subtensor.chain_endpoint ws://127.0.0.1:9944