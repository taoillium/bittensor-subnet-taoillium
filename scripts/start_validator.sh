#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
port=${1:-8092}
echo "Running validator"
python -m neurons.validator --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name validator --wallet.hotkey default --logging.debug --axon.port $port #--neuron.epoch_length 101