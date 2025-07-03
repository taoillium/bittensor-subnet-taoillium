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


class TaoilliumAPI(SubnetsAPI):
    """
    Standardized API client for Taoillium subnet.
    This class provides a clean interface for external clients to interact with the subnet.
    """
    
    def __init__(self, wallet: "bt.wallet", netuid: int = None, network: str = "local"):
        super().__init__(wallet)
        if netuid is None:
            raise ValueError("netuid is required")
        self.netuid = netuid
        self.name = "taoillium"
        self.metagraph = bt.metagraph(netuid=self.netuid, network=network)
        
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
            axons = [self.metagraph.axons[int(uid)] for uid in user_input["uids"]]
        else:
            if use_random_selection:
                # Use random selection like forward_with_input
                axons = await self.get_miner_uids_with_ping(sample_size)
            else:
                # Get available axons to query (based on stake ranking)
                axons = await get_query_api_axons(
                    wallet=self.wallet,
                    metagraph=self.metagraph,
                    n=0.1,  # Top 10% of nodes by stake
                    timeout=timeout
                )
        
        # Limit the number of axons to query
        if len(axons) > sample_size:
            axons = axons[:sample_size]
            
        if not axons:
            raise Exception("No available nodes found")

        bt.logging.debug(f"query_network user_input: {user_input}")
        # Prepare the synapse
        synapse = self.prepare_synapse(user_input)
        
        # Query the network
        responses = await self.dendrite(
            axons=axons,
            synapse=synapse,
            deserialize=True,
            timeout=timeout
        )
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

    async def ping_uids(self, uids, timeout=3):
        axons = [self.metagraph.axons[uid] for uid in uids]
        responses = await self.dendrite(axons, bt.Synapse(), deserialize=False, timeout=timeout)
        
        # only return successful uids
        return [
            uid for uid, response in zip(uids, responses)
            if response.dendrite.status_code == 200
        ]