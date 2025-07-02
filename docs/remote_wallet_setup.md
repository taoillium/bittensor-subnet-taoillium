# Wallet Service Architecture (TODO)

## Overview

This architecture separates transaction operations from miner and validator nodes in Bittensor, creating a centralized wallet service that handles all blockchain transactions while keeping nodes focused on their core business logic.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Miner Node    │    │  Wallet Service │    │   Blockchain    │
│                 │    │                 │    │                 │
│ - Process req   │◄──►│ - Store keys    │◄──►│ - Execute txns  │
│ - Return resp   │    │ - Sign txns     │    │ - Submit txns   │
│ - No private    │    │ - Secure env    │    │                 │
│   keys          │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       ▲                       │
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                    Validator Node
                    - No private keys
                    - API calls to wallet service
```

## Benefits

1. **Security**: Private keys are only stored on the wallet service
2. **Separation of Concerns**: Nodes focus on business logic, wallet service handles transactions
3. **Centralized Management**: All blockchain operations are managed from one place
4. **Scalability**: Multiple nodes can share the same wallet service
5. **Monitoring**: Centralized transaction operations facilitate auditing and monitoring

## Deployment Methods

### Method 1: Docker Compose (Recommended)

1. **Set Environment Variables**:
```bash
export network="local"  # or "test", "finney"
export netuid=2
export chain_endpoint="ws://127.0.0.1:9944"
export WALLET_SERVICE_URL="http://localhost:8000"
```

2. **Start All Services**:
```bash
docker-compose up -d
```

3. **View Logs**:
```bash
docker-compose logs -f wallet-service
docker-compose logs -f miner
docker-compose logs -f validator
```

### Method 2: Manual Deployment

1. **Start Wallet Service**:
```bash
# Set environment variables
export WALLET_SERVICE_URL="http://localhost:8000"

# Start service
./scripts/start_manage.sh
```

2. **Start Miner**:
```bash
# Set environment variables
export WALLET_SERVICE_URL="http://localhost:8000"

# Start miner
./scripts/start_miner.sh
```

3. **Start Validator**:
```bash
# Set environment variables
export WALLET_SERVICE_URL="http://localhost:8000"

# Start validator
./scripts/start_validator.sh
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WALLET_SERVICE_URL` | Wallet service address | `http://localhost:8000` |
| `WALLET_SERVICE_TOKEN` | Wallet service auth token | `default-token` |

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--wallet.service_url` | Wallet service URL | `http://localhost:8000` |
| `--wallet.service_token` | Wallet service auth token | `your-token` |

## API Endpoints

### Set Weights
```bash
POST /wallet/set_weights
Authorization: Bearer your-token
Content-Type: application/json

{
    "wallet_name": "validator",
    "hotkey_name": "default",
    "transaction_data": {
        "netuid": 2,
        "uids": [1, 2, 3],
        "weights": [100, 200, 300],
        "version_key": 1,
        "wait_for_finalization": false,
        "wait_for_inclusion": false
    }
}
```

## Security Recommendations

1. **Network Isolation**: Deploy the wallet service in an isolated network
2. **HTTPS**: Use HTTPS in production environments
3. **Firewall**: Restrict access to the wallet service
4. **Authentication**: Implement proper authentication for wallet service
5. **Monitoring**: Monitor all transaction operations
6. **Backup**: Regularly backup wallet files

## Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Check if the wallet service is running
   - Check network connectivity
   - Verify the service URL is correct

2. **Authentication Failed**:
   - Check if the authentication token is correct
   - Verify the token has proper permissions

3. **Transaction Failed**:
   - Check if wallet files exist
   - Check permission settings

4. **Fallback to Local Wallet**:
   - If the wallet service is unavailable, the system will automatically fall back to the local wallet (if available)
   - Check logs to confirm fallback status

### Viewing Logs

```bash
# View wallet service logs
docker-compose logs wallet-service

# View miner logs
docker-compose logs miner

# View validator logs
docker-compose logs validator
```

## Migration from Remote Wallet Service

If you're migrating from the previous remote wallet service:

1. **Update Environment Variables**:
   - Replace `WALLET_SERVICE_URL` with `WALLET_SERVICE_URL`
   - Add `WALLET_SERVICE_TOKEN` for authentication

2. **Update Command Line Arguments**:
   - Replace `--wallet.service_url` with `--wallet.service_url`
   - Add `--wallet.service_token` for authentication

3. **Update API Calls**:
   - Use `/wallet/set_weights` for direct transaction execution
