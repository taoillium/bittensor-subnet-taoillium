# Environment Variables Documentation

This document provides comprehensive documentation for all environment variables used in the Bittensor Subnet Taoillium project.

## Overview

Environment variables are configured through a `.env` file in the project root directory. The configuration is managed by `services/config.py` using Pydantic Settings.

## Core Environment Variables

### 🔑 **Authentication & API Configuration**

#### `SRV_API_KEY`
- **Description**: Authentication token for Taoillium.ai API services
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Source**: Register at [taoillium.ai](https://taoillium.ai) to obtain
- **Expiration**: 30 minutes (default)
- **Important**: **Obtain and set this token before starting nodes to ensure proper authentication**
- **Usage**: Used by both MinerClient and ValidatorClient for API authentication

#### `SRV_API_URL`
- **Description**: Base URL for Taoillium.ai API services
- **Type**: String
- **Required**: Yes
- **Default**: https://api.taoillium.ai
- **Usage**: Base endpoint for all API interactions

#### `DETECT_IP`
- **Description**: IP address used for local IP detection
- **Type**: String
- **Required**: No
- **Default**: "8.8.8.8"
- **Usage**: Used by `get_local_ip()` function to determine external IP

### 🔐 **JWT Authentication**

#### `NEURON_JWT_SECRET_KEY`
- **Description**: Secret key for JWT token generation and validation
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Usage**: Used for secure authentication between services

#### `NEURON_JWT_EXPIRE_IN`
- **Description**: JWT token expiration time in minutes
- **Type**: Integer
- **Required**: No
- **Default**: 30
- **Usage**: Controls how long JWT tokens remain valid

#### `NEURON_JWT_ALGORITHM`
- **Description**: Algorithm used for JWT token signing
- **Type**: String
- **Required**: No
- **Default**: "HS256"
- **Usage**: Specifies the cryptographic algorithm for JWT

### 🌐 **Network Configuration**

#### `CHAIN_NETWORK`
- **Description**: Bittensor network type
- **Type**: String
- **Required**: No
- **Default**: "local"
- **Options**: "local", "test", "finney"
- **Usage**: Determines which Bittensor network to connect to

#### `CHAIN_ENDPOINT`
- **Description**: Bittensor chain endpoint URL
- **Type**: String
- **Required**: No
- **Default**: Auto-configured based on CHAIN_NETWORK
- **Auto-defaults**:
  - `local`: "ws://127.0.0.1:9944"
  - `finney`: "wss://entrypoint-finney.opentensor.ai"
  - `test`: "wss://test.finney.opentensor.ai"
- **Usage**: WebSocket endpoint for blockchain communication

#### `CHAIN_NETUID`
- **Description**: Subnet UID (Unique Identifier)
- **Type**: Integer
- **Required**: No
- **Default**: 2
- **Usage**: Identifies which subnet to participate in

### 👛 **Wallet Configuration**

#### `WALLET_NAME`
- **Description**: Name of the Bittensor wallet to use
- **Type**: String
- **Required**: No
- **Default**: "validator"
- **Usage**: Specifies which wallet to use for node operations

#### `HOTKEY_NAME`
- **Description**: Name of the hotkey within the wallet
- **Type**: String
- **Required**: No
- **Default**: "default"
- **Usage**: Specifies which hotkey to use for signing operations

### ⚙️ **Service Configuration**

#### `VALIDATOR_SLEEP_TIME`
- **Description**: Sleep time between validator operations in seconds
- **Type**: Integer
- **Required**: No
- **Default**: 1
- **Usage**: Controls validator polling frequency

### 🏗️ **Manager Service Configuration**

#### `MANAGER_HOST`
- **Description**: Host address for the management API server
- **Type**: String
- **Required**: No
- **Default**: "0.0.0.0"
- **Usage**: Binding address for the FastAPI management server

#### `MANAGER_PORT`
- **Description**: Port for the management API server
- **Type**: Integer
- **Required**: No
- **Default**: 8000
- **Usage**: Port number for the management API

#### `MANAGER_DEBUG`
- **Description**: Logging level for the management server
- **Type**: String
- **Required**: No
- **Default**: "INFO"
- **Usage**: Controls logging verbosity

#### `MANAGER_RELOAD`
- **Description**: Enable auto-reload for development
- **Type**: Boolean
- **Required**: No
- **Default**: false
- **Usage**: Enables hot reloading during development

#### `MANAGER_JWT_SECRET_KEY`
- **Description**: Secret key for manager JWT authentication
- **Type**: String
- **Required**: No
- **Default**: "your-secret-api-key"
- **Usage**: JWT secret for manager API authentication

#### `MANAGER_JWT_EXPIRE_IN`
- **Description**: Manager JWT token expiration time in minutes
- **Type**: Integer
- **Required**: No
- **Default**: 30
- **Usage**: Controls manager JWT token validity

#### `MANAGER_JWT_ALGORITHM`
- **Description**: Algorithm for manager JWT token signing
- **Type**: String
- **Required**: No
- **Default**: "HS256"
- **Usage**: Cryptographic algorithm for manager JWT

### 🐳 **Docker Service Configuration**

#### `MINER_PORT`
- **Description**: Port for the miner service
- **Type**: Integer
- **Required**: No
- **Default**: 8091
- **Usage**: Port for miner service communication

#### `VALIDATOR_PORT`
- **Description**: Port for the validator service
- **Type**: Integer
- **Required**: No
- **Default**: 8092
- **Usage**: Port for validator service communication

#### `MINER_NAME`
- **Description**: Name identifier for the miner instance
- **Type**: String
- **Required**: No
- **Default**: Auto-configured from directory name
- **Usage**: Unique identifier for miner instances

#### `VALIDATOR_NAME`
- **Description**: Name identifier for the validator instance
- **Type**: String
- **Required**: No
- **Default**: Auto-configured from directory name
- **Usage**: Unique identifier for validator instances

## Example .env File

```bash
# Authentication & API Configuration
SRV_API_KEY=your_taoillium_api_key_here
SRV_API_URL=https://api.taoillium.ai
DETECT_IP=8.8.8.8

# JWT Authentication
NEURON_JWT_SECRET_KEY=your_jwt_secret_key_here
NEURON_JWT_EXPIRE_IN=30
NEURON_JWT_ALGORITHM=HS256

# Network Configuration
CHAIN_NETWORK=local
CHAIN_ENDPOINT=ws://127.0.0.1:9944
CHAIN_NETUID=2

# Wallet Configuration
WALLET_NAME=validator
HOTKEY_NAME=default

# Service Configuration
VALIDATOR_SLEEP_TIME=1

# Manager Service Configuration
MANAGER_HOST=0.0.0.0
MANAGER_PORT=8000
MANAGER_DEBUG=INFO
MANAGER_RELOAD=false
MANAGER_JWT_SECRET_KEY=your-manager-secret-key
MANAGER_JWT_EXPIRE_IN=30
MANAGER_JWT_ALGORITHM=HS256

# Docker Service Configuration
MINER_PORT=8091
VALIDATOR_PORT=8092
MINER_NAME=my-miner
VALIDATOR_NAME=my-validator
```

## Important Notes

### SRV_API_KEY Requirements
1. **Registration Required**: You must register at [taoillium.ai](https://taoillium.ai) to obtain an API key
2. **Token Expiration**: The default expiration time is 30 minutes
3. **Pre-launch Setup**: **It is recommended to obtain and set this token before starting any nodes**
4. **Authentication**: This token is used for all API interactions with Taoillium services

### Network Configuration
- For **local development**: Use `CHAIN_NETWORK=local`
- For **testnet**: Use `CHAIN_NETWORK=test`
- For **mainnet**: Use `CHAIN_NETWORK=finney`

### Security Considerations
- Keep JWT secret keys secure and unique
- Never commit API keys to version control
- Use strong, unique passwords for wallet operations
- Regularly rotate authentication tokens

## Troubleshooting

### Common Issues
1. **Missing SRV_API_KEY**: Ensure you have registered at taoillium.ai and obtained a valid API key
2. **Token Expired**: Re-authenticate and obtain a new token if the current one has expired
3. **Network Connection**: Verify CHAIN_ENDPOINT is accessible and correct for your network
4. **Port Conflicts**: Ensure MINER_PORT and VALIDATOR_PORT are not in use by other services

### Validation
The configuration is validated by Pydantic Settings, which will raise clear error messages for invalid configurations. 