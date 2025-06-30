#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
VALIDATOR_PORT=${VALIDATOR_PORT:-8092}
port=${1:-$VALIDATOR_PORT}

echo "Running validator $chain_endpoint $netuid $port"
export BT_SUBTENSOR_CHAIN_ENDPOINT=$chain_endpoint
python -m neurons.validator --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name validator --wallet.hotkey default --logging.debug --axon.port $port #--neuron.epoch_length 101