#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

if [ "$network" != "local" ]; then
    echo "Non-local network detected, skipping installation"
    exit 0
fi

trap 'echo "\nScript interrupted, exiting..."; exit 1' INT

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

# Test/Run
# This section is for running and testing the setup.

# Create a coldkey for the owner role
wallet=${1:-owner}

cd $CURRENT_DIR/../

# Logic for setting up and running the environment
setup_environment() {
    # Install the bittensor-subnet-taoillium python package
    if which uv > /dev/null; then
        uv pip install -e .
    else
        python -m pip install -e .
    fi

    # Create and set up wallets
    if ! btcli wallet inspect --wallet.name $wallet &> /dev/null; then
        echo "Creating coldkey and hotkey for $wallet"
        btcli wallet new_coldkey --wallet.name $wallet
        btcli wallet new_hotkey --wallet.name $wallet
    fi

    for name in miner validator; do
        if ! btcli wallet inspect --wallet.name $name &> /dev/null; then
            echo "Creating coldkey and hotkey for $name"
            btcli wallet new_coldkey --wallet.name $name
            btcli wallet new_hotkey --wallet.name $name
        fi
    done

}

# Call setup_environment every time
setup_environment 

balance=$(btcli wallet balance --wallet.name $wallet --subtensor.chain_endpoint ${chain_endpoint} --json-output | jq -r ".balances.$wallet.free")
echo "balance: $balance"
if [[ -z "$balance" || "$balance" == "null" ]]; then
    echo "Error: Could not determine wallet balance."
    exit 1
fi
if (( $(echo "$balance < 2111" | bc -l) )); then
    echo "Error: $wallet wallet balance is less than 1111, current balance is $balance"
    exit 1
fi


echo "Creating subnet for $wallet"
btcli subnet create --wallet.name $wallet --wallet.hotkey default --subtensor.chain_endpoint ${chain_endpoint}

# Transfer tokens to miner and validator coldkeys
export BT_MINER_TOKEN_WALLET=$(sed -nE 's/.*"ss58Address": ?"([^"]+)".*/\1/p' ~/.bittensor/wallets/miner/coldkeypub.txt)
export BT_VALIDATOR_TOKEN_WALLET=$(sed -nE 's/.*"ss58Address": ?"([^"]+)".*/\1/p' ~/.bittensor/wallets/validator/coldkeypub.txt)

echo "Transferring tokens to miner"
btcli wallet transfer --subtensor.network ${chain_endpoint} --wallet.name $wallet --dest $BT_MINER_TOKEN_WALLET --amount 11

echo "Transferring tokens to validator"
btcli wallet transfer --subtensor.network ${chain_endpoint} --wallet.name $wallet --dest $BT_VALIDATOR_TOKEN_WALLET --amount 1100


echo "Registering validator to subnet"
btcli subnet register --wallet.name validator --netuid $netuid --wallet.hotkey default --subtensor.chain_endpoint ${chain_endpoint}

# Register wallet hotkeys to subnet
echo "Registering miner to subnet"
btcli subnet register --wallet.name miner --netuid $netuid --wallet.hotkey default --subtensor.chain_endpoint ${chain_endpoint}


echo "Adding stake to the validator"
btcli stake add --wallet.name validator --wallet.hotkey default --subtensor.chain_endpoint ${chain_endpoint} --amount 10 --partial

echo "Adding stake to the miner"
btcli stake add --wallet.name miner --wallet.hotkey default --subtensor.chain_endpoint ${chain_endpoint} --amount 2 --partial

echo "Start subnet"
btcli subnet start --wallet.name owner --netuid $netuid --subtensor.chain_endpoint ${chain_endpoint}

# Ensure both the miner and validator keys are successfully registered.
echo "Listing subnets"
btcli subnet list --subtensor.chain_endpoint ${chain_endpoint}


echo "Checking validator wallet"
btcli wallet overview --wallet.name validator --subtensor.chain_endpoint ${chain_endpoint}

echo "Checking miner wallet"
btcli wallet overview --wallet.name miner --subtensor.chain_endpoint ${chain_endpoint}
