#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
MINER_PORT=${MINER_PORT:-8091}
port=${1:-$MINER_PORT}
MINER_WALLET=${MINER_WALLET:-miner}
MINER_HOTKEY=${MINER_HOTKEY:-default}

# Build axon.external_ip parameter based on network
if [ "$network" = "local" ] && [ -n "$external_ip" ]; then
    axon_external_ip_param="--axon.external_ip $external_ip"
else
    axon_external_ip_param=""
fi

echo "Running miner python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $MINER_WALLET --wallet.hotkey $MINER_HOTKEY --logging.debug  --axon.port $port $axon_external_ip_param"
python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $MINER_WALLET --wallet.hotkey $MINER_HOTKEY --logging.debug  --axon.port $port $axon_external_ip_param # --neuron.epoch_length 101