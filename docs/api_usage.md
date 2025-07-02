# Taoillium Subnet API Usage Guide

This document explains the different ways to interact with the Taoillium subnet API and provides recommendations for different use cases.

## Overview

There are two main approaches to interact with the Taoillium subnet:

1. **Validator HTTP Server** (Current Implementation)
2. **Standardized SubnetsAPI** (Recommended for External Clients)

## 1. Validator HTTP Server (Current)

The validator currently runs an embedded HTTP server that provides direct access to the subnet.

### Usage

```python
import requests
import json

# Endpoint
url = "http://localhost:8080/task/receive"

# Headers (authentication required)
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

# Request data
data = {
    "task": "example_task",
    "input": "Hello, subnet!"
}

# Make request
response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result)
```

### Pros
- ✅ Simple and direct
- ✅ No additional setup required
- ✅ Immediate access to validator functionality

### Cons
- ❌ Coupled to validator process
- ❌ Single point of failure
- ❌ Limited scalability
- ❌ Resource competition with validator

## 2. Standardized SubnetsAPI (Recommended)

The `TaoilliumAPI` class provides a standardized interface following Bittensor's `SubnetsAPI` pattern.

### Direct Usage

```python
import asyncio
import bittensor as bt
from template.api import TaoilliumAPI

async def main():
    # Initialize wallet
    wallet = bt.wallet()
    
    # Create API client
    api_client = TaoilliumAPI(wallet=wallet, netuid=33)
    
    # Query the network
    user_input = {
        "task": "example_task",
        "data": "Hello, subnet!"
    }
    
    responses = await api_client.query_network(
        user_input=user_input,
        sample_size=3,
        timeout=30
    )
    
    print(f"Received {len(responses)} responses:")
    for response in responses:
        print(response)

# Run
asyncio.run(main())
```

### Independent HTTP Server

We also provide an independent HTTP API server that uses `TaoilliumAPI` as the backend:

```bash
# Start the API server
python api_server.py
```

#### Available Endpoints

1. **`/task/receive`** - Equivalent to validator.py endpoint (requires authentication)
2. **`/query/public`** - Public query endpoint (no authentication)
3. **`/query`** - Authenticated query endpoint
4. **`/health`** - Health check endpoint
5. **`/token`** - Get access token

#### Using /task/receive (Validator-compatible)

This endpoint behaves exactly like the validator.py `/task/receive` endpoint:

```python
import requests
import json

# Get access token
token_response = requests.get("http://localhost:8000/token")
token = token_response.json()["token"]

# Headers with authentication
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Request data (same format as validator.py expects)
data = {
    "task": "example_task",
    "input": "Hello, subnet!",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 100
    }
}

# Make request to /task/receive
response = requests.post(
    "http://localhost:8000/task/receive",
    headers=headers,
    json=data
)

result = response.json()
print(result)  # Returns list of responses (same as validator.py)
```

#### Using /query/public (Simplified)

For simpler use cases without authentication:

```python
import requests
import json

# Public endpoint (no authentication)
url = "http://localhost:8000/query/public"

data = {
    "input": {
        "task": "example_task",
        "data": "Hello, subnet!"
    },
    "sample_size": 3,
    "timeout": 30
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### Pros
- ✅ Standardized Bittensor interface
- ✅ Decoupled from validator
- ✅ Better error handling and retry logic
- ✅ Scalable and extensible
- ✅ Can be deployed independently
- ✅ Supports load balancing

### Cons
- ❌ Requires additional setup
- ❌ More complex initial configuration

## 3. Migration Strategy

### Phase 1: Keep Both (Current)
- Maintain the current validator HTTP server for backward compatibility
- Add the new `TaoilliumAPI` for new clients

### Phase 2: Gradual Migration
- Encourage new clients to use `TaoilliumAPI`
- Provide migration guides for existing clients
- Monitor usage patterns

### Phase 3: Deprecation
- Deprecate the validator HTTP server
- Provide clear migration timeline
- Eventually remove the embedded server

## 4. Configuration

### Environment Variables

```bash
# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Subnet Configuration
CHAIN_NETUID=2

# Validator HTTP Server (legacy)
VALIDATOR_HOST=127.0.0.1
VALIDATOR_API_PORT=8080
```

### Example .env file

```env
# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Subnet
CHAIN_NETUID=2

# Legacy Validator Server
VALIDATOR_HOST=127.0.0.1
VALIDATOR_API_PORT=8080

# Security
NEURON_JWT_SECRET_KEY=your-secret-key
NEURON_JWT_EXPIRE_IN=30
```

## 5. Best Practices

### For New Projects
1. Use `TaoilliumAPI` directly in your Python applications
2. Use the independent HTTP server for web applications
3. Implement proper error handling and retry logic
4. Use appropriate timeouts and sample sizes

### For Existing Projects
1. Start with the independent HTTP server for easy migration
2. Gradually migrate to direct `TaoilliumAPI` usage
3. Test thoroughly before switching
4. Maintain backward compatibility during transition

### Security Considerations
1. Use authentication for sensitive operations
2. Implement rate limiting
3. Validate input data
4. Use HTTPS in production
5. Regularly rotate JWT secrets

## 6. Examples

See the following example files:
- `examples/api_client_example.py` - Direct API usage
- `api_server.py` - Independent HTTP server
- `neurons/validator.py` - Current embedded server

## 7. Troubleshooting

### Common Issues

1. **Connection refused**: Check if the server is running and port is correct
2. **Authentication failed**: Verify JWT token is valid and not expired
3. **No responses**: Check network connectivity and node availability
4. **Timeout errors**: Increase timeout or reduce sample size

### Debug Mode

Enable debug logging:

```python
import bittensor as bt
bt.logging.set_config(level="DEBUG")
```

## 8. Performance Considerations

### Optimizations
1. Use connection pooling for HTTP clients
2. Implement caching for frequently requested data
3. Use async/await for concurrent operations
4. Monitor and adjust sample sizes based on network conditions

### Monitoring
1. Track response times
2. Monitor success rates
3. Log error patterns
4. Set up alerts for service degradation 