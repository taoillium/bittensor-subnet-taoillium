# Subnet Manager API

The `manage` directory contains a FastAPI-based management server for the Taoillium Subnet. This server provides a RESTful API for wallet management and subnet interactions, with built-in authentication and comprehensive logging.

## Overview

The Subnet Manager is a unified server that provides:
- **Wallet Management**: Sign messages, verify signatures, and manage Bittensor wallets
- **Subnet API**: Query the subnet network, receive tasks, and monitor subnet health
- **Authentication**: JWT-based authentication middleware for secure access
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Directory Structure

```
manage/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application entry point
├── router/                  # API route handlers
│   ├── __init__.py         # Router package initialization
│   ├── wallet.py           # Wallet management endpoints
│   └── subnet.py           # Subnet interaction endpoints
├── middlewares/            # Custom middleware components
│   ├── __init__.py         # Middleware package initialization
│   └── auth.py             # Authentication middleware
└── README.md               # This file
```

## Features

### 🔐 Authentication
- JWT-based authentication using Bearer tokens
- Middleware-based authentication for all protected endpoints
- Public endpoints: `/docs`, `/openapi.json`, `/`, `/health`, `/subnet/status`

### 💼 Wallet Management (`/wallet/*`)
- **Sign Messages**: Sign data with hotkey or coldkey
- **Verify Signatures**: Verify message signatures
- **Wallet Information**: Get wallet status and public addresses
- **Transaction Management**: Sign and submit transactions
- **Weight Management**: Set neuron weights

### 🌐 Subnet API (`/subnet/*`)
- **Network Queries**: Query the subnet network with custom inputs
- **Task Reception**: Receive and process tasks from the network
- **Health Monitoring**: Check subnet and network health
- **Status Information**: Get detailed subnet status and metagraph information

## API Endpoints

### Public Endpoints
- `GET /` - Root endpoint with version information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /openapi.json` - OpenAPI specification
- `GET /subnet/status` - Public subnet status

### Wallet Endpoints (Protected)
- `POST /wallet/sign` - Sign messages with wallet keys
- `POST /wallet/verify` - Verify message signatures
- `GET /wallet/info` - Get wallet information and addresses

### Subnet Endpoints (Protected)
- `POST /subnet/query` - Query the subnet network
- `POST /subnet/task/receive` - Receive and process tasks
- `GET /subnet/health` - Detailed subnet health check

## Configuration

The server uses configuration from `services.config.settings`:

```python
# Server Configuration
MANAGER_HOST = "0.0.0.0"
MANAGER_PORT = 8000
MANAGER_DEBUG = "INFO"
MANAGER_RELOAD = False

# Wallet Configuration
WALLET_NAME = "default"
HOTKEY_NAME = "default"
WALLET_PASSWORD = "your-wallet-password"

# Network Configuration
CHAIN_NETWORK = "finney"
CHAIN_NETUID = 1
CHAIN_ENDPOINT = "ws://127.0.0.1:9944"
```

## Usage

### Starting the Server

```bash
# Run directly
python manage/main.py

# Or using uvicorn
uvicorn manage.main:app --host 0.0.0.0 --port 8000
```

### Example API Calls

#### Sign a Message
```bash
curl -X POST "http://localhost:8000/wallet/sign" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_name": "my_wallet",
    "hotkey_name": "default",
    "message": "Hello, Bittensor!",
    "message_type": "general"
  }'
```

#### Query the Subnet
```bash
curl -X POST "http://localhost:8000/subnet/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"prompt": "What is Bittensor?"},
    "sample_size": 3,
    "timeout": 30
  }'
```

#### Check Health
```bash
curl "http://localhost:8000/health"
```

## Security

### Authentication
- All endpoints (except public ones) require Bearer token authentication
- Tokens are verified using `services.security.verify_manage_token()`
- Invalid or missing tokens return 401 Unauthorized

### CORS
- CORS is enabled for all origins (`*`)
- Allows all methods and headers
- Supports credentials

## Logging

The server uses structured logging with configurable levels:
- **DEBUG**: Detailed debug information
- **INFO**: General operational information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical error messages

Log level is controlled by `MANAGER_DEBUG` setting.

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Bittensor**: Core Bittensor library for wallet and network operations
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for running the FastAPI application

## Development

### Adding New Endpoints
1. Create new route handlers in the appropriate router file
2. Add Pydantic models for request/response validation
3. Include proper error handling and logging
4. Update this README with new endpoint documentation

### Testing
- Use the interactive API documentation at `/docs`
- Test endpoints with proper authentication tokens
- Verify error handling with invalid inputs

## Troubleshooting

### Common Issues

1. **Wallet Loading Errors**
   - Ensure wallet files exist in `~/.bittensor/wallets/`
   - Check wallet password configuration
   - Verify wallet and hotkey names

2. **Network Connection Issues**
   - Verify chain endpoint configuration
   - Check network connectivity
   - Ensure proper netuid configuration

3. **Authentication Errors**
   - Verify token format (Bearer <token>)
   - Check token validity and expiration
   - Ensure proper role permissions

### Debug Mode
Enable debug logging by setting `MANAGER_DEBUG = "DEBUG"` in your configuration.

## License

This project is licensed under the MIT License. See the license headers in individual files for details. 