# Token Refresh Design Documentation

## Overview

This document describes the dual token refresh mechanism implemented in the Bittensor subnet neurons (validators and miners) to maintain continuous authentication with the business server.

## Solution: Dual Token Refresh System

### Design Principles

1. **Dual Authentication**: Two separate token refresh mechanisms for different purposes
2. **Proactive Refresh**: Refresh tokens 5 minutes before expiration to ensure continuous operation
3. **Minimal Overhead**: Only refresh when necessary, not on every sync cycle
4. **Consistent Behavior**: Same logic for both validators and miners
5. **Graceful Degradation**: System continues to work even if refresh fails

### Implementation Details

#### 1. Token Types and Purposes

**Business Server Access (`refresh_business_server_access`)**:
- Used for neurons to register with the business server using tokens
- Endpoint: `/sapi/node/neuron/register`
- Contains neuron metadata (uid, chain, netuid, type, account) and authentication token
- Allows business server to access and communicate with neurons
- New neurons create database records, existing neurons update their tokens
- Expires after 30 minutes (configurable via `NEURON_JWT_EXPIRE_IN`)

**Service Authentication Token (`refresh_service_token`)**:
- Used for general API authentication with the service
- Endpoint: `/sapi/auth/refresh`
- Provides access token for service API calls
- Expires after server-defined time (typically 30 minutes)

#### 2. Token Refresh Tracking

See [`BaseNeuron.__init__()`](template/base/neuron.py#L69) for initialization of token expiration timestamps.

#### 3. Business Server Access Refresh

See [`BaseNeuron.refresh_business_server_access()`](template/base/neuron.py#L250) for the complete implementation.

Key functionality:
- Checks API key availability
- Validates token expiration timing
- Creates neuron registration data with authentication token
- Registers neuron with business server
- Updates expiration timestamp on success

#### 4. Service Token Refresh

See [`BaseNeuron.refresh_service_token()`](template/base/neuron.py#L285) for the complete implementation.

Key functionality:
- Checks API key availability
- Validates token expiration timing
- Refreshes service authentication token
- Updates API key and expiration timestamp on success

#### 5. Integration with Sync Cycle

See [`BaseNeuron.sync()`](template/base/neuron.py#L185) for the complete sync implementation.

Both token refresh methods are called at the end of each sync cycle:
```python
self.refresh_business_server_access()
self.refresh_service_token()
```

## Token Lifecycle and Timing

### Business Server Access Lifecycle

1. **Initial Registration**: Neuron creates authentication token and registers with business server
2. **Database Handling**: Business server creates new database record for new neurons, updates tokens for existing neurons
3. **Active Period**: Registration token valid for 30 minutes (configurable via `NEURON_JWT_EXPIRE_IN`)
4. **Refresh Window**: Token refreshed 5 minutes before expiration (25 minutes after creation)
5. **Continuous Operation**: Process repeats indefinitely, maintaining business server access capability

### Service Token Lifecycle

1. **Initial Authentication**: API key obtained from environment or initial auth
2. **Active Period**: Token valid for server-defined time (typically 30 minutes)
3. **Refresh Window**: Token refreshed 5 minutes before expiration
4. **Continuous Operation**: Process repeats indefinitely

### Sync Cycle Integration

- **Validator**: `sync()` called every epoch (typically every 100 blocks)
- **Miner**: `sync()` called periodically during operation
- **Token Refresh**: Both tokens checked on every sync cycle, but only executed when needed

## API Key Management

### Environment Variable Support

The system supports multiple API key sources:

```python
# Neuron-specific API key (preferred)
SRV_API_KEY_<hotkey_address>

# Global API key (fallback)
SRV_API_KEY
```

### API Key Tracking

See [`BaseNeuron.__init__()`](template/base/neuron.py#L95) for API key initialization and tracking.

### Graceful Shutdown

See [`BaseNeuron._signal_handler()`](template/base/neuron.py#L240) for shutdown handling and API key recording.

## Configuration

### Environment Variables

```bash
# Token expiration time in minutes
NEURON_JWT_EXPIRE_IN=30

# API key configuration
SRV_API_KEY=<global_api_key>
SRV_API_KEY_<hotkey_address>=<neuron_specific_api_key>
```

### Customization Options

1. **Refresh Buffer**: Currently hardcoded to 5 minutes, could be made configurable
2. **Refresh Strategy**: Could implement exponential backoff for failed refreshes
3. **Token Validation**: Could add token validation before refresh to avoid unnecessary calls
4. **API Key Rotation**: Could implement automatic API key rotation

## Error Handling

### Refresh Failures

If either token refresh fails:
1. Log the error for debugging
2. Continue operation with existing token
3. Retry on next sync cycle
4. System remains functional until token actually expires

### Network Issues

If business server is unreachable:
1. Log connection errors
2. Continue with existing token
3. Retry on next sync cycle
4. Graceful degradation of functionality

### API Key Issues

If API key is invalid or expired:
1. Log authentication errors
2. Continue with existing token if available
3. Retry on next sync cycle
4. System may lose functionality until valid API key is provided

## Security Considerations

### Token Security

1. **Short Expiration**: 30-minute tokens limit exposure window
2. **Proactive Refresh**: Prevents service interruption
3. **Secure Storage**: Tokens stored in memory only
4. **No Persistence**: Tokens not saved to disk
5. **API Key Rotation**: Support for neuron-specific API keys

### Authentication Flow

1. **Initial Registration**: Neuron authenticates with business server
2. **Token Exchange**: Business server provides access token
3. **Continuous Refresh**: Both tokens refreshed before expiration
4. **Bidirectional Auth**: Both directions use separate keys
5. **Graceful Shutdown**: API keys recorded to .env file on shutdown

## Monitoring and Logging

### Log Levels

- **INFO**: Token refresh events, registration results, shutdown events
- **DEBUG**: Token validity checks, timing information, API key updates
- **WARNING**: Refresh failures, network issues, missing API keys
- **ERROR**: Critical authentication failures

### Metrics to Monitor

1. **Token Refresh Frequency**: Should be ~25 minutes apart for both tokens
2. **Refresh Success Rate**: Should be close to 100% for both tokens
3. **Authentication Failures**: Should be minimal
4. **Network Latency**: Impact on refresh operations
5. **API Key Validity**: Track API key expiration and rotation

## Business Server Access Mechanism

### Neuron Registration Process

The neuron registration system enables bidirectional communication between neurons and the business server:

1. **Token Creation**: Neurons create authentication tokens using `create_neuron_access_token()`
2. **Registration**: Neurons send registration data including metadata and token to business server
3. **Database Management**: Business server handles new neuron records and token updates
4. **Access Capability**: Business server can now access and communicate with registered neurons
5. **Token Validation**: Neurons verify token legitimacy during the registration process

### Business Server Database Operations

- **New Neurons**: Create new database records with neuron metadata and authentication token
- **Existing Neurons**: Update authentication tokens while maintaining existing records
- **Token Expiration**: Handle token refresh cycles to maintain continuous access
- **Access Control**: Business server uses stored tokens to authenticate with neurons

### Security Considerations

1. **Token Authentication**: Neurons validate tokens before accepting business server requests
2. **Database Security**: Business server securely stores neuron tokens and metadata
3. **Token Rotation**: Regular token refresh prevents long-term token exposure
4. **Access Verification**: Business server verifies token validity before neuron communication
