#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
VALIDATOR_PORT=${VALIDATOR_PORT:-8092}
port=${1:-$VALIDATOR_PORT}

# Set validator wallet with fallback chain: VALIDATOR_WALLET -> WALLET_NAME -> validator
VALIDATOR_WALLET=${VALIDATOR_WALLET:-$WALLET_NAME}
VALIDATOR_WALLET=${VALIDATOR_WALLET:-validator}

# Set validator hotkey with fallback chain: VALIDATOR_HOTKEY -> HOTKEY_NAME -> default
VALIDATOR_HOTKEY=${VALIDATOR_HOTKEY:-$HOTKEY_NAME}
VALIDATOR_HOTKEY=${VALIDATOR_HOTKEY:-default}

# Build axon.external_ip parameter based on network
if [ "$network" = "local" ] && [ -n "$external_ip" ]; then
    axon_external_ip_param="--axon.external_ip $external_ip"
else
    axon_external_ip_param=""
fi

NEURON_LOGGING_LEVEL=${NEURON_LOGGING_LEVEL:-info}
logging_param="--logging.$NEURON_LOGGING_LEVEL"

echo "Running validator python -m neurons.validator --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $VALIDATOR_WALLET --wallet.hotkey $VALIDATOR_HOTKEY --axon.port $port $axon_external_ip_param $logging_param"
python -m neurons.validator --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $VALIDATOR_WALLET --wallet.hotkey $VALIDATOR_HOTKEY --axon.port $port $axon_external_ip_param $logging_param #--neuron.epoch_length 101