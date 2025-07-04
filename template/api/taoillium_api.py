# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2025 Taoillium Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import bittensor as bt
from typing import List, Union, Any, Dict
from bittensor import SubnetsAPI
import services.protocol as protocol
from template.api.get_query_axons import get_query_api_axons
from services.config import settings
from services.api import get_local_ip


class TaoilliumAPI(SubnetsAPI):
    """
    Standardized API client for Taoillium subnet.
    This class provides a clean interface for external clients to interact with the subnet.
    """
    
    def __init__(self, wallet: "bt.wallet", netuid: int = None, network: str = 'local', chain_endpoint: str = 'ws://127.0.0.1:9944'):
        super().__init__(wallet)
        if netuid is None:
            raise ValueError("netuid is required")
        
        bt.logging.info(f"TaoilliumAPI wallet: {wallet}")
        bt.logging.info(f"TaoilliumAPI netuid: {netuid}")
        bt.logging.info(f"TaoilliumAPI network: {network}")
        bt.logging.info(f"TaoilliumAPI chain_endpoint: {chain_endpoint}")

        self.netuid = netuid
        self.name = "taoillium"
        
        # Create config for metagraph with chain_endpoint
        import argparse
        parser = argparse.ArgumentParser()
        bt.subtensor.add_args(parser)
        config = bt.config(parser)

        config.subtensor.network = network
        config.subtensor.chain_endpoint = chain_endpoint
        
        # Debug: Print the actual config values
        bt.logging.info(f"Config before subtensor creation:")
        bt.logging.info(f"  config.subtensor.network = {config.subtensor.network}")
        bt.logging.info(f"  config.subtensor.chain_endpoint = {config.subtensor.chain_endpoint}")
        
        # Force set environment variable to ensure Bittensor uses our chain_endpoint
        import os
        os.environ['BT_SUBTENSOR_CHAIN_ENDPOINT'] = chain_endpoint
        bt.logging.info(f"Set BT_SUBTENSOR_CHAIN_ENDPOINT={chain_endpoint}")
        
        # Debug: Check if environment variable is set correctly
        bt.logging.info(f"Environment BT_SUBTENSOR_CHAIN_ENDPOINT: {os.environ.get('BT_SUBTENSOR_CHAIN_ENDPOINT', 'NOT_SET')}")
        
        # Create subtensor and metagraph with config
        bt.logging.info(f"Creating subtensor with config: network={config.subtensor.network}, chain_endpoint={config.subtensor.chain_endpoint}")
        
        # Debug: Print all config values before creating subtensor
        bt.logging.info(f"Full config.subtensor values:")
        for attr in dir(config.subtensor):
            if not attr.startswith('_'):
                try:
                    value = getattr(config.subtensor, attr)
                    bt.logging.info(f"  {attr}: {value}")
                except:
                    pass
        
        self.subtensor = bt.subtensor(config=config)
        
        # Debug: Check what chain_endpoint the subtensor actually uses
        bt.logging.info(f"Subtensor created with chain_endpoint: {self.subtensor.chain_endpoint}")
        
        # Force override the chain_endpoint if it's wrong
        if self.subtensor.chain_endpoint != chain_endpoint:
            bt.logging.warning(f"Subtensor chain_endpoint mismatch! Expected: {chain_endpoint}, Got: {self.subtensor.chain_endpoint}")
            # Try to force set the chain_endpoint
            try:
                self.subtensor.chain_endpoint = chain_endpoint
                bt.logging.info(f"Force set subtensor chain_endpoint to: {self.subtensor.chain_endpoint}")
            except Exception as e:
                bt.logging.error(f"Failed to force set chain_endpoint: {e}")
        self.metagraph = self.subtensor.metagraph(netuid=self.netuid)
        
        # Log metagraph info
        bt.logging.info(f"Metagraph created: netuid={self.metagraph.netuid}, total_neurons={len(self.metagraph.axons)}")
        bt.logging.info(f"Metagraph network: {self.metagraph.network}")
        bt.logging.info(f"Metagraph block: {self.metagraph.block}")
        
        # Log some axon details for debugging
        serving_axons = [i for i, axon in enumerate(self.metagraph.axons) if axon.is_serving]
        bt.logging.info(f"Serving axons: {serving_axons}")
        if serving_axons:
            for uid in serving_axons[:3]:  # Show first 3 serving axons
                axon = self.metagraph.axons[uid]
                bt.logging.info(f"UID {uid}: {axon.ip}:{axon.port} (serving: {axon.is_serving})")
        
    def prepare_synapse(self, user_input: Dict[str, Any]) -> protocol.ServiceProtocol:
        """
        Prepare the synapse with user input for transit.
        
        Args:
            user_input: Dictionary containing the user's request data
            
        Returns:
            ServiceProtocol: Prepared synapse for network transmission
        """
        # Create and fill the synapse with user input
        synapse = protocol.ServiceProtocol(input=user_input)
        return synapse
        
    def process_responses(self, responses: List[Union["bt.Synapse", Any]]) -> List[Dict[str, Any]]:
        """
        Process responses from the network and extract relevant data.
        
        Args:
            responses: List of responses from network nodes
            
        Returns:
            List[Dict]: Processed and filtered responses
        """
        return responses
        
    async def query_network(self, user_input: Dict[str, Any], 
                           sample_size: int = 3, 
                           timeout: int = 30,
                           use_random_selection: bool = False) -> List[Dict[str, Any]]:
        """
        Query the network with user input and return processed responses.
        
        Args:
            user_input: User's request data
            sample_size: Number of nodes to query
            timeout: Request timeout in seconds
            use_random_selection: If True, use random selection like forward_with_input
            
        Returns:
            List[Dict]: Processed responses from network nodes
        """
        if user_input.get("uids"):
            uids = [int(uid) for uid in user_input["uids"]]
            axons = [self.metagraph.axons[uid] for uid in uids]
        else:
            if use_random_selection:
                # Use random selection like forward_with_input
                axons = await self.get_miner_uids_with_ping(sample_size)
                # Get UIDs by finding the index of each axon in the metagraph
                uids = []
                for axon in axons:
                    for uid in range(len(self.metagraph.axons)):
                        if self.metagraph.axons[uid] == axon:
                            uids.append(uid)
                            break
            else:
                # Get available axons to query (based on stake ranking)
                axons = await get_query_api_axons(
                    wallet=self.wallet,
                    metagraph=self.metagraph,
                    n=0.1,  # Top 10% of nodes by stake
                    timeout=timeout
                )
                # Get UIDs by finding the index of each axon in the metagraph
                uids = []
                for axon in axons:
                    for uid in range(len(self.metagraph.axons)):
                        if self.metagraph.axons[uid] == axon:
                            uids.append(uid)
                            break
        
        # Limit the number of axons to query
        if len(axons) > sample_size:
            axons = axons[:sample_size]
            uids = uids[:sample_size]
            
        if not axons:
            raise Exception("No available nodes found")

        user_input["uids"] = uids
        bt.logging.debug(f"query_network user_input: {user_input}")
        # Prepare the synapse
        synapse = self.prepare_synapse(user_input)
        
        # Temporarily fix axon IPs in the metagraph
        original_ips = self._fix_metagraph_axons(uids)
        
        try:
            # Get axons from metagraph (which now have fixed IPs)
            axons = [self.metagraph.axons[uid] for uid in uids]
            
            # Query the network with fixed axons
            responses = await self.dendrite(
                axons=axons,
                synapse=synapse,
                deserialize=True,
                timeout=timeout
            )
        finally:
            # Always restore original IPs
            self._restore_metagraph_axons(original_ips)
        bt.logging.info(f"axons: {axons}")
        bt.logging.info(f"Received responses: {responses}")
        # Process and return the responses
        return responses
        
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the network.
        
        Returns:
            Dict: Health status information
        """
        return await self.query_network(
            user_input={"__type__": "health"},
            sample_size=1,
            timeout=10
        ) 
    
    def get_miner_uids(self, sample_size: int = 3) -> List[Any]:
        """
        Get random miner axons (non-validators) from the metagraph.
        
        Args:
            sample_size: Number of miner axons to return
            
        Returns:
            List[Any]: List of miner axons
        """
        import random
        
        # First, try to get all non-validator UIDs that are serving
        non_validator_serving_uids = [
            uid for uid in range(len(self.metagraph.axons))
            if not self.metagraph.validator_permit[uid] and self.metagraph.axons[uid].is_serving
        ]
        bt.logging.debug(f"Non-validator serving UIDs: {non_validator_serving_uids}")
        
        # If we have non-validator serving nodes, use them
        if non_validator_serving_uids:
            miner_uids = non_validator_serving_uids
        else:
            # Special case: try to identify miners among serving validators
            # This handles cases where miners run on validator UIDs (like UID 2 in this case)
            serving_validator_uids = [
                uid for uid in range(len(self.metagraph.axons))
                if self.metagraph.validator_permit[uid] and self.metagraph.axons[uid].is_serving
            ]
            bt.logging.debug(f"Serving validator UIDs: {serving_validator_uids}")
            
            # For now, we'll include all serving validators as potential miners
            # In a production system, you might want to add more sophisticated detection
            # like pinging with a test request to see if they respond like miners
            miner_uids = serving_validator_uids
            
            # If still no miners, fall back to all non-validator nodes
            if not miner_uids:
                all_non_validator_uids = [
                    uid for uid in range(len(self.metagraph.axons))
                    if not self.metagraph.validator_permit[uid]
                ]
                bt.logging.debug(f"No serving nodes found, using all non-validator UIDs: {all_non_validator_uids}")
                miner_uids = all_non_validator_uids
        
        if not miner_uids:
            raise Exception("No available miners found")
        
        # Randomly sample the requested number of miners
        selected_uids = random.sample(miner_uids, min(sample_size, len(miner_uids)))
        bt.logging.debug(f"Selected miner UIDs: {selected_uids}")
        
        # Return axons instead of UIDs
        selected_axons = [self.metagraph.axons[uid] for uid in selected_uids]
        return selected_axons



    async def get_miner_uids_with_ping(self, sample_size: int = 3, timeout: int = 3) -> List[Any]:
        """Get miner axons with actual network connectivity test"""
        # Get candidate UIDs directly
        candidate_uids = self._get_miner_uids_list(sample_size * 2)  # get more candidates
        
        # ping test
        bt.logging.debug(f"Candidate UIDs: {candidate_uids}")
        successful_uids = await self.ping_uids(candidate_uids, timeout=timeout)
        bt.logging.debug(f"Successful UIDs: {successful_uids}")
        # Return successful axons
        return [self.metagraph.axons[uid] for uid in successful_uids[:sample_size]]

    def _get_miner_uids_list(self, sample_size: int = 3) -> List[int]:
        """Get random miner UIDs (not axons) from the metagraph."""
        import random
        
        # First, try to get all non-validator UIDs that are serving
        non_validator_serving_uids = [
            uid for uid in range(len(self.metagraph.axons))
            if not self.metagraph.validator_permit[uid] and self.metagraph.axons[uid].is_serving
        ]
        bt.logging.debug(f"Non-validator serving UIDs: {non_validator_serving_uids}")
        
        # If we have non-validator serving nodes, use them
        if non_validator_serving_uids:
            miner_uids = non_validator_serving_uids
        else:
            # Special case: try to identify miners among serving validators
            serving_validator_uids = [
                uid for uid in range(len(self.metagraph.axons))
                if self.metagraph.validator_permit[uid] and self.metagraph.axons[uid].is_serving
            ]
            bt.logging.debug(f"Serving validator UIDs: {serving_validator_uids}")
            
            # For now, we'll include all serving validators as potential miners
            miner_uids = serving_validator_uids
            
            # If still no miners, fall back to all non-validator nodes
            if not miner_uids:
                all_non_validator_uids = [
                    uid for uid in range(len(self.metagraph.axons))
                    if not self.metagraph.validator_permit[uid]
                ]
                bt.logging.debug(f"No serving nodes found, using all non-validator UIDs: {all_non_validator_uids}")
                miner_uids = all_non_validator_uids
        
        if not miner_uids:
            raise Exception("No available miners found")
        
        # Randomly sample the requested number of miners
        selected_uids = random.sample(miner_uids, min(sample_size, len(miner_uids)))
        bt.logging.debug(f"Selected miner UIDs: {selected_uids}")
        
        # Return UIDs directly
        return selected_uids

    async def ping_uids(self, uids, timeout=10):
        # Temporarily fix axon IPs in the metagraph
        original_ips = self._fix_metagraph_axons(uids)
        
        try:
            axons = [self.metagraph.axons[uid] for uid in uids]
            
            # Debug: Print axon details before pinging
            bt.logging.debug(f"Pinging axons:")
            for uid, axon in zip(uids, axons):
                bt.logging.debug(f"  UID {uid}: {axon.ip}:{axon.port} (serving: {axon.is_serving})")
            
            # Debug: Check what we're passing to dendrite
            bt.logging.debug(f"Passing {len(axons)} axons to dendrite:")
            for i, axon in enumerate(axons):
                bt.logging.debug(f"  Dendrite axon {i}: {axon.ip}:{axon.port}")
            
            responses = await self.dendrite(axons, bt.Synapse(), deserialize=False, timeout=timeout)
        finally:
            # Always restore original IPs
            self._restore_metagraph_axons(original_ips)
        
        # Debug: Print response details
        for uid, response in zip(uids, responses):
            if hasattr(response, 'dendrite') and hasattr(response.dendrite, 'status_code'):
                bt.logging.debug(f"  UID {uid}: status_code={response.dendrite.status_code}")
            else:
                bt.logging.debug(f"  UID {uid}: no status_code attribute")
        
        # only return successful uids
        successful_uids = [
            uid for uid, response in zip(uids, responses)
            if hasattr(response, 'dendrite') and hasattr(response.dendrite, 'status_code') and response.dendrite.status_code == 200
        ]
        
        bt.logging.debug(f"Successful UIDs: {successful_uids}")
        return successful_uids

    def _get_fixed_axons(self, axons):
        """
        Temporarily fix axon IPs for dendrite calls without modifying metagraph
        The root cause of this is that the axon IPs are 0.0.0.0 when the manager is running on the same server as the axon.
        code is from /bittensor/core/dendrite.py:_get_endpoint_url https://github.com/opentensor/bittensor/blob/master/bittensor/core/dendrite.py#L239
        """
        import copy
        fixed_axons = []
        
        bt.logging.debug(f"_get_fixed_axons called with {len(axons)} axons")
        
        for i, axon in enumerate(axons):
            bt.logging.debug(f"Original axon {i}: {axon.ip}:{axon.port}")
            
            # Debug: Check all attributes of the axon object
            bt.logging.debug(f"Axon {i} attributes: {dir(axon)}")
            bt.logging.debug(f"Axon {i} __dict__: {axon.__dict__}")
            bt.logging.debug(f"Axon {i} ip_str: {getattr(axon, 'ip_str', 'N/A')}")
            
            # Only fix IP if it's 0.0.0.0 (which means it's on the same server as manager)
            if axon.ip == "0.0.0.0":
                local_ip = get_local_ip()  # Manager's public IP
                # Create a new axon object with the fixed IP
                fixed_axon = bt.axon(
                    ip=local_ip,
                    port=axon.port,
                    ip_type=axon.ip_type,
                    protocol=axon.protocol
                )
                bt.logging.debug(f"Temporarily fixing axon IP from 0.0.0.0 to {fixed_axon.ip} (get_local_ip returned: {local_ip})")
            else:
                # Create a copy to avoid modifying the original metagraph
                fixed_axon = copy.deepcopy(axon)
                bt.logging.debug(f"Axon {i} IP {fixed_axon.ip} is not 0.0.0.0, no fix needed")
            
            fixed_axons.append(fixed_axon)
        
        bt.logging.debug(f"Returning {len(fixed_axons)} fixed axons")
        return fixed_axons

    def _fix_metagraph_axons(self, uids):
        """Temporarily fix axon IPs in the metagraph for the given UIDs"""
        bt.logging.debug(f"_fix_metagraph_axons called with UIDs: {uids}")
        
        # Store original IPs to restore later
        original_ips = {}
        
        # Get dendrite's external IP to check for conflicts
        dendrite_external_ip = getattr(self.dendrite, 'external_ip', None)
        bt.logging.debug(f"Dendrite external_ip: {dendrite_external_ip}")
        
        # Store original dendrite external_ip to restore later
        original_dendrite_external_ip = dendrite_external_ip
        
        for uid in uids:
            axon = self.metagraph.axons[uid]
            bt.logging.debug(f"UID {uid} axon IP: {axon.ip}")
            
            # Fix IP if it's 0.0.0.0 or if it conflicts with dendrite's external_ip
            if axon.ip == "0.0.0.0" or (dendrite_external_ip and axon.ip == str(dendrite_external_ip)):
                # Temporarily change dendrite's external_ip to avoid conflict
                if hasattr(self.dendrite, 'external_ip'):
                    self.dendrite.external_ip = "127.0.0.1"  # Use localhost to avoid conflict
                    bt.logging.debug(f"Temporarily changed dendrite external_ip from {original_dendrite_external_ip} to {self.dendrite.external_ip}")
                original_ips[uid] = axon.ip
                bt.logging.debug(f"Detected IP conflict for UID {uid}: axon.ip={axon.ip}, original dendrite.external_ip={original_dendrite_external_ip}")
            else:
                bt.logging.debug(f"Metagraph axon UID {uid} IP {axon.ip} is not 0.0.0.0 and doesn't conflict with dendrite external_ip, no fix needed")
        
        # Store the original dendrite external_ip in the return dict with a special key
        original_ips['_dendrite_external_ip'] = original_dendrite_external_ip
        
        return original_ips

    def _restore_metagraph_axons(self, original_ips):
        """Restore original axon IPs in the metagraph and dendrite external_ip"""
        # Restore dendrite external_ip if it was modified
        if '_dendrite_external_ip' in original_ips:
            original_dendrite_external_ip = original_ips['_dendrite_external_ip']
            if hasattr(self.dendrite, 'external_ip'):
                self.dendrite.external_ip = original_dendrite_external_ip
                bt.logging.debug(f"Restored dendrite external_ip to {original_dendrite_external_ip}")
        
        # Restore axon IPs
        for uid, original_ip in original_ips.items():
            if uid != '_dendrite_external_ip':  # Skip the special key
                self.metagraph.axons[uid].ip = original_ip
                bt.logging.debug(f"Restored metagraph axon UID {uid} IP to {original_ip}")