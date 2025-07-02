# Tests Documentation

This directory contains test files for the Taoillium subnet project.

## New Tests (Created for Miner Selection Fix)

### 1. `test_api_fix.py`
Tests for the TaoilliumAPI miner selection functionality.

**Test Cases:**
- `test_api_client_creation`: Verifies TaoilliumAPI client can be created successfully
- `test_get_miner_uids_returns_axons`: Ensures get_miner_uids returns axon objects
- `test_miner_selection_sample_size`: Tests that miner selection respects sample size parameter
- `test_metagraph_consistency`: Verifies metagraph consistency

### 2. `test_miner_detection.py`
Tests for the miner detection logic.

**Test Cases:**
- `test_metagraph_initialization`: Tests metagraph initialization
- `test_node_status_consistency`: Verifies node status information consistency
- `test_miner_detection_logic`: Tests the miner detection algorithm
- `test_validator_miner_distribution`: Ensures validators and miners are properly identified
- `test_serving_status`: Tests serving status of nodes

### 3. `test_subnet_api.py`
Tests for the subnet API functionality.

**Test Cases:**
- `test_metagraph_initialization`: Tests metagraph initialization without wallet
- `test_wallet_creation`: Tests wallet creation with config
- `test_api_client_creation`: Tests TaoilliumAPI client creation
- `test_settings_configuration`: Verifies settings are properly configured
- `test_metagraph_consistency`: Tests metagraph data consistency
- `test_wallet_configuration`: Tests wallet configuration validity
- `test_full_api_workflow`: Integration test for complete API workflow

## Running Tests

### Run All New Tests
```bash
cd tests
python run_new_tests.py
```

### Run Individual Test Files
```bash
cd tests
python -m unittest test_api_fix.py -v
python -m unittest test_miner_detection.py -v
python -m unittest test_subnet_api.py -v
```

### Run All Tests (Including Old Tests)
```bash
cd tests
python -m unittest discover -v
```

## Test Results

All new tests should pass successfully. The tests verify:

1. **Miner Selection Logic**: Ensures that the updated miner selection algorithm works correctly
2. **API Functionality**: Verifies that the TaoilliumAPI can be created and used properly
3. **Network Connectivity**: Tests that the metagraph can be accessed and contains valid data
4. **Configuration**: Ensures that settings and wallet configuration are valid

## Notes

- Tests are designed to be robust and handle cases where no miners are available
- Some tests may be skipped if network connectivity is not available
- The tests use the actual network configuration from `services.config.settings`
- All tests use `unittest.TestCase` for consistency and proper test reporting 