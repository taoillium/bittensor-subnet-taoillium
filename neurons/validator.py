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
from services.security import verify_neuron_token,create_neuron_access_token
from services.api import ValidatorClient


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
        

    def register_with_business_server(self):
        """Register this neuron with the business server to establish authentication"""
        data = {"uid": self.uid, "chain": "bittensor", "netuid": self.config.netuid, "type": "validator", "account": self.wallet.hotkey.ss58_address}
        data["token"] = create_neuron_access_token(data=data)
        client = ValidatorClient()
        result = client.post("/sapi/node/neuron/register", json=data)
        bt.logging.info(f"Register with business server result: {result}")
        # Store registration time for token refresh tracking
        self.last_token_refresh = time.time()

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

        # get_random_uids is an example method, but you can replace it with your own.
        miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
       
        # Filter out validator's own uid and convert to Python int
        checked_uids = [int(uid) for uid in miner_uids if uid != self.uid]
        if not checked_uids:
            bt.logging.warning("No available nodes found after filtering")
            synapse.output = {"error": "No available nodes found"}
            time.sleep(settings.VALIDATOR_SLEEP_TIME)
            return synapse

        bt.logging.debug(f"Validator forward uids: {checked_uids}, validator uid: {self.uid}, synapse: {synapse}")
        # The dendrite client queries the network.
        responses = await self.dendrite(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in checked_uids],
            # Construct a dummy query. This simply contains a single integer.
            synapse=synapse,
            # All responses have the deserialize function called on them before returning.
            # You are encouraged to define your own deserialization function.
            deserialize=True,
        )

        
        responses.append({"method": "health", "success": True, "uid": self.uid, "device": self.device})
        
        uids = checked_uids  # Already converted to Python int
        uids.append(self.uid)

        client = ValidatorClient()
        # Log the results for monitoring purposes.
        data = {"uids": uids, "responses": responses, "chain": "bittensor", "uid": int(self.uid), "netuid": self.config.netuid}
        bt.logging.debug(
            f"request node/task/validate: {data}"
        )
        result = client.post("/sapi/node/task/validate", json=data)
        bt.logging.debug(f"Validate result: {result}")
        values = result.get('values', [])
        total = sum(values)
        if result.get("error"):
            bt.logging.error(f"Validate error: {result.get('error')}")
            
        if len(values) == len(uids) and result.get('uids') == uids and total > 0:
            # Use the calculated rewards when validation conditions are met
            rewards = [x / total for x in values]
            bt.logging.debug(f"Scored responses: {rewards}")
            bt.logging.debug(f"Updating scores: {rewards}, {miner_uids}")
            self.update_scores(rewards, miner_uids)
        else:
            # When validation conditions are not met, use empty rewards (will trigger stake-only scoring)
            bt.logging.warning(f"Validation conditions not met, using stake-only scoring. Result: {result}")
            empty_rewards = [0.0] * len(miner_uids)  # Empty rewards to trigger stake-only mode
            bt.logging.debug(f"Empty rewards: {empty_rewards}")
            bt.logging.debug(f"Updating scores with stake-only rewards: {miner_uids}")
            self.update_scores(empty_rewards, miner_uids)
        
        synapse.output = result
        time.sleep(settings.VALIDATOR_SLEEP_TIME)
        return synapse
    

    async def concurrent_forward(self):
        coroutines = [
            self.forward(protocol.ServiceProtocol(input={"__type__": "health"}))
            for _ in range(self.config.neuron.num_concurrent_forwards)
        ]
        await asyncio.gather(*coroutines)

    def sync(self):
        """
        Wrapper for synchronizing the state of the network for the given validator.
        Includes business server token refresh.
        """
        self.set_subtensor()

        # Ensure validator hotkey is still registered on the network.
        self.check_registered()

        # Refresh business server token if needed
        self.refresh_business_server_token()

        if self.should_sync_metagraph():
            self.resync_metagraph()

        if self.should_set_weights():
            self.set_weights()

        # Always save state.
        self.save_state()


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)
