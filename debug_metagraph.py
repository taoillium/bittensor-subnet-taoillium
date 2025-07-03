#!/usr/bin/env python3
"""
Debug script to examine metagraph and axon details
"""

import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bittensor as bt
from services.config import settings
from template.api import TaoilliumAPI


async def debug_metagraph():
    """Debug the metagraph and axon details"""
    
    print("=" * 60)
    print("🔍 METAGRAPH DEBUG SCRIPT")
    print("=" * 60)
    
    try:
        # Create wallet
        import argparse
        parser = argparse.ArgumentParser()
        bt.wallet.add_args(parser)
        config = bt.config(parser)
        config.wallet.name = settings.WALLET_NAME
        config.wallet.hotkey = settings.HOTKEY_NAME
        wallet = bt.wallet(config=config)
        
        print(f"✅ Wallet created: {wallet}")
        print(f"📡 Network: {settings.CHAIN_NETWORK}")
        print(f"🔗 Chain endpoint: {settings.CHAIN_ENDPOINT}")
        print(f"🆔 NetUID: {settings.CHAIN_NETUID}")
        
        # Create API client
        api_client = TaoilliumAPI(
            wallet=wallet, 
            netuid=settings.CHAIN_NETUID, 
            network=settings.CHAIN_NETWORK,
            chain_endpoint=settings.CHAIN_ENDPOINT
        )
        
        print(f"✅ API client created")
        
        # Examine metagraph
        metagraph = api_client.metagraph
        print(f"\n📊 METAGRAPH INFO:")
        print(f"   Total axons: {len(metagraph.axons)}")
        print(f"   Network: {metagraph.network}")
        print(f"   NetUID: {metagraph.netuid}")
        print(f"   Block: {metagraph.block}")
        
        # Examine all axons
        print(f"\n🔗 ALL AXONS DETAILS:")
        print("-" * 80)
        print(f"{'UID':<4} {'IP':<20} {'Port':<6} {'Serving':<8} {'Validator':<10} {'Stake':<12}")
        print("-" * 80)
        
        serving_count = 0
        validator_count = 0
        
        for uid in range(len(metagraph.axons)):
            axon = metagraph.axons[uid]
            is_serving = axon.is_serving
            is_validator = metagraph.validator_permit[uid]
            stake = metagraph.S[uid].item() if hasattr(metagraph, 'S') else 0
            
            if is_serving:
                serving_count += 1
            if is_validator:
                validator_count += 1
                
            print(f"{uid:<4} {axon.ip:<20} {axon.port:<6} {str(is_serving):<8} {str(is_validator):<10} {stake:<12}")
        
        print("-" * 80)
        print(f"📈 SUMMARY:")
        print(f"   Serving axons: {serving_count}")
        print(f"   Validator axons: {validator_count}")
        print(f"   Non-validator axons: {len(metagraph.axons) - validator_count}")
        
        # Test miner selection
        print(f"\n🔍 MINER SELECTION TEST:")
        try:
            miner_axons = api_client.get_miner_uids(sample_size=3)
            print(f"   Selected {len(miner_axons)} miner axons")
            for i, axon in enumerate(miner_axons):
                print(f"   Miner {i+1}: {axon.ip}:{axon.port}")
        except Exception as e:
            print(f"   ❌ Miner selection failed: {e}")
        
        # Test ping functionality
        print(f"\n🏓 PING TEST:")
        try:
            # Get some candidate UIDs
            candidate_uids = api_client._get_miner_uids_list(sample_size=2)
            print(f"   Testing ping for UIDs: {candidate_uids}")
            
            # Test ping with detailed logging
            successful_uids = await api_client.ping_uids(candidate_uids, timeout=5)
            print(f"   Successful UIDs: {successful_uids}")
            
            if not successful_uids:
                print(f"   ⚠️  No successful pings - all connections failed")
                
        except Exception as e:
            print(f"   ❌ Ping test failed: {e}")
        
        # Test network query
        print(f"\n🌐 NETWORK QUERY TEST:")
        try:
            responses = await api_client.query_network(
                user_input={"__type__": "health"},
                sample_size=1,
                timeout=10,
                use_random_selection=True
            )
            print(f"   Query responses: {len(responses)}")
            for i, response in enumerate(responses):
                print(f"   Response {i+1}: {type(response)} - {response}")
                
        except Exception as e:
            print(f"   ❌ Network query failed: {e}")
        
        print(f"\n" + "=" * 60)
        print("🔍 DEBUG COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_metagraph()) 