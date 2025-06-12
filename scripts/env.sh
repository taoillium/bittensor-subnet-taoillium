#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "$CURRENT_DIR"
cd $CURRENT_DIR/../

if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        if which uv > /dev/null; then
            uv venv
            source .venv/bin/activate
        elif which python3 > /dev/null; then
            python3 -m venv .venv
            source .venv/bin/activate
        else
            echo "No virtual environment found, please install uv or python3"
            exit 1
        fi
    fi
fi

# Install btcli
if ! command -v btcli &> /dev/null; then
    echo "Installing btcli..."
    if which uv > /dev/null; then
        uv pip install -U bittensor-cli
    else
        python -m pip install -U bittensor-cli
    fi
else
    echo "btcli already installed"
fi

# read env variables from .env file
if [ -f "${CURRENT_DIR}/../.env" ]; then
    source "${CURRENT_DIR}/../.env"
else
    echo "# .env file not found"
fi

network=${CHAIN_NETWORK:-local}
default_chain_endpoint=ws://127.0.0.1:9944
if [ "$network" == "finney" ]; then
    default_chain_endpoint=wss://entrypoint-finney.opentensor.ai
elif [ "$network" == "test" ]; then
    default_chain_endpoint=wss://test.finney.opentensor.ai
fi

chain_endpoint=${CHAIN_ENDPOINT:-$default_chain_endpoint}
http_endpoint=$(echo "$chain_endpoint" | sed -e 's/^ws:\/\//http:\/\//' -e 's/^wss:\/\//https:\/\//')

netuid=${CHAIN_NETUID:-2}
echo "network: $network"
echo "netuid: $netuid"
echo "chain_endpoint: $chain_endpoint"
echo "http_endpoint: $http_endpoint"

## check localnet
# next steps need to check if the localnet is running
if [ "$network" == "local" ]; then
    curl --silent --fail --max-time 2 $http_endpoint
    rc=$?
    if [ $rc -eq 7 ]; then
        echo "Error: $http_endpoint is not running, please start the local chain (subtensor localnet)"
        echo "Please run the following command to start the local chain:"
        echo "cd ../subtensor && BUILD_BINARY=1 ./scripts/localnet.sh --no-purge"
        exit 1
    fi
fi

cd $CURRENT_DIR