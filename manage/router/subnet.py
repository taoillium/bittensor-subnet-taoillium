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

"""
Subnet API Router for Taoillium Subnet
This router provides endpoints for interacting with the subnet network.
"""

import bittensor as bt
import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from template.api import TaoilliumAPI
from services.config import settings
from services.security import verify_neuron_token, create_neuron_access_token
from template.utils.misc import sn_gen

router = APIRouter(prefix="/subnet", tags=["subnet"])

logger = logging.getLogger(__name__)

# Configure bittensor logging
try:
    import argparse
    parser = argparse.ArgumentParser()
    bt.logging.add_args(parser)
    config = bt.config(parser)
    config.logging.logging_dir = None  # Disable file logging
    config.logging.record_log = False  # Disable record logging
    config.logging.info = True
    config.logging.warning = True
    config.logging.error = True
    config.logging.critical = True
    config.logging.default = True
    config.logging.console = True
    if settings.MANAGER_DEBUG == "DEBUG":
        config.logging.debug = True
    elif settings.MANAGER_DEBUG == "TRACE":
        config.logging.trace = True
        config.logging.debug = True
    elif settings.MANAGER_DEBUG == "DEFAULT":
        config.logging.default = True
    elif settings.MANAGER_DEBUG == "CONSOLE":
        config.logging.console = True
    bt.logging.set_config(config=config)
except Exception as e:
    logger.warning(f"Failed to configure bittensor logging: {e}")

# Pydantic models for request/response
class QueryRequest(BaseModel):
    input: Dict[str, Any]
    sample_size: Optional[int] = 3
    timeout: Optional[int] = 30


class QueryResponse(BaseModel):
    success: bool
    responses: List[Dict[str, Any]]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    network_info: Optional[Dict[str, Any]] = None

class TaskReceiveRequest(BaseModel):
    method: str
    data: Dict[str, Any]
    uids: Optional[List[Union[int, str]]] = None


# Global API client instance
_api_client = None


def get_api_client() -> TaoilliumAPI:
    """Get or create the TaoilliumAPI client instance"""
    global _api_client
    if _api_client is None:
        try:
            # Try to create wallet with default settings
            import argparse
            parser = argparse.ArgumentParser()
            bt.wallet.add_args(parser)
            config = bt.config(parser)
            config.wallet.name = settings.WALLET_NAME
            config.wallet.hotkey = settings.HOTKEY_NAME
            wallet = bt.wallet(config=config)
            _api_client = TaoilliumAPI(wallet=wallet, netuid=settings.CHAIN_NETUID, network=settings.CHAIN_NETWORK)
            logger.info(f"Initialized TaoilliumAPI client for netuid {settings.CHAIN_NETUID}")
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {e}")
            raise e
        
    return _api_client


def get_metagraph():
    """Get or create the metagraph instance (no wallet required)"""
    try:
        return bt.metagraph(netuid=settings.CHAIN_NETUID, network=settings.CHAIN_NETWORK)
    except Exception as e:
        logger.error(f"Failed to initialize metagraph: {e}")
        return None


@router.post("/query", response_model=QueryResponse)
async def query_network(
    request: QueryRequest,
):
    """Query the subnet network (authenticated)"""
    try:
        # Query the network
        api_client = get_api_client()
        responses = await api_client.query_network(
            user_input=request.input,
            sample_size=request.sample_size,
            timeout=request.timeout
        )
        
        return QueryResponse(
            success=True,
            responses=responses
        )
        
    except Exception as e:
        logger.error(f"Query network failed: {e}")
        return QueryResponse(
            success=False,
            responses=[],
            error=str(e)
        )


@router.post("/task/receive")
async def task_receive(
    request: TaskReceiveRequest,
):
    """
    Task receive endpoint - equivalent to validator.py /task/receive
    This endpoint mimics the behavior of the validator's embedded HTTP server
    """
    try:
        # Get request data (same as validator.py)
        logger.info(f"Task receive request: {request}")
        
        # Convert TaskReceiveRequest to the format expected by ServiceProtocol
        user_input = {
            "__type__": "miner",
            "uids": request.uids,
            "sn": sn_gen(),
            "method": request.method,
            "data": request.data
        }
        
        logging.info(f"user_input: {user_input}")
        # Use the TaoilliumAPI to query the network
        # This mimics the forward_with_input behavior from validator.py
        api_client = get_api_client()
        responses = await api_client.query_network(
            user_input=user_input,
            sample_size=3,  # Default sample size (can be made configurable)
            timeout=30,
            use_random_selection=True  # Use random selection like forward_with_input
        )

        logging.info(f"responses: {responses}")
        
        # Return responses in the same format as validator.py
        # Only return non-empty responses (same as validator.py)
        outputs = [r for r in responses if r]
        return outputs
        
    except Exception as e:
        logger.error(f"Task receive failed: {e}")
        return {"error": str(e)}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for subnet connectivity"""
    try:
        metagraph = get_metagraph()
        if metagraph is None:
            return HealthResponse(
                status="unhealthy",
                message="Failed to connect to subnet",
                network_info={"error": "Metagraph initialization failed"}
            )
        
        return HealthResponse(
            status="healthy",
            message="Subnet API is accessible",
            network_info={
                "netuid": metagraph.netuid,
                "total_neurons": len(metagraph.axons),
                "network": metagraph.network,
                "block": metagraph.block.item() if hasattr(metagraph.block, 'item') else str(metagraph.block)
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"Subnet API check failed: {str(e)}",
            network_info={"error": str(e)}
        )


@router.get("/status")
async def get_subnet_info():
    """Get subnet information"""
    try:
        metagraph = get_metagraph()
        if metagraph is None:
            return {
                "netuid": settings.CHAIN_NETUID,
                "name": "taoillium",
                "error": "Metagraph not available"
            }
        
        return {
            "netuid": metagraph.netuid,
            "name": "taoillium",
            "metagraph_info": {
                "total_neurons": len(metagraph.axons),
                "network": metagraph.network,
                "block": metagraph.block.item() if hasattr(metagraph.block, 'item') else str(metagraph.block)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get subnet info: {e}")
        return {
            "netuid": settings.CHAIN_NETUID,
            "name": "taoillium",
            "error": str(e)
        } 