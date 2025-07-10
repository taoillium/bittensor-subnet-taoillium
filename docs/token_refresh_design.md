# Token Refresh Design Documentation

## Overview

This document describes the token refresh mechanism implemented in the Bittensor subnet neurons (validators and miners) to maintain continuous authentication with the business server.

## Problem Statement

The original design had a critical issue:
- `register_with_business_server()` was only called once during initialization
- JWT tokens have a 30-minute expiration time for security
- After token expiration, business server calls to `/task/receive` would fail authentication
- This would break the continuous operation of the system

## Solution: Automatic Token Refresh

### Design Principles

1. **Proactive Refresh**: Refresh tokens 5 minutes before expiration to ensure continuous operation
2. **Minimal Overhead**: Only refresh when necessary, not on every sync cycle
3. **Consistent Behavior**: Same logic for both validators and miners
4. **Graceful Degradation**: System continues to work even if refresh fails

### Implementation Details

#### 1. Token Refresh Tracking

```python
def register_with_business_server(self):
    """Register this neuron with the business server to establish authentication"""
    data = {"uid": self.uid, "chain": "bittensor", "netuid": self.config.netuid, "type": "miner", "account": self.wallet.hotkey.ss58_address}
    data["token"] = create_neuron_access_token(data=data)
    client = ServiceApiClient()
    result = client.post("/sapi/node/neuron/register", json=data)
    bt.logging.info(f"Register with business server result: {result}")
    # Store registration time for token refresh tracking
    self.last_token_refresh = time.time()
```

#### 2. Refresh Decision Logic

```python
def should_refresh_token(self) -> bool:
    """Check if the business server token needs to be refreshed"""
    if not hasattr(self, 'last_token_refresh'):
        return True
    
    # Refresh token 5 minutes before expiration (30 - 5 = 25 minutes)
    token_refresh_interval = (settings.NEURON_JWT_EXPIRE_IN - 5) * 60  # Convert to seconds
    return (time.time() - self.last_token_refresh) > token_refresh_interval
```

#### 3. Refresh Execution

```python
def refresh_business_server_token(self):
    """Refresh the business server token to maintain authentication"""
    if self.should_refresh_token():
        bt.logging.info("Refreshing business server token")
        self.register_with_business_server()
    else:
        bt.logging.trace("Token still valid, no refresh needed")
```

#### 4. Integration with Sync Cycle

```python
def sync(self):
    """
    Wrapper for synchronizing the state of the network for the given validator.
    Includes business server token refresh.
    """
    self.set_subtensor()
    self.check_registered()
    
    # Refresh business server token if needed
    self.refresh_business_server_token()
    
    if self.should_sync_metagraph():
        self.resync_metagraph()
    
    if self.should_set_weights():
        self.set_weights()
    
    self.save_state()
```

## Timing and Frequency

### Token Lifecycle

1. **Initial Registration**: Token created during neuron startup
2. **Active Period**: Token valid for 30 minutes (configurable via `NEURON_JWT_EXPIRE_IN`)
3. **Refresh Window**: Token refreshed 5 minutes before expiration (25 minutes after creation)
4. **Continuous Operation**: Process repeats indefinitely

### Sync Cycle Integration

- **Validator**: `sync()` called every epoch (typically every 100 blocks)
- **Miner**: `sync()` called periodically during operation
- **Token Refresh**: Checked on every sync cycle, but only executed when needed

## Configuration

### Environment Variables

```bash
# Token expiration time in minutes
NEURON_JWT_EXPIRE_IN=30

# Token refresh buffer (hardcoded to 5 minutes)
# This ensures tokens are refreshed 5 minutes before expiration
```

### Customization Options

1. **Refresh Buffer**: Currently hardcoded to 5 minutes, could be made configurable
2. **Refresh Strategy**: Could implement exponential backoff for failed refreshes
3. **Token Validation**: Could add token validation before refresh to avoid unnecessary calls

## Error Handling

### Refresh Failures

If token refresh fails:
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

## Security Considerations

### Token Security

1. **Short Expiration**: 30-minute tokens limit exposure window
2. **Proactive Refresh**: Prevents service interruption
3. **Secure Storage**: Tokens stored in memory only
4. **No Persistence**: Tokens not saved to disk

### Authentication Flow

1. **Initial Registration**: Neuron authenticates with business server
2. **Token Exchange**: Business server provides access token
3. **Continuous Refresh**: Tokens refreshed before expiration
4. **Bidirectional Auth**: Both directions use separate keys

## Monitoring and Logging

### Log Levels

- **INFO**: Token refresh events, registration results
- **DEBUG**: Token validity checks, timing information
- **WARNING**: Refresh failures, network issues
- **ERROR**: Critical authentication failures

### Metrics to Monitor

1. **Token Refresh Frequency**: Should be ~25 minutes apart
2. **Refresh Success Rate**: Should be close to 100%
3. **Authentication Failures**: Should be minimal
4. **Network Latency**: Impact on refresh operations

## Future Enhancements

### Potential Improvements

1. **Configurable Refresh Buffer**: Make 5-minute buffer configurable
2. **Retry Logic**: Implement exponential backoff for failed refreshes
3. **Token Validation**: Validate token before refresh to avoid unnecessary calls
4. **Health Checks**: Add endpoint to check token validity
5. **Metrics Collection**: Add detailed metrics for monitoring

### Alternative Approaches

1. **Long-lived Tokens**: Use longer expiration with refresh tokens
2. **Certificate-based Auth**: Use mTLS instead of JWT
3. **OAuth 2.0**: Implement full OAuth flow with refresh tokens
4. **API Keys**: Use simple API keys with rotation 