# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2025 Taoillium Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from typing import Dict, Any
from pydantic import Field
import bittensor as bt

# This is the protocol for the ai agent miner and validator.
# It is a simple request-response protocol where the validator sends a request
# to the miner, and the miner responds with a ai agent response.

# ---- miner ----
# Example usage:
#   def ai_agent( synapse: AiAgentProtocol ) -> AiAgentProtocol:
#       synapse.output = synapse.input
#       return synapse
#   axon = bt.axon().attach( ai_agent ).serve(netuid=...).start()

# ---- validator ---
# Example usage:
#   dendrite = bt.dendrite()
#   ai_agent_output = dendrite.query( AiAgentProtocol( input = {"message": "Hello, world!"} ) )
#   assert ai_agent_output == {"result": "Hello, world!"}


class ServiceProtocol(bt.Synapse):
    """
    A simple ai agent protocol representation which uses bt.Synapse as its base.
    This protocol helps in handling ai agent request and response communication between
    the miner and the validator.

    Attributes:
    - input: An json value representing the input request sent by the validator.
    - output: An optional json value which, when filled, represents the response from the miner.
    """

    # Required request input, filled by sending dendrite caller.
    input: Dict[str, Any] = None

    # Optional request output, filled by receiving axon.
    output: Dict[str, Any] = Field(default_factory=dict)

    def deserialize(self) -> dict:
        """
        Deserialize the output. This method retrieves the response from
        the miner in the form of output, deserializes it and returns it
        as the output of the dendrite.query() call.

        Returns:
        - int: The deserialized response, which in this case is the value of dummy_output.

        Example:
        Assuming a AiAgentProtocol instance has a output value of {"result": "Hello, world!"}:
        >>> ai_agent_protocol_instance = AiAgentProtocol(input={"message": "Hello, world!"})
        >>> ai_agent_protocol_instance.output = {"result": "Hello, world!"}
        >>> ai_agent_protocol_instance.deserialize()
        {"result": "Hello, world!"}
        """
        return self.output

