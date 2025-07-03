# Network Configuration Guide

## Current Issue
Your system is connecting to a local chain (`ws://192.168.110.90:9944`) but the metagraph contains axons from a public network (`203.175.14.45`, `119.237.255.203`, etc.).

## Solutions

### Option 1: Connect to Public Network (Recommended)
To connect to the network where those axons actually exist:

```bash
# Set these environment variables
export CHAIN_NETWORK=test
export CHAIN_ENDPOINT=wss://test.finney.opentensor.ai
export CHAIN_NETUID=2
```

Or create/update your `.env` file:
```env
CHAIN_NETWORK=test
CHAIN_ENDPOINT=wss://test.finney.opentensor.ai
CHAIN_NETUID=2
WALLET_NAME=validator
HOTKEY_NAME=default
```

### Option 2: Use Local Network with Local Nodes
If you want to use a local network, you need to:

1. **Run a local subtensor node** on `192.168.110.90:9944`
2. **Register local miners/validators** on that network
3. **Ensure the metagraph is populated** with local axons

### Option 3: Use Finney Mainnet
For production use:
```env
CHAIN_NETWORK=finney
CHAIN_ENDPOINT=wss://entrypoint-finney.opentensor.ai
CHAIN_NETUID=2
```

## Testing the Fix

After updating your configuration:

1. **Restart your application**
2. **Run the debug script:**
   ```bash
   python debug_metagraph.py
   ```
3. **Check that axon IPs match your network**

## Expected Results

- **For public network:** Axon IPs should be public IPs and connections should work
- **For local network:** Axon IPs should be local IPs (like `192.168.x.x`)

## Troubleshooting

If connections still fail after switching networks:

1. **Check firewall settings** - ensure outbound connections are allowed
2. **Verify network connectivity** - try pinging the axon IPs manually
3. **Check if nodes are actually running** - the metagraph might contain stale data
4. **Try different timeout values** - some networks are slower 