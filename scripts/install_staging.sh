#!/bin/bash

trap 'echo "\nScript interrupted, exiting..."; exit 1' INT

# Test/Run
# This section is for running and testing the setup.

# Create a coldkey for the owner role
wallet=${1:-owner}

# Logic for setting up and running the environment
setup_environment() {
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ ! -d "venv" ]; then
            python -m venv venv
        fi
        source venv/bin/activate
    fi

    # Install btcli
    if ! command -v btcli &> /dev/null; then
        echo "Installing btcli..."
        python -m pip install -U bittensor-cli
    fi

    # Install the bittensor-subnet-taoillium python package
    python -m pip install -e .

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

## check localnet
# next steps need to check if the localnet is running
curl --silent --fail --max-time 2 http://127.0.0.1:9944
rc=$?
if [ $rc -eq 7 ]; then
    echo "Error: ws://127.0.0.1:9944 is not running, please start the local chain (subtensor localnet)"
    echo "Please run the following command to start the local chain:"
    echo "cd ../subtensor && BUILD_BINARY=1 ./scripts/localnet.sh --no-purge"
    exit 1
fi

balance=$(btcli wallet overview --wallet.name $wallet --subtensor.chain_endpoint ws://127.0.0.1:9944 2>/dev/null | grep -i 'Wallet balance:' | grep -Eo '[0-9]+([.][0-9]+)?' | head -n1)
if (( $(echo "$balance < 2111" | bc -l) )); then
    echo "Error: $wallet wallet balance is less than 1111, current balance is $balance"
    exit 1
fi

echo "Creating subnet for $wallet"
btcli subnet create --wallet.name $wallet --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9944

# Transfer tokens to miner and validator coldkeys
export BT_MINER_TOKEN_WALLET=$(sed -nE 's/.*"ss58Address": ?"([^"]+)".*/\1/p' ~/.bittensor/wallets/miner/coldkeypub.txt)
export BT_VALIDATOR_TOKEN_WALLET=$(sed -nE 's/.*"ss58Address": ?"([^"]+)".*/\1/p' ~/.bittensor/wallets/validator/coldkeypub.txt)

echo "Transferring tokens to miner"
btcli wallet transfer --subtensor.network ws://127.0.0.1:9944 --wallet.name $wallet --dest $BT_MINER_TOKEN_WALLET --amount 11

echo "Transferring tokens to validator"
btcli wallet transfer --subtensor.network ws://127.0.0.1:9944 --wallet.name $wallet --dest $BT_VALIDATOR_TOKEN_WALLET --amount 1100


echo "Registering validator to subnet"
btcli subnet register --wallet.name validator --netuid 2 --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9944

# Register wallet hotkeys to subnet
echo "Registering miner to subnet"
btcli subnet register --wallet.name miner --netuid 2 --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9944


echo "Adding stake to the validator"
btcli stake add --wallet.name validator --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9944 --amount 10 --partial

echo "Adding stake to the miner"
btcli stake add --wallet.name miner --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9944 --amount 2 --partial

# Ensure both the miner and validator keys are successfully registered.
echo "Listing subnets"
btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9944


echo "Checking validator wallet"
btcli wallet overview --wallet.name validator --subtensor.chain_endpoint ws://127.0.0.1:9944

echo "Checking miner wallet"
btcli wallet overview --wallet.name miner --subtensor.chain_endpoint ws://127.0.0.1:9944
