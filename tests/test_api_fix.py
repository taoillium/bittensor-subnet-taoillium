#!/usr/bin/env python3
"""
Test cases for TaoilliumAPI miner selection fix
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bittensor as bt
from services.config import settings
from template.api import TaoilliumAPI


class TestTaoilliumAPIMinerSelection(unittest.TestCase):
    """Test cases for TaoilliumAPI miner selection functionality"""

    def setUp(self):
        """Set up test fixtures"""
        try:
            # Create wallet
            import argparse
            parser = argparse.ArgumentParser()
            bt.wallet.add_args(parser)
            config = bt.config(parser)
            config.wallet.name = settings.WALLET_NAME
            config.wallet.hotkey = settings.HOTKEY_NAME
            self.wallet = bt.wallet(config=config)
            
            # Create API client
            self.api_client = TaoilliumAPI(
                wallet=self.wallet, 
                netuid=settings.CHAIN_NETUID, 
                network=settings.CHAIN_NETWORK,
                chain_endpoint=settings.CHAIN_ENDPOINT
            )
        except Exception as e:
            self.skipTest(f"Failed to set up API client: {e}")

    def test_api_client_creation(self):
        """Test that TaoilliumAPI client can be created successfully"""
        self.assertIsNotNone(self.api_client)
        self.assertEqual(self.api_client.netuid, settings.CHAIN_NETUID)
        self.assertEqual(self.api_client.name, "taoillium")
        self.assertIsNotNone(self.api_client.metagraph)

    def test_get_miner_uids_returns_axons(self):
        """Test that get_miner_uids returns axon objects"""
        try:
            miner_axons = self.api_client.get_miner_uids(sample_size=3)
            
            # Should return a list
            self.assertIsInstance(miner_axons, list)
            
            # Should not be empty (assuming there are miners in the network)
            self.assertGreater(len(miner_axons), 0)
            
            # Each item should be an axon object
            for axon in miner_axons:
                self.assertIsNotNone(axon)
                # Check if it has axon-like attributes
                self.assertTrue(hasattr(axon, 'hotkey') or hasattr(axon, 'is_serving'))
                
        except Exception as e:
            # If no miners found, that's also acceptable for testing
            if "No available miners found" in str(e):
                self.skipTest("No miners available in the network")
            else:
                raise

    def test_miner_selection_sample_size(self):
        """Test that miner selection respects the sample size parameter"""
        try:
            # Test with different sample sizes
            for sample_size in [1, 2, 3]:
                miner_axons = self.api_client.get_miner_uids(sample_size=sample_size)
                self.assertLessEqual(len(miner_axons), sample_size)
                
        except Exception as e:
            if "No available miners found" in str(e):
                self.skipTest("No miners available in the network")
            else:
                raise

    def test_metagraph_consistency(self):
        """Test that the metagraph is consistent"""
        metagraph = self.api_client.metagraph
        self.assertIsNotNone(metagraph)
        self.assertEqual(metagraph.netuid, settings.CHAIN_NETUID)
        self.assertGreater(len(metagraph.axons), 0)


if __name__ == '__main__':
    unittest.main() 