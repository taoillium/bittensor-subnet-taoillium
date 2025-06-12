#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

echo "Running validator"
python -m neurons.validator --netuid 2 --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name validator --wallet.hotkey default --logging.debug #--neuron.epoch_length 101