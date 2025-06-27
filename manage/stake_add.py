import argparse
import sys
import os
import logging

# Add the parent directory to the Python path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cli import stake_add
import json
from services.config import settings

def main():
    # Configure logging to show debug messages
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Add stake to a Bittensor subnet')
    parser.add_argument('--wallet-name', required=False, help='Wallet name', default=settings.VALIDATOR_WALLET)
    parser.add_argument('--hotkey', required=False, help='Hotkey name', default=settings.VALIDATOR_HOTKEY)
    parser.add_argument('--amount', required=True, type=float, help='Amount to stake', default=0.0)
    parser.add_argument('--netuid', required=False, type=int, help='Network UID', default=settings.CHAIN_NETUID)
    parser.add_argument('--password', required=False, help='Wallet password', default=settings.VALIDATOR_PASSWORD)
    parser.add_argument('--partial', action='store_true', help='Partial stake')
    parser.add_argument('--network', required=False, help='Chain network')
    parser.add_argument('--chain-endpoint', required=False, help='Chain endpoint')
    
    args = parser.parse_args()
    
    try:
        result = stake_add(
            wallet_name=args.wallet_name,
            hotkey=args.hotkey,
            amount=args.amount,
            netuid=args.netuid,
            password=args.password,
            chain_endpoint=args.chain_endpoint,
            network=args.network,
            partial=args.partial
        )
        
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            # Check if staking was actually successful
            if 'staking_success' in result:
                success_dict = result['staking_success']
                for netuid_key, hotkey_dict in success_dict.items():
                    for hotkey_addr, success in hotkey_dict.items():
                        if success:
                            print("✅ Stake added successfully!")
                        else:
                            print("❌ Stake operation failed!")
                        print(f"Network UID: {netuid_key}")
                        print(f"Hotkey: {hotkey_addr}")
                        print(f"Success: {success}")
            else:
                print("✅ Stake added successfully!")
            print(f"Full Result: {result}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

