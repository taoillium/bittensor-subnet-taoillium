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
from services.security import verify_token
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
        self.http_thread = None
        self.http_app = None
        
        self.start_http_server()
        # TODO(developer): Anything specific to your use case you can do here

    def start_http_server(self):
        """start FastAPI HTTP server"""
        app = FastAPI()
        validator_self = self

        @app.post("/task/receive")
        async def receive(request: Request):
            token = request.headers.get("Authorization", "")
            if not verify_token(token):
                return {"error": "Unauthorized"}
            
            data = await request.json()
            if data is None:
                return {"error": "Missing 'input' in request body"}
            # here use run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(
                validator_self.forward_with_input(data), validator_self.loop
            )
            responses = future.result()
            return responses
        
        @app.post("/stake/add")
        async def stake_add(request: Request):
            token = request.headers.get("Authorization", "")
            if not verify_token(token):
                return {"error": "Unauthorized"}
            data = await request.json()
            amount = data.get("amount")
            try:
                amount = float(amount)
                if amount <= 0:
                    return {"error": "Amount must be greater than 0"}
            except (TypeError, ValueError):
                return {"error": "Amount must be a valid number"}
            future = asyncio.run_coroutine_threadsafe(
                validator_self.stake_add(amount), validator_self.loop
            )
            responses = future.result()
            return responses

        def run():
            uvicorn.run(app, host=settings.VALIDATOR_HOST, port=settings.VALIDATOR_PORT, log_level="info")

        self.http_app = app
        self.http_thread = threading.Thread(target=run, daemon=True)
        self.http_thread.start()
        bt.logging.info(f"HTTP server started on port {settings.VALIDATOR_PORT}")

    async def stake_add(self, amount):
        result = self.subtensor.add_stake(
            wallet=self.wallet,
            netuid=self.config.netuid,
            amount=amount,
            wait_for_finalization=True
        )
        bt.logging.info(f"Stake add result: {result}")
        return {
            "success": result,
            "message": None if result else "Stake failed, see logs for details."
        }

    async def forward_with_input(self, user_input):
        miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
        # Filter out validator's own uid
        bt.logging.info(f"Miner uids: {miner_uids}, validator uid: {self.uid}")
        miner_uids = [uid for uid in miner_uids if uid != self.uid]
        if not miner_uids:
            return {"error": "No available miners found"}
            
        responses = await self.dendrite(
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            synapse=protocol.ServiceProtocol(input=user_input),
            deserialize=True,
        )
        bt.logging.info(f"[HTTP] Raw responses: {responses}")
        # only return non-empty responses
        outputs = [r for r in responses if r]
        return outputs

    async def forward(self, synapse: protocol.ServiceProtocol) -> protocol.ServiceProtocol:
        """
        The forward function is called by the validator every time step.

        It is responsible for querying the network and scoring the responses.

        Args:
            self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

        """
        # TODO(developer): Define how the validator selects a miner to query, how often, etc.
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

        client = ValidatorClient(self.uid)
        # Log the results for monitoring purposes.
        data = {"uids": uids, "uid": int(self.uid), "responses": responses}
        bt.logging.debug(
            f"request node/task/validate: {data}"
        )
        result = client.post("/sapi/node/task/validate", json=data)
        bt.logging.debug(f"Validate result: {result}")
        values = result.get('values', [])
        total = sum(values)
        if result.get("error"):
            bt.logging.error(f"Validate error: {result.get('error')}")
        elif len(values) == len(uids) and result['uids'] == uids and total > 0:
            rewards = [x / total for x in values]
            bt.logging.debug(f"Scored responses: {rewards}")
            # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
            bt.logging.debug(f"Updating scores: {rewards}, {miner_uids}")
            self.update_scores(rewards, miner_uids)
        else:
            bt.logging.error(f"Validate failed, invalid result: {result}")
        
        synapse.output = result
        time.sleep(settings.VALIDATOR_SLEEP_TIME)
        return synapse
    

    async def concurrent_forward(self):
        coroutines = [
            self.forward(protocol.ServiceProtocol(input={"__type__": "health"}))
            for _ in range(self.config.neuron.num_concurrent_forwards)
        ]
        await asyncio.gather(*coroutines)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)
