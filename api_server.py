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
Independent HTTP API Server for Taoillium Subnet
This server provides a clean REST API interface for external clients to interact with the subnet.
It uses TaoilliumAPI as the backend and can be deployed independently from validators.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import bittensor as bt
from template.api import TaoilliumAPI
from services.config import settings
from services.security import verify_neuron_token, create_neuron_access_token


# Pydantic models for request/response
class QueryRequest(BaseModel):
    input: Dict[str, Any]
    sample_size: Optional[int] = 3
    timeout: Optional[int] = 30


class TaskReceiveRequest(BaseModel):
    """Request model for /task/receive endpoint - matches validator.py behavior"""
    # This can be any JSON data, so we use Dict[str, Any]
    pass


class QueryResponse(BaseModel):
    success: bool
    responses: List[Dict[str, Any]]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    network_info: Optional[Dict[str, Any]] = None


# Security
security = HTTPBearer()


class APIServer:
    def __init__(self):
        self.app = FastAPI(
            title="Taoillium Subnet API",
            description="REST API for interacting with Taoillium subnet",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure as needed for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize API client
        self.wallet = bt.wallet()
        self.api_client = TaoilliumAPI(wallet=self.wallet, netuid=settings.CHAIN_NETUID)
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_model=HealthResponse)
        async def root():
            """Root endpoint with basic info"""
            return HealthResponse(
                status="healthy",
                message="Taoillium Subnet API is running"
            )
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            try:
                health_result = await self.api_client.health_check()
                return HealthResponse(
                    status="healthy",
                    message="Network is accessible",
                    network_info=health_result
                )
            except Exception as e:
                return HealthResponse(
                    status="unhealthy",
                    message=f"Network check failed: {str(e)}"
                )
        
        @self.app.post("/query", response_model=QueryResponse)
        async def query_network(
            request: QueryRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Query the subnet network"""
            try:
                # Verify authentication
                if not verify_neuron_token(credentials.credentials):
                    raise HTTPException(status_code=401, detail="Invalid token")
                
                # Query the network
                responses = await self.api_client.query_network(
                    user_input=request.input,
                    sample_size=request.sample_size,
                    timeout=request.timeout
                )
                
                return QueryResponse(
                    success=True,
                    responses=responses
                )
                
            except Exception as e:
                return QueryResponse(
                    success=False,
                    responses=[],
                    error=str(e)
                )
        
        
        @self.app.post("/task/receive")
        async def task_receive(
            request: Request,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """
            Task receive endpoint - equivalent to validator.py /task/receive
            This endpoint mimics the behavior of the validator's embedded HTTP server
            """
            try:
                # Verify authentication (same as validator.py)
                if not verify_neuron_token(credentials.credentials):
                    return {"error": "Unauthorized"}
                
                # Get request data (same as validator.py)
                data = await request.json()
                if data is None:
                    return {"error": "Missing 'input' in request body"}
                
                # Use the TaoilliumAPI to query the network
                # This mimics the forward_with_input behavior from validator.py
                responses = await self.api_client.query_network(
                    user_input=data,
                    sample_size=3,  # Default sample size (can be made configurable)
                    timeout=30,
                    use_random_selection=True  # Use random selection like forward_with_input
                )
                
                # Return responses in the same format as validator.py
                # Only return non-empty responses (same as validator.py)
                outputs = [r for r in responses if r]
                return outputs
                
            except Exception as e:
                return {"error": str(e)}
        
        @self.app.get("/token")
        async def get_access_token():
            """Get access token for authenticated endpoints"""
            # This is a simple example - in production, implement proper authentication
            token_data = {
                "type": "api_client",
                "permissions": ["query"]
            }
            token = create_neuron_access_token(data=token_data)
            return {"token": token}
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the API server"""
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point"""
    server = APIServer()
    print(f"Starting Taoillium API Server on {settings.API_HOST}:{settings.API_PORT}")
    server.run(host=settings.API_HOST, port=settings.API_PORT)


if __name__ == "__main__":
    main() 