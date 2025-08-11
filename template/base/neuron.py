# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

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

import copy
import typing
import time
import bittensor as bt
import os
import signal
import sys

from abc import ABC, abstractmethod

# Sync calls set weights and also resyncs the metagraph.
from template.utils.config import check_config, add_args, config
from template.utils.misc import ttl_get_block
from template import __spec_version__ as spec_version
from template.mock import MockSubtensor, MockMetagraph
from websockets.protocol import State as WebSocketClientState
from services.config import settings
from services.api import ServiceApiClient
from services.security import create_neuron_access_token


class BaseNeuron(ABC):
    """
    Base class for Bittensor miners. This class is abstract and should be inherited by a subclass. It contains the core logic for all neurons; validators and miners.

    In addition to creating a wallet, subtensor, and metagraph, this class also handles the synchronization of the network state via a basic checkpointing mechanism based on epoch length.
    """

    neuron_type: str = "BaseNeuron"

    @classmethod
    def check_config(cls, config: "bt.Config"):
        check_config(cls, config)

    @classmethod
    def add_args(cls, parser):
        add_args(cls, parser)

    @classmethod
    def config(cls):
        return config(cls)

    subtensor: "bt.subtensor"
    wallet: "bt.wallet"
    metagraph: "bt.metagraph"
    spec_version: int = spec_version

    @property
    def block(self):
        return ttl_get_block(self)

    def __init__(self, config=None):
        base_config = copy.deepcopy(config or BaseNeuron.config())
        self.config = self.config()
        self.config.merge(base_config)
        self.check_config(self.config)

        # Set up logging with the provided configuration.
        bt.logging.set_config(config=self.config.logging)

        # If a gpu is required, set the device to cuda:N (e.g. cuda:0)
        self.device = self.config.neuron.device

        # Log the configuration for reference.
        bt.logging.info(self.config)

        # Build Bittensor objects
        # These are core Bittensor classes to interact with the network.
        bt.logging.info("Setting up bittensor objects.")

        # The wallet holds the cryptographic key pairs for the miner.
        if self.config.mock:
            self.wallet = bt.MockWallet(config=self.config)
            self.subtensor = MockSubtensor(
                self.config.netuid, wallet=self.wallet
            )
            self.metagraph = MockMetagraph(
                self.config.netuid, subtensor=self.subtensor
            )
        else:
            self.wallet = bt.wallet(config=self.config)
            self.subtensor = bt.subtensor(config=self.config)
            self.metagraph = self.subtensor.metagraph(self.config.netuid)

        bt.logging.info(f"Wallet: {self.wallet}")
        # bt.logging.info(f"Coldkey Address: {self.wallet.coldkey.ss58_address}")
        bt.logging.info(f"Hotkey Address: {self.wallet.hotkey.ss58_address}")
        bt.logging.info(f"Subtensor: {self.subtensor}")
        bt.logging.info(f"Metagraph: {self.metagraph}")

        my_srv_api_key = f"SRV_API_KEY_{self.wallet.hotkey.ss58_address}"
        self.current_api_key_name = None
        self.current_api_key_value = None
        
        if os.getenv(my_srv_api_key):
            settings.SRV_API_KEY = os.getenv(my_srv_api_key)
            self.current_api_key_value = settings.SRV_API_KEY
            self.current_api_key_name = my_srv_api_key
            bt.logging.info(f"Using SRV_API_KEY from environment variable: {my_srv_api_key}")
        elif os.getenv("SRV_API_KEY"):
            self.current_api_key_value = os.getenv("SRV_API_KEY")
            self.current_api_key_name = "SRV_API_KEY"
            bt.logging.info("Using SRV_API_KEY from environment variable: SRV_API_KEY")

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

        # Check if the miner is registered on the Bittensor network before proceeding further.
        self.check_registered()

        # Each miner gets a unique identity (UID) in the network for differentiation.
        self.uid = self.metagraph.hotkeys.index(
            self.wallet.hotkey.ss58_address
        )
        bt.logging.info(
            f"Running neuron on subnet: {self.config.netuid} with type {self.neuron_type} uid {self.uid} using network: {self.subtensor.chain_endpoint}"
        )
        self.step = 0

        self.last_neuron_registration_expire = time.time() +  600  # 10 minutes from now
        self.last_service_token_expire = time.time() +  600  # 10 minutes from now

        # Set epoch length from chain during initialization
        self._set_epoch_length_from_chain()

        self._login_to_business_server()

    def _login_to_business_server(self):
        login_time = int(time.time()*1000)
        signature = self.wallet.hotkey.sign(data=str(login_time))
        
        # Convert signature from bytes to hex string for JSON serialization
        signature_hex = signature.hex() if isinstance(signature, bytes) else str(signature)
        
        sign_result = {
            "signature": signature_hex,
            "message": login_time,
            "ss58Address": self.wallet.hotkey.ss58_address,
            "timestamp": login_time,
            "type": "web3_"+self.neuron_type,
        }

        bt.logging.debug(f"Sign result: {sign_result}")
        try:
            client = ServiceApiClient(self.current_api_key_value)
            result = client.post("/auth/tao/login", json=sign_result)
            if result.get("nodeToken"):
                self.current_api_key_value = result.get("nodeToken").get("access_token")
                self.last_service_token_expire = result.get("nodeToken").get("exp")
                bt.logging.info(f"Using NODE_TOKEN from business server, expires at: {self.last_service_token_expire}")
            else:
                bt.logging.error(f"Failed to login to business server: {result}")
        except Exception as e:
            bt.logging.error(f"Failed to login to business server: {e}")


    def _set_epoch_length_from_chain(self):
        """
        Sets the epoch length from the chain using subtensor.tempo() during initialization.
        Updates self.config.neuron.epoch_length with the chain value.
        """
        try:
            chain_tempo = self.subtensor.tempo(netuid=self.config.netuid)
            if chain_tempo is not None and chain_tempo <= self.config.neuron.epoch_length:
                self.config.neuron.epoch_length = chain_tempo
                bt.logging.info(f"Set epoch length from chain: {chain_tempo} blocks for netuid {self.config.netuid}")
            elif chain_tempo is not None:
                bt.logging.info(f"Chain tempo ({chain_tempo}) > config epoch_length ({self.config.neuron.epoch_length}), using config value for more frequent weight updates")
            else:
                bt.logging.warning(f"Could not retrieve tempo from chain for netuid {self.config.netuid}, using config default: {self.config.neuron.epoch_length}")
        except Exception as e:
            bt.logging.warning(f"Failed to query epoch length from chain: {e}, using config default: {self.config.neuron.epoch_length}")

    def set_subtensor(self):
        try:
            if (
                self.subtensor
                and self.subtensor.substrate
                and self.subtensor.substrate.ws
                and self.subtensor.substrate.ws.state is WebSocketClientState.OPEN
            ):
                # bt.logging.debug(
                #     f"Subtensor already set"
                # )
                return

            bt.logging.info(
                f"Getting subtensor"
            )

            self.subtensor = bt.subtensor(config=self.config)

            # check registered
            self.check_registered()
        except Exception as e:
            bt.logging.info(
                f"[Error] Getting subtensor: {e}"
            )

    @abstractmethod
    async def forward(self, synapse: bt.Synapse) -> bt.Synapse:
        ...


    @abstractmethod
    def run(self):
        ...

    def sync(self):
        """
        Wrapper for synchronizing the state of the network for the given miner or validator.
        """
        self.set_subtensor()

        # Ensure miner or validator hotkey is still registered on the network.
        self.check_registered()

        if self.should_sync_metagraph():
            self.resync_metagraph()

        if self.should_set_weights():
            self.set_weights()

        # Always save state.
        self.save_state()

        self.refresh_business_server_access()


    def check_registered(self):
        # --- Check for registration.
        if not self.subtensor.is_hotkey_registered(
            netuid=self.config.netuid,
            hotkey_ss58=self.wallet.hotkey.ss58_address,
        ):
            bt.logging.error(
                f"Wallet: {self.wallet} is not registered on netuid {self.config.netuid}."
                f" Please register the hotkey using `btcli subnets register` before trying again"
            )
            exit()

    def get_epoch_length(self) -> int:
        """
        Returns the epoch length in blocks.
        This value is set during initialization from the chain.
        
        Returns:
            int: The epoch length in blocks
        """
        return self.config.neuron.epoch_length

    def should_sync_metagraph(self):
        """
        Check if enough epoch blocks have elapsed since the last checkpoint to sync.
        """
        bt.logging.trace(f"block: {self.block}, last_update: {self.metagraph.last_update[self.uid]}, epoch_length: {self.get_epoch_length()}")
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.get_epoch_length()

    def should_set_weights(self) -> bool:
        # Don't set weights on initialization.
        if self.step == 0:
            return False

        # Check if enough epoch blocks have elapsed since the last epoch.
        if self.config.neuron.disable_set_weights:
            return False

        # Define appropriate logic for when set weights.
        return (
            (self.block - self.metagraph.last_update[self.uid])
            > self.get_epoch_length()
            # and self.neuron_type != "miner"
        )  # don't set weights if you're a miner

    def save_state(self):
        bt.logging.trace(
            "save_state() not implemented for this neuron. You can implement this function to save model checkpoints or other useful data."
        )

    def load_state(self):
        bt.logging.trace(
            "load_state() not implemented for this neuron. You can implement this function to load model checkpoints or other useful data."
        )

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals and record API key to .env file"""
        bt.logging.info(f"Received signal {signum}, shutting down gracefully...")
        bt.logging.info(f"Current API key name: {self.current_api_key_name}")
        bt.logging.info(f"Current API key value: {'*' * len(self.current_api_key_value) if self.current_api_key_value else 'None'}")
        settings.record_api_key_to_env(self.current_api_key_name, self.current_api_key_value)
        sys.exit(0)


    def refresh_business_server_access(self):
        """Refresh both neuron registration and service access tokens from business server"""
        try:
            # Check if we have an API key to use
            if not self.current_api_key_value:
                bt.logging.warning("No API key available for business server registration")
                return

            # Check if either token needs refresh (5 minutes before expiration)
            token_refresh_interval = min(settings.NEURON_JWT_EXPIRE_IN * 60, 300)  # Convert to seconds
            neuron_token_expired = (self.last_neuron_registration_expire - time.time()) < token_refresh_interval
            service_token_expired = (self.last_service_token_expire - time.time()) < token_refresh_interval
            
            if not (neuron_token_expired or service_token_expired):
                bt.logging.debug(f"Both tokens still valid, skipping refresh")
                return

            # Prepare neuron registration data with authentication token
            data = {
                "uid": self.uid, 
                "chain": "bittensor", 
                "netuid": self.config.netuid, 
                "type": self.neuron_type, 
                "account": self.wallet.hotkey.ss58_address
            }
            # Create authentication token for business server access
            data["token"] = create_neuron_access_token(data=data)
            
            # Register neuron with business server and get both tokens
            # This is the correct approach - registration includes token exchange
            client = ServiceApiClient(self.current_api_key_value)
            result = client.post("/sapi/node/neuron/register", json=data)
            bt.logging.debug(f"Register with business server result: {result}")
            
            if result.get("success"):
                # Update both token expiration times
                self.last_neuron_registration_expire = time.time() + settings.NEURON_JWT_EXPIRE_IN * 60
                
                # Update service token if returned
                if result.get("access_token") and result.get("exp"):
                    self.last_service_token_expire = result.get("exp")
                    self.current_api_key_value = result.get("access_token")
                    settings.SRV_API_KEY = self.current_api_key_value
                    bt.logging.debug(f"Service token refreshed, expires at: {result.get('exp')}")
            else:
                bt.logging.error(f"Failed to register with business server: {result}")
        except Exception as e:
            bt.logging.error(f"Failed to refresh business server access: {e}")