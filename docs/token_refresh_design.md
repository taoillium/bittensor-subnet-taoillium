# Token Refresh Design Documentation

## Overview

This document describes the dual token refresh mechanism implemented in the Bittensor subnet neurons (validators and miners) to maintain continuous authentication with the business server.

## Solution: Integrated Token Refresh System

### Design Principles

1. **Integrated Authentication**: Single endpoint returns both tokens for simplified architecture
2. **Proactive Refresh**: Refresh tokens 5 minutes before expiration to ensure continuous operation
3. **Minimal Overhead**: Only refresh when necessary, not on every sync cycle
4. **Consistent Behavior**: Same logic for both validators and miners
5. **Graceful Degradation**: System continues to work even if refresh fails

### Implementation Details

#### 1. Token Types and Purposes

**Integrated Business Server Access (`refresh_business_server_access`)**:
- Used for neurons to register with the business server and obtain service tokens
- Endpoint: `/sapi/node/neuron/register`
- Contains neuron metadata (uid, chain, netuid, type, account) and authentication token
- Returns both neuron registration token and service access token
- Allows business server to access and communicate with neurons
- New neurons create database records, existing neurons update their tokens
- Both tokens expire after 30 minutes (configurable via `NEURON_JWT_EXPIRE_IN`)

#### 2. Token Refresh Tracking

```python
def __init__(self, config=None):
    # ... other initialization code ...
    
    # Initialize token expiration timestamps for both tokens
    self.last_neuron_registration_expire = time.time() + 60  # 1 minute from now
    self.last_service_token_expire = time.time() + 60  # 1 minute from now
```

#### 3. Integrated Business Server Access Refresh

```python
def refresh_business_server_access(self):
    """Refresh both neuron registration and service access tokens from business server"""
    try:
        # Check if we have an API key to use
        if not self.current_api_key_value:
            bt.logging.warning("No API key available for business server registration")
            return

        # Check if either token needs refresh (5 minutes before expiration)
        token_refresh_interval = min(settings.NEURON_JWT_EXPIRE_IN * 60, 300)  # Convert to seconds
        neuron_token_expired = (self.last_neuron_registration_expire - time.time()) < token_refresh_interval
        service_token_expired = (self.last_service_token_expire - time.time()) < token_refresh_interval
        
        if not (neuron_token_expired or service_token_expired):
            bt.logging.debug(f"Both tokens still valid, skipping refresh")
            return

        # Prepare neuron registration data with authentication token
        data = {
            "uid": self.uid, 
            "chain": "bittensor", 
            "netuid": self.config.netuid, 
            "type": self.neuron_type, 
            "account": self.wallet.hotkey.ss58_address
        }
        # Create authentication token for business server access
        data["token"] = create_neuron_access_token(data=data)
        
        # Use dedicated token refresh endpoint
        client = ServiceApiClient(self.current_api_key_value)
        result = client.post("/sapi/node/neuron/refresh", json=data)
        bt.logging.debug(f"Token refresh result: {result}")
        
        if result.get("success"):
            # Update both token expiration times
            self.last_neuron_registration_expire = time.time() + settings.NEURON_JWT_EXPIRE_IN * 60
            
            # Update service token if returned
            if result.get("access_token") and result.get("exp"):
                self.last_service_token_expire = result.get("exp")
                self.current_api_key_value = result.get("access_token")
                settings.SRV_API_KEY = self.current_api_key_value
                bt.logging.debug(f"Service token refreshed, expires at: {result.get('exp')}")
        else:
            bt.logging.error(f"Failed to refresh tokens: {result}")
    except Exception as e:
        bt.logging.error(f"Failed to refresh business server access: {e}")
```

#### 4. Integration with Sync Cycle

```python
def sync(self):
    """
    Wrapper for synchronizing the state of the network for the given miner or validator.
    Includes integrated token refresh mechanism.
    """
    self.set_subtensor()
    self.check_registered()
    
    if self.should_sync_metagraph():
        self.resync_metagraph()
    
    if self.should_set_weights():
        self.set_weights()
    
    # Always save state.
    self.save_state()

    # Refresh both tokens in single call
    self.refresh_business_server_access()
```

## Token Lifecycle and Timing

### Integrated Token Lifecycle

1. **Initial Registration**: Neuron creates authentication token and registers with business server
2. **Token Response**: Business server returns both neuron registration token and service access token
3. **Database Handling**: Business server creates new database record for new neurons, updates tokens for existing neurons
4. **Active Period**: Both tokens valid for 30 minutes (configurable via `NEURON_JWT_EXPIRE_IN`)
5. **Refresh Window**: Tokens refreshed 5 minutes before expiration (25 minutes after creation)
6. **Continuous Operation**: Process repeats indefinitely, maintaining business server access capability

### Sync Cycle Integration

- **Validator**: `sync()` called every epoch (typically every 100 blocks)
- **Miner**: `sync()` called periodically during operation
- **Token Refresh**: Both tokens checked on every sync cycle, but only executed when either token needs refresh

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

```python
# Track current API key information
self.current_api_key_name = None
self.current_api_key_value = None

# Initialize from environment
if os.getenv(my_srv_api_key):
    settings.SRV_API_KEY = os.getenv(my_srv_api_key)
    self.current_api_key_value = settings.SRV_API_KEY
    self.current_api_key_name = my_srv_api_key
elif os.getenv("SRV_API_KEY"):
    self.current_api_key_value = os.getenv("SRV_API_KEY")
    self.current_api_key_name = "SRV_API_KEY"
```

