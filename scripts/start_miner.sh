#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
MINER_PORT=${MINER_PORT:-8091}
port=${1:-$MINER_PORT}

# Use host.docker.internal for Docker containers, otherwise use the configured endpoint
if [ -f /.dockerenv ]; then
    chain_endpoint="ws://host.docker.internal:9944"
else
    chain_endpoint=${CHAIN_ENDPOINT:-$default_chain_endpoint}
fi

echo "Running miner $chain_endpoint $netuid $port"
export BT_SUBTENSOR_CHAIN_ENDPOINT=$chain_endpoint
python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name miner --wallet.hotkey default --logging.debug  --axon.port $port # --neuron.epoch_length 101