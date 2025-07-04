#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
VALIDATOR_PORT=${VALIDATOR_PORT:-8092}
port=${1:-$VALIDATOR_PORT}
VALIDATOR_WALLET=${VALIDATOR_WALLET:-validator}
VALIDATOR_HOTKEY=${VALIDATOR_HOTKEY:-default}

# Build axon.external_ip parameter based on network
if [ "$network" = "local" ] && [ -n "$external_ip" ]; then
    axon_external_ip_param="--axon.external_ip $external_ip"
else
    axon_external_ip_param=""
fi

echo "Running validator python -m neurons.validator --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $VALIDATOR_WALLET --wallet.hotkey $VALIDATOR_HOTKEY --logging.debug --axon.port $port $axon_external_ip_param"
python -m neurons.validator --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $VALIDATOR_WALLET --wallet.hotkey $VALIDATOR_HOTKEY --logging.debug --axon.port $port $axon_external_ip_param #--neuron.epoch_length 101