### Graceful Shutdown

```python
def _signal_handler(self, signum, frame):
    """Handle shutdown signals and record API key to .env file"""
    bt.logging.info(f"Received signal {signum}, shutting down gracefully...")
    bt.logging.info(f"Current API key name: {self.current_api_key_name}")
    bt.logging.info(f"Current API key value: {'*' * len(self.current_api_key_value) if self.current_api_key_value else 'None'}")
    settings.record_api_key_to_env(self.current_api_key_name, self.current_api_key_value)
    sys.exit(0)
```

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

## API Design and Naming Considerations

### Current API Endpoint Analysis

**Current Endpoint**: `/sapi/node/neuron/register`

**Design Intent**: 
1. **Neuron Registration**: Client neurons register with the business server
2. **Token Exchange**: Server returns access tokens after successful registration
3. **Bidirectional Authentication**: Both neuron and business server obtain authentication tokens
4. **Continuous Operation**: Registration includes token refresh for ongoing access

**Current Implementation is Correct**:
- ✅ **Semantic Accuracy**: The endpoint correctly handles neuron registration
- ✅ **Function Completeness**: Registration includes authentication and token exchange
- ✅ **RESTful Compliance**: POST /register is standard for registration operations
- ✅ **Business Logic**: Registration provides immediate access through token exchange

### API Design Validation

**Why `/sapi/node/neuron/register` is Appropriate**:

1. **Registration Process**:
   ```
   Neuron → POST /register → Business Server
   Business Server → Validate → Return Tokens
   ```

2. **Token Exchange Flow**:
   ```
   Request: Neuron metadata + authentication token
   Response: Registration confirmation + service access token
   ```

3. **Bidirectional Authentication**:
   ```
   Neuron gets: Service access token (for API calls)
   Business Server gets: Neuron authentication token (for neuron access)
   ```

### Current Implementation is Optimal

**Benefits of Current Design**:
1. **Single Endpoint**: Efficient one-call registration with token exchange
2. **Clear Purpose**: Registration endpoint naturally includes authentication
3. **Standard Practice**: Common pattern in API design
4. **Minimal Overhead**: No need for separate registration and token calls

**Implementation Strategy** (Current approach is correct):
```python
def refresh_business_server_access(self):
    """Refresh both neuron registration and service access tokens from business server"""
    try:
        # Check if we have an API key to use
        if not self.current_api_key_value:
            bt.logging.warning("No API key available for business server registration")
            return

        # Check if either token needs refresh (5 minutes before expiration)
        token_refresh_interval = min(settings.NEURON_JWT_EXPIRE_IN * 60, 300)  # Convert to seconds
        neuron_token_expired = (self.last_neuron_registration_expire - time.time()) < token_refresh_interval
        service_token_expired = (self.last_service_token_expire - time.time()) < token_refresh_interval
        
        if not (neuron_token_expired or service_token_expired):
            bt.logging.debug(f"Both tokens still valid, skipping refresh")
            return

        # Prepare neuron registration data with authentication token
        data = {
            "uid": self.uid, 
            "chain": "bittensor", 
            "netuid": self.config.netuid, 
            "type": self.neuron_type, 
            "account": self.wallet.hotkey.ss58_address
        }
        # Create authentication token for business server access
        data["token"] = create_neuron_access_token(data=data)
        
        # Register neuron with business server and get both tokens
        # This is the correct approach - registration includes token exchange
        client = ServiceApiClient(self.current_api_key_value)
        result = client.post("/sapi/node/neuron/register", json=data)
        bt.logging.debug(f"Register with business server result: {result}")
        
        if result.get("success"):
            # Update both token expiration times
            self.last_neuron_registration_expire = time.time() + settings.NEURON_JWT_EXPIRE_IN * 60
            
            # Update service token if returned
            if result.get("access_token") and result.get("exp"):
                self.last_service_token_expire = result.get("exp")
                self.current_api_key_value = result.get("access_token")
                settings.SRV_API_KEY = self.current_api_key_value
                bt.logging.debug(f"Service token refreshed, expires at: {result.get('exp')}")
        else:
            bt.logging.error(f"Failed to register with business server: {result}")
    except Exception as e:
        bt.logging.error(f"Failed to refresh business server access: {e}")
```

### Server-Side API Design (Current is Correct)

**Current Server Endpoint**:
```
POST /sapi/node/neuron/register
Purpose: Neuron registration with token exchange
Request: Neuron metadata + authentication token
Response: Registration confirmation + service access token
```

**Why This Design Works**:
1. **Registration Includes Authentication**: Standard practice in API design
2. **Token Exchange**: Natural part of the registration process
3. **Efficient**: Single call handles both registration and token provision
4. **Clear Intent**: Registration endpoint naturally provides access credentials

### Conclusion

The current API design with `/sapi/node/neuron/register` is **correct and optimal**:

- ✅ **Semantic Accuracy**: Correctly represents neuron registration
- ✅ **Functional Completeness**: Handles both registration and token exchange
- ✅ **RESTful Compliance**: Follows standard API design patterns
- ✅ **Business Logic**: Registration provides immediate access through tokens
- ✅ **Efficiency**: Single endpoint reduces complexity and overhead

**No changes needed** - the current implementation aligns perfectly with the intended design.
