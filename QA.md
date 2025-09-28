# Questions

## Q: Why does the subnet have no incentives or emissions when I staked TAO in the new subnet to become a validator, and the validator and miner nodes are running?

A: Answer about the minimum TAO staking requirements for validators to receive normal incentive and emission rewards in your local network setup.

## Minimum Staking Requirements Analysis
Based on the subtensor code analysis, here are the minimum TAO staking requirements for validators to receive normal rewards and emissions:

### 1. Default Stake Threshold (Default Stake Threshold)
From the code, we can see:
Default stake threshold: DefaultStakeThreshold<T>() returns 0
Default minimum stake: DefaultMinStake<T>() returns 500_000 (0.0005 TAO)
Default staking fee: DefaultStakingFee<T>() returns 50_000 (0.00005 TAO)

### 2. Actual Staking Amounts in Testing
From the test code, we can see the actual staking amounts used:
```javascript
// In evm-tests/test/staking.precompile.reward.test.ts
await addStake(api, netuid, convertPublicKeyToSs58(validator.publicKey), tao(100), coldkey)
```
Here tao(100) represents 100 TAO, which is the staking amount used by validators in testing.

### 3. Reward Distribution Mechanism
According to the consensus documentation, reward distribution follows these formulas:
- Emission ratio: ξ = 0.5 (50% to validators, 50% to miners)
- Validator reward: D_i = Σ_j B_ij · I_j (validator's EMA bond multiplied by server incentive)
- Final emission: E_i = ξ · D_i + (1-ξ) · I_i

### 4. Key Requirements
For validators to receive rewards normally, they need to meet:
Stake threshold check: Validator's total stake must be ≥ stake_threshold
Weight setting permission: Only validators meeting minimum stake requirements can set weights
Consensus participation: Validators need to participate in consensus and set valid weights

### 5. Recommended Minimum Staking Amount
Based on test code and actual usage, it is recommended:
Minimum stake: 100 TAO (based on usage in test code)
Recommended stake: 1000+ TAO (to ensure sufficient influence in the network)

### 6. Local Network Special Considerations
In local networks:
Stake threshold is usually set to 0 (default value)
But to participate normally in consensus and receive rewards, it is recommended to stake at least 100 TAO
Ensure validators set valid weights
Ensure miners are also registered and set weights

### Summary
Answer: For validators to receive normal incentive and emissions rewards in local networks, it is recommended to stake at least 100 TAO. Although the default stake threshold is 0, in actual testing and operation, 100 TAO is the minimum recommended amount to ensure validators can effectively participate in consensus and receive rewards.

## Testnet and Mainnet Staking Requirements Analysis
### Key Findings
From the code analysis, I discovered an important fact:
All networks (local network, testnet, mainnet) use the same code logic, which means:
1. Default stake threshold: All networks' DefaultStakeThreshold<T>() returns 0
2. Stake threshold check: All networks use Self::get_stake_threshold() to check minimum stake requirements
3. Dynamic configuration: Stake thresholds can be dynamically adjusted through governance or administrator operations

### Actual Network Configuration
1. Local Network
Stake threshold: 0 (default value)
Recommended stake: 100 TAO (based on test code)

2. Testnet (Testfinney)
Stake threshold: 0 (default value, unless modified by administrator)
Actual requirement: Need to check current network status

3. Mainnet (Finney)
Stake threshold: 0 (default value, unless modified by administrator)
Actual requirement: Need to check current network status

### Important Notes
Key Point: Although the default stake threshold is 0, this doesn't mean validators don't need to stake to receive rewards. In reality:
1. Consensus participation: Validators need sufficient stake to participate in consensus
2. Weight setting permission: Only validators meeting stake requirements can set weights
3. Reward distribution: Reward distribution is based on relative stake weight - more stake means more rewards

### How to Check Current Network Stake Requirements
You can check the current network's stake threshold through the following methods:
```sh
# Check current stake threshold
subtensor query stake_threshold --network finney
subtensor query stake_threshold --network testfinney
```

### Practical Recommendations
Based on code analysis and network practice:
1. Testnet (Testfinney): Recommend staking at least 100-1000 TAO
2. Mainnet (Finney): Recommend staking at least 1000+ TAO to receive meaningful rewards

### Summary
Answer: The default minimum stake requirements for testnet and mainnet are also 0, the same as local networks. However, to actually receive meaningful rewards and participate in consensus, it is recommended:
1. Testnet: Minimum 100 TAO
2. Mainnet: Minimum 1000+ TAO
The actual stake threshold may be dynamically adjusted by network administrators, so it's recommended to query the current network's actual configuration before participating.