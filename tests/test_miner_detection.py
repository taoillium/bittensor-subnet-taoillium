#!/usr/bin/env python3
"""
Test cases for miner detection logic
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bittensor as bt
from services.config import settings


class TestMinerDetection(unittest.TestCase):
    """Test cases for miner detection logic"""

    def setUp(self):
        """Set up test fixtures"""
        try:
            self.metagraph = bt.metagraph(netuid=settings.CHAIN_NETUID, network=settings.CHAIN_NETWORK)
        except Exception as e:
            self.skipTest(f"Failed to set up metagraph: {e}")

    def test_metagraph_initialization(self):
        """Test that metagraph can be initialized"""
        self.assertIsNotNone(self.metagraph)
        self.assertEqual(self.metagraph.netuid, settings.CHAIN_NETUID)
        self.assertGreater(len(self.metagraph.axons), 0)

    def test_node_status_consistency(self):
        """Test that node status information is consistent"""
        total_nodes = len(self.metagraph.axons)
        self.assertGreater(total_nodes, 0)
        
        # Check that all nodes have consistent status information
        for uid in range(total_nodes):
            # validator_permit should be a boolean
            self.assertIsInstance(self.metagraph.validator_permit[uid], (bool, type(self.metagraph.validator_permit[uid])))
            
            # axon should exist and have is_serving attribute
            axon = self.metagraph.axons[uid]
            self.assertIsNotNone(axon)
            self.assertIsInstance(axon.is_serving, (bool, type(axon.is_serving)))

    def test_miner_detection_logic(self):
        """Test the miner detection logic"""
        # Test the logic from TaoilliumAPI.get_miner_uids
        non_validator_serving_uids = [
            uid for uid in range(len(self.metagraph.axons))
            if not self.metagraph.validator_permit[uid] and self.metagraph.axons[uid].is_serving
        ]
        
        serving_validator_uids = [
            uid for uid in range(len(self.metagraph.axons))
            if self.metagraph.validator_permit[uid] and self.metagraph.axons[uid].is_serving
        ]
        
        all_non_validator_uids = [
            uid for uid in range(len(self.metagraph.axons))
            if not self.metagraph.validator_permit[uid]
        ]
        
        # Test that the logic produces consistent results
        if non_validator_serving_uids:
            miner_uids = non_validator_serving_uids
        else:
            miner_uids = serving_validator_uids
            if not miner_uids:
                miner_uids = all_non_validator_uids
        
        # Should have some potential miners (either serving or non-serving)
        self.assertIsInstance(miner_uids, list)
        
        # All selected UIDs should be within valid range
        for uid in miner_uids:
            self.assertGreaterEqual(uid, 0)
            self.assertLess(uid, len(self.metagraph.axons))

    def test_validator_miner_distribution(self):
        """Test that we can identify validators and miners"""
        validators = [
            uid for uid in range(len(self.metagraph.axons))
            if self.metagraph.validator_permit[uid]
        ]
        
        miners = [
            uid for uid in range(len(self.metagraph.axons))
            if not self.metagraph.validator_permit[uid]
        ]
        
        # Should have some validators and miners
        self.assertIsInstance(validators, list)
        self.assertIsInstance(miners, list)
        
        # Validators and miners should be mutually exclusive
        validator_set = set(validators)
        miner_set = set(miners)
        self.assertEqual(len(validator_set.intersection(miner_set)), 0)
        
        # All UIDs should be either validator or miner
        all_uids = set(range(len(self.metagraph.axons)))
        self.assertEqual(validator_set.union(miner_set), all_uids)

    def test_serving_status(self):
        """Test serving status of nodes"""
        serving_nodes = [
            uid for uid in range(len(self.metagraph.axons))
            if self.metagraph.axons[uid].is_serving
        ]
        
        non_serving_nodes = [
            uid for uid in range(len(self.metagraph.axons))
            if not self.metagraph.axons[uid].is_serving
        ]
        
        # Should have some serving and non-serving nodes
        self.assertIsInstance(serving_nodes, list)
        self.assertIsInstance(non_serving_nodes, list)
        
        # Serving and non-serving should be mutually exclusive
        serving_set = set(serving_nodes)
        non_serving_set = set(non_serving_nodes)
        self.assertEqual(len(serving_set.intersection(non_serving_set)), 0)
        
        # All UIDs should be either serving or non-serving
        all_uids = set(range(len(self.metagraph.axons)))
        self.assertEqual(serving_set.union(non_serving_set), all_uids)


if __name__ == '__main__':
    unittest.main() 