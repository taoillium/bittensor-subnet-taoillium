#!/usr/bin/env python3
"""
Test cases for subnet API functionality
"""

import unittest
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bittensor as bt
from services.config import settings


class TestSubnetAPI(unittest.TestCase):
    """Test cases for subnet API functionality"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    def test_metagraph_initialization(self):
        """Test that metagraph can be initialized without wallet"""
        try:
            metagraph = bt.metagraph(netuid=settings.CHAIN_NETUID, network=settings.CHAIN_NETWORK)
            
            self.assertIsNotNone(metagraph)
            self.assertEqual(metagraph.netuid, settings.CHAIN_NETUID)
            self.assertEqual(metagraph.network, settings.CHAIN_NETWORK)
            self.assertGreater(len(metagraph.axons), 0)
            self.assertIsNotNone(metagraph.block)
            
        except Exception as e:
            self.fail(f"Metagraph initialization failed: {e}")

    def test_wallet_creation(self):
        """Test that wallet can be created with config"""
        try:
            import argparse
            parser = argparse.ArgumentParser()
            bt.wallet.add_args(parser)
            config = bt.config(parser)
            config.wallet.name = settings.WALLET_NAME
            config.wallet.hotkey = settings.HOTKEY_NAME
            
            wallet = bt.wallet(config=config)
            
            self.assertIsNotNone(wallet)
            self.assertIsNotNone(wallet.hotkey)
            self.assertIsNotNone(wallet.hotkey.ss58_address)
            
        except Exception as e:
            self.fail(f"Wallet creation failed: {e}")

    def test_api_client_creation(self):
        """Test that TaoilliumAPI client can be created"""
        try:
            from template.api import TaoilliumAPI
            
            # First create wallet
            import argparse
            parser = argparse.ArgumentParser()
            bt.wallet.add_args(parser)
            config = bt.config(parser)
            config.wallet.name = settings.WALLET_NAME
            config.wallet.hotkey = settings.HOTKEY_NAME
            wallet = bt.wallet(config=config)
            
            # Create API client
            api_client = TaoilliumAPI(
                wallet=wallet, 
                netuid=settings.CHAIN_NETUID, 
                network=settings.CHAIN_NETWORK,
                chain_endpoint=settings.CHAIN_ENDPOINT
            )
            
            self.assertIsNotNone(api_client)
            self.assertEqual(api_client.netuid, settings.CHAIN_NETUID)
            self.assertEqual(api_client.name, "taoillium")
            self.assertGreater(len(api_client.metagraph.axons), 0)
            
        except Exception as e:
            self.fail(f"TaoilliumAPI client creation failed: {e}")

    def test_settings_configuration(self):
        """Test that settings are properly configured"""
        self.assertIsNotNone(settings.CHAIN_NETUID)
        self.assertIsNotNone(settings.CHAIN_NETWORK)
        self.assertIsNotNone(settings.WALLET_NAME)
        self.assertIsNotNone(settings.HOTKEY_NAME)
        
        # Check that netuid is a positive integer
        self.assertIsInstance(settings.CHAIN_NETUID, int)
        self.assertGreater(settings.CHAIN_NETUID, 0)
        
        # Check that network is a string
        self.assertIsInstance(settings.CHAIN_NETWORK, str)
        self.assertGreater(len(settings.CHAIN_NETWORK), 0)

    def test_metagraph_consistency(self):
        """Test that metagraph data is consistent"""
        try:
            metagraph = bt.metagraph(netuid=settings.CHAIN_NETUID, network=settings.CHAIN_NETWORK)
            
            # Test basic properties
            self.assertIsNotNone(metagraph.netuid)
            self.assertIsNotNone(metagraph.network)
            self.assertIsNotNone(metagraph.block)
            self.assertGreater(len(metagraph.axons), 0)
            
            # Test that arrays have consistent lengths
            total_nodes = len(metagraph.axons)
            self.assertEqual(len(metagraph.validator_permit), total_nodes)
            self.assertEqual(len(metagraph.hotkeys), total_nodes)
            
            # Test that all hotkeys are strings
            for hotkey in metagraph.hotkeys:
                self.assertIsInstance(hotkey, str)
                self.assertGreater(len(hotkey), 0)
                
        except Exception as e:
            self.fail(f"Metagraph consistency test failed: {e}")

    def test_wallet_configuration(self):
        """Test that wallet configuration is valid"""
        try:
            import argparse
            parser = argparse.ArgumentParser()
            bt.wallet.add_args(parser)
            config = bt.config(parser)
            config.wallet.name = settings.WALLET_NAME
            config.wallet.hotkey = settings.HOTKEY_NAME
            
            # Test that config is properly set
            self.assertEqual(config.wallet.name, settings.WALLET_NAME)
            self.assertEqual(config.wallet.hotkey, settings.HOTKEY_NAME)
            
        except Exception as e:
            self.fail(f"Wallet configuration test failed: {e}")


class TestSubnetAPIIntegration(unittest.TestCase):
    """Integration tests for subnet API"""

    def test_full_api_workflow(self):
        """Test the complete API workflow"""
        try:
            # 1. Initialize metagraph
            metagraph = bt.metagraph(netuid=settings.CHAIN_NETUID, network=settings.CHAIN_NETWORK)
            self.assertIsNotNone(metagraph)
            
            # 2. Create wallet
            import argparse
            parser = argparse.ArgumentParser()
            bt.wallet.add_args(parser)
            config = bt.config(parser)
            config.wallet.name = settings.WALLET_NAME
            config.wallet.hotkey = settings.HOTKEY_NAME
            wallet = bt.wallet(config=config)
            self.assertIsNotNone(wallet)
            
            # 3. Create API client
            from template.api import TaoilliumAPI
            api_client = TaoilliumAPI(
                wallet=wallet, 
                netuid=settings.CHAIN_NETUID, 
                network=settings.CHAIN_NETWORK,
                chain_endpoint=settings.CHAIN_ENDPOINT
            )
            self.assertIsNotNone(api_client)
            
            # 4. Test basic API functionality
            self.assertEqual(api_client.netuid, metagraph.netuid)
            self.assertEqual(len(api_client.metagraph.axons), len(metagraph.axons))
            
        except Exception as e:
            self.fail(f"Full API workflow test failed: {e}")


if __name__ == '__main__':
    unittest.main() 