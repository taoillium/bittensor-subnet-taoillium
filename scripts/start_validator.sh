#!/bin/bash
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

curl --silent --fail --max-time 2 http://127.0.0.1:9944
rc=$?
if [ $rc -eq 7 ]; then
    echo "Error: ws://127.0.0.1:9944 is not running, please start the local chain (subtensor localnet)"
    echo "Please run the following command to start the local chain:"
    echo "cd ../subtensor && BUILD_BINARY=1 ./scripts/localnet.sh --no-purge"
    exit 1
fi

echo "Running validator"
python -m neurons.validator --netuid 2 --subtensor.chain_endpoint ws://127.0.0.1:9944 --subtensor.network local --wallet.name validator --wallet.hotkey default --logging.debug #--neuron.epoch_length 101