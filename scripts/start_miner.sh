#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
MINER_PORT=${MINER_PORT:-8091}
port=${1:-$MINER_PORT}

# Set miner wallet with fallback chain: $2 -> MINER_WALLET -> WALLET_NAME -> miner
MINER_WALLET=${2:-$MINER_WALLET}
MINER_WALLET=${MINER_WALLET:-$WALLET_NAME}
MINER_WALLET=${MINER_WALLET:-miner}

# Set miner hotkey with fallback chain: MINER_HOTKEY -> HOTKEY_NAME -> default
MINER_HOTKEY=${MINER_HOTKEY:-$HOTKEY_NAME}
MINER_HOTKEY=${MINER_HOTKEY:-default}

# Build axon.external_ip parameter based on network
if [ "$network" = "local" ] && [ -n "$external_ip" ]; then
    axon_external_ip_param="--axon.external_ip $external_ip"
else
    axon_external_ip_param=""
fi

NEURON_LOGGING_LEVEL=${NEURON_LOGGING_LEVEL:-info}
logging_param="--logging.$NEURON_LOGGING_LEVEL"

# Blacklist configuration - allow validators to access miners
# Set to true to only allow validators, false to allow all registered entities
BLACKLIST_FORCE_VALIDATOR_PERMIT=${BLACKLIST_FORCE_VALIDATOR_PERMIT:-false}
BLACKLIST_ALLOW_NON_REGISTERED=${BLACKLIST_ALLOW_NON_REGISTERED:-false}

blacklist_params=""
if [ "$BLACKLIST_FORCE_VALIDATOR_PERMIT" = "true" ]; then
    blacklist_params="$blacklist_params --blacklist.force_validator_permit"
fi
if [ "$BLACKLIST_ALLOW_NON_REGISTERED" = "true" ]; then
    blacklist_params="$blacklist_params --blacklist.allow_non_registered"
fi

echo "Running miner python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $MINER_WALLET --wallet.hotkey $MINER_HOTKEY  --axon.port $port $axon_external_ip_param $logging_param $blacklist_params"
python -m neurons.miner --netuid $netuid --subtensor.chain_endpoint $chain_endpoint --subtensor.network $network --wallet.name $MINER_WALLET --wallet.hotkey $MINER_HOTKEY  --axon.port $port $axon_external_ip_param $logging_param $blacklist_params