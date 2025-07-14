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


import copy
import numpy as np
import asyncio
import argparse
import threading
import bittensor as bt
import time
import traceback
import requests
import json
import os

from typing import List, Union
from abc import ABC, abstractmethod

from template.base.neuron import BaseNeuron
from template.base.utils.weight_utils import (
    process_weights_for_netuid,
    convert_weights_and_uids_for_emit,
)  # TODO: Replace when bittensor switches to numpy
from template.mock import MockDendrite
from template.utils.config import add_validator_args
from template.utils.misc import ttl_get_block


class BaseValidatorNeuron(BaseNeuron):
    """
    Base class for Bittensor validators. Your validator should inherit from this class.
    """

    neuron_type: str = "validator"

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        add_validator_args(cls, parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        # Save a copy of the hotkeys to local memory.
        self.hotkeys = copy.deepcopy(self.metagraph.hotkeys)

        # Dendrite lets us send messages to other nodes (axons) in the network.
        if self.config.mock:
            self.dendrite = MockDendrite(wallet=self.wallet)
        else:
            self.dendrite = bt.dendrite(wallet=self.wallet)
        bt.logging.info(f"Dendrite: {self.dendrite}")

        # Set up initial scoring weights for validation
        bt.logging.info("Building validation weights.")
        self.scores = np.zeros(self.metagraph.n, dtype=np.float32)

        # Init sync with the network. Updates the metagraph.
        self.sync()

        # Serve axon to enable external connections.
        if not self.config.neuron.axon_off:
            self.serve_axon()
        else:
            bt.logging.warning("axon off, not serving ip to chain.")

        # Create asyncio event loop to manage async tasks.
        self.loop = asyncio.get_event_loop()

        # Instantiate runners
        self.should_exit: bool = False
        self.is_running: bool = False
        self.thread: Union[threading.Thread, None] = None
        self.lock = asyncio.Lock()

    def serve_axon(self):
        """Serve axon to enable external connections."""

        bt.logging.info("serving ip to chain...")
        try:
            self.axon = bt.axon(wallet=self.wallet, config=self.config)
             # Attach determiners which functions are called when servicing a request.
            bt.logging.info(f"Attaching forward function to validator axon.")
            self.axon.attach(
                forward_fn=self.forward,
                # blacklist_fn=self.blacklist,
                # priority_fn=self.priority,
            )
            bt.logging.info(f"Axon created: {self.axon}")

            try:
                self.subtensor.serve_axon(
                    netuid=self.config.netuid,
                    axon=self.axon,
                )
                bt.logging.info(
                    f"Running validator {self.axon} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
                )

                # Start  starts the miner's axon, making it active on the network.
                self.axon.start()
            except Exception as e:
                bt.logging.error(f"Failed to serve Axon with exception: {e}")
                pass

        except Exception as e:
            bt.logging.error(
                f"Failed to create Axon initialize with exception: {e}"
            )
            pass

    @abstractmethod
    async def concurrent_forward(self):
        """
        The forward function is called by the validator every time step.
        It is responsible for querying the network and scoring the responses.
        """
        ...

    def run(self):
        """
        Initiates and manages the main loop for the miner on the Bittensor network. The main loop handles graceful shutdown on keyboard interrupts and logs unforeseen errors.

        This function performs the following primary tasks:
        1. Check for registration on the Bittensor network.
        2. Continuously forwards queries to the miners on the network, rewarding their responses and updating the scores accordingly.
        3. Periodically resynchronizes with the chain; updating the metagraph with the latest network state and setting weights.

        The essence of the validator's operations is in the forward function, which is called every step. The forward function is responsible for querying the network and scoring the responses.

        Note:
            - The function leverages the global configurations set during the initialization of the miner.
            - The miner's axon serves as its interface to the Bittensor network, handling incoming and outgoing requests.

        Raises:
            KeyboardInterrupt: If the miner is stopped by a manual interruption.
            Exception: For unforeseen errors during the miner's operation, which are logged for diagnosis.
        """

        # Check that validator is registered on the network.
        self.sync()

        bt.logging.info(f"Validator starting at block: {self.block}")

        # This loop maintains the validator's operations until intentionally stopped.
        try:
            while True:
                bt.logging.debug(f"step({self.step}) block({self.block})")

                # Run multiple forwards concurrently.
                self.loop.run_until_complete(self.concurrent_forward())

                # Check if we should exit.
                if self.should_exit:
                    break

                # Sync metagraph and potentially set weights.
                self.sync()

                self.step += 1

        # If someone intentionally stops the validator, it'll safely terminate.
        except KeyboardInterrupt:
            bt.logging.info("Validator interrupted by keyboard.")
            self.should_exit = True

        # In case of unforeseen errors, the validator will log the error and continue operations.
        except Exception as e:
            bt.logging.error(f"Validator error: {e}")
            bt.logging.debug(f"Validator traceback: {traceback.format_exc()}")

        # Always save state before exiting.
        self.save_state()

    def run_in_background_thread(self):
        """
        Starts the validator's operations in a background thread upon entering the context.
        This method facilitates the use of the validator in a 'with' statement.
        """
        if not self.is_running:
            bt.logging.debug("Starting validator in background thread.")
            self.should_exit = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            bt.logging.debug("Started")

    def stop_run_thread(self):
        """
        Stops the validator's operations that are running in the background thread.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def __enter__(self):
        self.run_in_background_thread()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the validator's background operations upon exiting the context.
        This method facilitates the use of the validator in a 'with' statement.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if the context was exited without an exception.
            exc_value: The instance of the exception that caused the context to be exited.
                       None if the context was exited without an exception.
            traceback: A traceback object encoding the stack trace.
                       None if the context was exited without an exception.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def set_weights(self):
        """
        Sets the validator weights to the metagraph hotkeys based on the scores it has received from the miners. The weights determine the trust and incentive level the validator assigns to miner nodes on the network.
        """

        # Check if self.scores contains any NaN values and log a warning if it does.
        if np.isnan(self.scores).any():
            bt.logging.warning(
                f"Scores contain NaN values. This may be due to a lack of responses from miners, or a bug in your reward functions."
            )

        # Calculate the average reward for each uid across non-zero values.
        # Replace any NaN values with 0.
        # Compute the norm of the scores
        norm = np.linalg.norm(self.scores, ord=1, axis=0, keepdims=True)

        # Check if the norm is zero or contains NaN values
        if np.any(norm == 0) or np.isnan(norm).any():
            norm = np.ones_like(norm)  # Avoid division by zero or NaN

        # Compute raw_weights safely
        raw_weights = self.scores / norm

        bt.logging.debug("raw_weights", raw_weights)
        bt.logging.debug("raw_weight_uids", str(self.metagraph.uids.tolist()))
        # Process the raw weights to final_weights via subtensor limitations.
        (
            processed_weight_uids,
            processed_weights,
        ) = process_weights_for_netuid(
            uids=self.metagraph.uids,
            weights=raw_weights,
            netuid=self.config.netuid,
            subtensor=self.subtensor,
            metagraph=self.metagraph,
        )
        bt.logging.debug("processed_weights", processed_weights)
        bt.logging.debug("processed_weight_uids", processed_weight_uids)

        # Convert to uint16 weights and uids.
        (
            uint_uids,
            uint_weights,
        ) = convert_weights_and_uids_for_emit(
            uids=processed_weight_uids, weights=processed_weights
        )

        # Set the weights on chain via our subtensor connection.
        result, msg = self.subtensor.set_weights(
            wallet=self.wallet,
            netuid=self.config.netuid,
            uids=uint_uids,
            weights=uint_weights,
            wait_for_finalization=False,
            wait_for_inclusion=False,
            version_key=self.spec_version,
        )
        # sync once, ensure get latest chain state
        self.metagraph.sync(subtensor=self.subtensor)
        bt.logging.info(f"set_weights: my uid: {self.uid}, uids: {uint_uids}, weights: {uint_weights}, last_update: {self.metagraph.last_update[self.uid]}, block: {self.block}")
        if result is True:
            bt.logging.info("set_weights on chain successfully!")
        else:
            bt.logging.error("set_weights failed", msg)

    def resync_metagraph(self):
        """Resyncs the metagraph and updates the hotkeys and moving averages based on the new metagraph."""

        # Copies state of metagraph before syncing.
        previous_metagraph = copy.deepcopy(self.metagraph)

        # Sync the metagraph.
        self.metagraph.sync(subtensor=self.subtensor)

        log = (
            f"resync_metagraph() | "
            f"uid: {self.uid} | "
            f"last_update[{self.uid}]: {self.metagraph.last_update[self.uid]} | "
            f"Block: {self.metagraph.block.item()} | "
            f"Incentive: {self.metagraph.I[self.uid]} | "
        )
        bt.logging.trace(log)

        # Check if the metagraph axon info has changed.
        if previous_metagraph.axons == self.metagraph.axons:
            return

        bt.logging.info(
            "Metagraph updated, re-syncing hotkeys, dendrite pool and moving averages"
        )
        # Zero out all hotkeys that have been replaced.
        for uid, hotkey in enumerate(self.hotkeys):
            if hotkey != self.metagraph.hotkeys[uid]:
                self.scores[uid] = 0  # hotkey has been replaced

        # Check to see if the metagraph has changed size.
        # If so, we need to add new hotkeys and moving averages.
        if len(self.hotkeys) < len(self.metagraph.hotkeys):
            # Update the size of the moving average scores.
            new_moving_average = np.zeros((self.metagraph.n))
            min_len = min(len(self.hotkeys), len(self.scores))
            new_moving_average[:min_len] = self.scores[:min_len]
            self.scores = new_moving_average

        # Update the hotkeys.
        self.hotkeys = copy.deepcopy(self.metagraph.hotkeys)

    def update_scores(self, rewards: np.ndarray, uids: List[int]):
        """
        Performs exponential moving average on the scores based on the rewards received from the miners.
        Implements a hybrid scoring mechanism: 50% from external rewards, 50% from stake-based rewards.
        If external rewards are empty or invalid, uses only stake-based rewards.
        """

        # Check if rewards contains NaN values.
        if np.isnan(rewards).any():
            bt.logging.warning(f"NaN values detected in rewards: {rewards}")
            # Replace any NaN values in rewards with 0.
            rewards = np.nan_to_num(rewards, nan=0)

        # Ensure rewards is a numpy array.
        rewards = np.asarray(rewards)

        # Check if `uids` is already a numpy array and copy it to avoid the warning.
        if isinstance(uids, np.ndarray):
            uids_array = uids.copy()
        else:
            uids_array = np.array(uids)

        # Handle edge case: If either rewards or uids_array is empty.
        if rewards.size == 0 or uids_array.size == 0:
            bt.logging.info(f"rewards: {rewards}, uids_array: {uids_array}")
            bt.logging.warning(
                "Either rewards or uids_array is empty. No updates will be performed."
            )
            return

        # Check if sizes of rewards and uids_array match.
        if rewards.size != uids_array.size:
            raise ValueError(
                f"Shape mismatch: rewards array of shape {rewards.shape} "
                f"cannot be broadcast to uids array of shape {uids_array.shape}"
            )

        # Get stake-based rewards for the specified uids
        stake_rewards = self._calculate_stake_rewards(uids_array)
        
        # Check if external rewards are valid (non-zero sum)
        total_external_reward = np.sum(rewards)
        if total_external_reward > 0:
            # Use hybrid scoring when external rewards are valid
            external_weight = self.config.neuron.external_reward_weight
            # Validate external_weight is within [0.0, 1.0]
            if not 0.0 <= external_weight <= 1.0:
                bt.logging.warning(f"Invalid external_reward_weight: {external_weight}. Clamping to [0.0, 1.0]")
                external_weight = max(0.0, min(1.0, external_weight))
            
            stake_weight = 1.0 - external_weight
            combined_rewards = external_weight * rewards + stake_weight * stake_rewards
            
            bt.logging.debug(f"External rewards: {rewards}")
            bt.logging.debug(f"Stake rewards: {stake_rewards}")
            bt.logging.debug(f"External weight: {external_weight}, Stake weight: {stake_weight}")
            bt.logging.debug(f"Combined rewards: {combined_rewards}")
        else:
            # Use only stake-based rewards when external rewards are invalid
            combined_rewards = stake_rewards
            bt.logging.debug(f"External rewards invalid (sum={total_external_reward}), using only stake rewards: {stake_rewards}")

        # Compute forward pass rewards, assumes uids are mutually exclusive.
        # shape: [ metagraph.n ]
        scattered_rewards: np.ndarray = np.zeros_like(self.scores)
        scattered_rewards[uids_array] = combined_rewards
        bt.logging.debug(f"Scattered rewards: {scattered_rewards}")

        # Update scores with rewards produced by this step.
        # shape: [ metagraph.n ]
        alpha: float = self.config.neuron.moving_average_alpha
        bt.logging.debug(f"update_scores alpha: {alpha}")
        bt.logging.debug(f"update_scores scattered_rewards: {scattered_rewards}")
        bt.logging.debug(f"update_scores old self.scores: {self.scores}")
        self.scores: np.ndarray = (
            alpha * scattered_rewards + (1 - alpha) * self.scores
        )
        bt.logging.debug(f"Updated moving avg scores: {self.scores}")

    def _calculate_stake_rewards(self, uids: np.ndarray) -> np.ndarray:
        """
        Calculate stake-based rewards for the given UIDs.
        Normalizes stake values to [0, 1] range for fair comparison with external rewards.
        
        Args:
            uids: Array of UIDs to calculate stake rewards for
            
        Returns:
            np.ndarray: Stake-based rewards normalized to [0, 1] range
        """
        # Get stake values for the specified UIDs
        stake_values = self.metagraph.S[uids]
        
        # Handle case where all stakes are zero
        total_stake = np.sum(stake_values)
        if total_stake == 0:
            bt.logging.warning("All specified UIDs have zero stake, using equal distribution")
            return np.ones_like(stake_values) / len(stake_values)
        
        # Normalize stake values to [0, 1] range (sum to 1)
        stake_rewards = stake_values / total_stake
        
        bt.logging.debug(f"Stake values for UIDs {uids}: {stake_values}")
        bt.logging.debug(f"Normalized stake rewards: {stake_rewards}")
        
        return stake_rewards

    def save_state(self):
        """Saves the state of the validator to a file."""
        bt.logging.debug("Saving validator state.")

        # Save the state of the validator to file.
        np.savez(
            self.config.neuron.full_path + "/state.npz",
            step=self.step,
            scores=self.scores,
            hotkeys=self.hotkeys,
        )

    def load_state(self):
        """Loads the state of the validator from a file."""
        bt.logging.info("Loading validator state.")

        # Load the state of the validator from file.
        state = np.load(self.config.neuron.full_path + "/state.npz")
        self.step = state["step"]
        self.scores = state["scores"]
        self.hotkeys = state["hotkeys"]
