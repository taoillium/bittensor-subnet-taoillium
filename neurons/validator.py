# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2025 Taoillium Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import time
import threading
from fastapi import FastAPI, Request
import uvicorn
import asyncio

# Bittensor
import bittensor as bt

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron

from template.validator.reward import get_rewards
from template.utils.uids import get_random_uids
import services.protocol as protocol
from services.config import settings
from services.api import ServiceApiClient


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super().__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()
        

    async def forward(self, synapse: protocol.ServiceProtocol) -> protocol.ServiceProtocol:
        """
        The forward function is called by the validator every time step.

        It is responsible for querying the network and scoring the responses.

        Args:
            self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

        """
        bt.logging.debug(f"Validator forward synapse.input: {synapse}")
        if synapse.input.get("__type__") == "miner":
            synapse.output = {"error": "validator skip miner task", "uid": self.uid}
            return synapse
        elif synapse.input.get("__type__") == "health":
            bt.logging.info(f"Validator health synapse.input: {synapse.input})")
            synapse.output = {"method": "health", "success": True, "uid": self.uid, "device": self.device}
        elif synapse.input.get("__type__") == "ping":
            bt.logging.debug(f"Validator ping synapse.input: {synapse.input})")

        client = ServiceApiClient(self.current_api_key_value)

        picked_uids = []
        try:
            result = client.get("/sapi/node/neuron/list", params={"flag": "dex-pool-validator,dex-pool-miner"})
            if result:
                picked_uids = self._filter_valid_axons([int(item["channel"]) for item in result])
                bt.logging.debug(f"Api picked uids: {picked_uids}")
        except Exception as e:
            bt.logging.error(f"ServiceApiClient call failed: {e}")

        # get_random_uids is an example method, but you can replace it with your own.
        if not picked_uids:
            random_uids = get_random_uids(self, k=self.config.neuron.sample_size)
            picked_uids = self._filter_valid_axons(random_uids)
            bt.logging.debug(f"random picked uids: {picked_uids}")
       
        # Filter out validator's own uid and convert to Python int
        checked_uids = [int(uid) for uid in picked_uids if uid != self.uid]
        if not checked_uids:
            bt.logging.warning("No available nodes found after filtering")
            synapse.output = {"error": "No available nodes found"}
            await asyncio.sleep(settings.VALIDATOR_SLEEP_TIME)
            return synapse

        bt.logging.debug(f"Validator forward uids: {checked_uids}, validator uid: {self.uid}, synapse: {synapse}")
        # The dendrite client queries the network with proper timeout handling.
        responses = []
        
        # Query each axon individually with simplified approach
        for uid in checked_uids:
            try:
                axon = self.metagraph.axons[uid]
                
                # Use simple dendrite call with error handling
                response = await self.dendrite(
                    axons=[axon],
                    synapse=synapse,
                    deserialize=True,
                    timeout=8.0,
                )
                
                if response and len(response) > 0:
                    responses.extend(response)
                else:
                    mock_response = {"method": "ping", "success": False, "uid": uid, "error": "empty_response"}
                    responses.append(mock_response)
                    
            except Exception as e:
                bt.logging.debug(f"Dendrite call failed for uid {uid}: {e}")
                mock_response = {"method": "ping", "success": False, "uid": uid, "error": str(e)}
                responses.append(mock_response)

        
        # Ensure responses is a list even if dendrite call failed
        if not isinstance(responses, list):
            responses = []
        
        # Add validator's own response
        responses.append({"method": "ping", "success": True, "uid": self.uid})
        
        # Create uids list matching responses
        uids = checked_uids.copy()  # Already converted to Python int
        uids.append(self.uid)
        
        # Log summary of responses
        successful_responses = [r for r in responses if r.get("success", False)]
        failed_responses = [r for r in responses if not r.get("success", True)]
        bt.logging.debug(f"Dendrite summary: {len(successful_responses)} successful, {len(failed_responses)} failed")

        # Log the results for monitoring purposes.
        data = {"uids": uids, "responses": responses, "chain": "bittensor", "uid": int(self.uid), "netuid": self.config.netuid}
        bt.logging.debug(
            f"request node/task/validate: {data}"
        )
        try:
            result = client.post("/sapi/node/task/validate", json=data)
        except Exception as e:
            bt.logging.error(f"ServiceApiClient call failed: {e}")
            result = {"error": str(e), "values": [], "uids": uids}
        bt.logging.debug(f"Validate result: {result}")
        values = result.get('values', [])
        total = sum(values)
        if result.get("error"):
            bt.logging.error(f"Validate error: {result.get('error')}")
            
        if len(values) == len(uids) and result.get('uids') == uids and total > 0:
            # Use the calculated rewards when validation conditions are met
            rewards = [x / total for x in values]
            bt.logging.debug(f"Scored responses: {rewards}")
            bt.logging.debug(f"Updating scores: {rewards}, {picked_uids}")
            self.update_scores(rewards, picked_uids)
        else:
            # When validation conditions are not met, use empty rewards (will trigger stake-only scoring)
            bt.logging.warning(f"Validation conditions not met, using stake-only scoring. Result: {result}")
            empty_rewards = [0.0] * len(picked_uids)  # Empty rewards to trigger stake-only mode
            bt.logging.debug(f"Empty rewards: {empty_rewards}")
            bt.logging.debug(f"Updating scores with stake-only rewards: {picked_uids}")
            self.update_scores(empty_rewards, picked_uids)
        
        synapse.output = result
        # Use asyncio.sleep instead of time.sleep in async function
        await asyncio.sleep(settings.VALIDATOR_SLEEP_TIME)
        return synapse

    def _filter_valid_axons(self, uids):
        """
        Filter out UIDs with invalid axon configurations (0.0.0.0:0).
        
        Args:
            uids: List of UIDs to filter
            
        Returns:
            List of UIDs with valid axon configurations
        """
        valid_uids = []
        for uid in uids:
            uid_int = int(uid)
            axon = self.metagraph.axons[uid_int]
            if axon.ip == "0.0.0.0" or axon.port == 0:
                bt.logging.debug(f"Skipping invalid axon for uid {uid_int}: {axon.ip}:{axon.port}")
            else:
                valid_uids.append(uid_int)
        return valid_uids
    

    async def concurrent_forward(self):
        # For finney network, run forwards sequentially to avoid event loop issues
        try:
            await self.forward(protocol.ServiceProtocol(input={"__type__": "ping"}))
        except Exception as e:
            bt.logging.error(f"Forward call failed: {e}")


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        # The validator is now running in a background thread
        # We just need to keep the main thread alive
        try:
            # Keep the main thread running to allow the background validator to operate
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            bt.logging.info("Validator stopped by user")
