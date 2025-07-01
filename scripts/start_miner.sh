#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
MINER_PORT=${MINER_PORT:-8091}
port=${1:-$MINER_PORT}
MINER_WALLET=${MINER_WALLET:-miner}
MINER_HOTKEY=${MINER_HOTKEY:-default}

# Use host.docker.internal for Docker containers, otherwise use the configured endpoint
if [ -f /.dockerenv ]; then
    chain_endpoint="ws://host.docker.internal:9944"
else
    chain_endpoint=${CHAIN_ENDPOINT:-$default_chain_endpoint}
fi

export BT_SUBTENSOR_CHAIN_ENDPOINT=$chain_endpoint
echo "Running miner python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $MINER_WALLET --wallet.hotkey $MINER_HOTKEY --logging.debug  --axon.port $port"
python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $MINER_WALLET --wallet.hotkey $MINER_HOTKEY --logging.debug  --axon.port $port # --neuron.epoch_length 101