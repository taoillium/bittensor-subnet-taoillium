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
