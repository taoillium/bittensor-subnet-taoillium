#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

echo "Running miner"
python -m neurons.miner --netuid 2 --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name miner --wallet.hotkey default --logging.debug  --axon.port 8901 # --neuron.epoch_length 101