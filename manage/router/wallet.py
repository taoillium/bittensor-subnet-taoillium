import bittensor as bt
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hashlib
import hmac
import os
import re
from pathlib import Path
from services.config import settings

router = APIRouter(prefix="/wallet", tags=["wallet"])

logger = logging.getLogger(__name__)

# Pydantic models for request validation
class SignMessageRequest(BaseModel):
    wallet_name: str
    hotkey_name: str = "default"
    message: str
    message_type: str = "general"

class SignTransactionRequest(BaseModel):
    wallet_name: str
    hotkey_name: str = "default"
    transaction_data: Dict[str, Any]
    transaction_type: str

class UnlockWalletRequest(BaseModel):
    wallet_name: str
    hotkey_name: str = "default"
    password: str

class SubmitTransactionRequest(BaseModel):
    signed_transaction: str
    wallet_name: str
    hotkey_name: str = "default"
    wait_for_finalization: bool = False
    wait_for_inclusion: bool = False

class SetWeightsRequest(BaseModel):
    wallet_name: str
    hotkey_name: str = "default"
    transaction_data: Dict[str, Any]

class VerifyMessageRequest(BaseModel):
    wallet_name: str
    hotkey_name: str = "default"
    message: str
    signature: str
    message_type: str = "general"

def load_wallet(wallet_name: str, hotkey_name: str = "default"):
    """load wallet using config like neuron.py"""
    try:
        logger.info(f"Loading wallet {wallet_name} with hotkey {hotkey_name}")
        
        # Create config like neuron.py does
        import argparse
        parser = argparse.ArgumentParser()
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        bt.logging.add_args(parser)
        bt.axon.add_args(parser)
        
        # Set wallet name and hotkey in config
        config = bt.config(parser)
        config.wallet.name = wallet_name
        config.wallet.hotkey = hotkey_name
        
        # Set the password environment variable if available
        if settings.WALLET_PASSWORD and settings.WALLET_PASSWORD != "your-wallet-password":
            os.environ['WALLET_PASS'] = settings.WALLET_PASSWORD
            logger.info("Wallet password set from environment")
        else:
            logger.warning("No wallet password configured, wallet may prompt for password")
        
        # Use config to initialize wallet like neuron.py
        wallet = bt.wallet(config=config)
        logger.info(f"Wallet {wallet_name} loaded successfully")
        return wallet
    except Exception as e:
        logger.error(f"Failed to load wallet {wallet_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load wallet: {str(e)}")

def get_wallet_public_addresses(wallet_name: str, hotkey_name: str = "default"):
    """get wallet public addresses from key files without decryption"""
    try:
        # Get the wallet path
        wallet_path = Path.home() / ".bittensor" / "wallets" / wallet_name
        
        if not wallet_path.exists():
            raise HTTPException(status_code=404, detail=f"Wallet {wallet_name} not found")
        
        # Read coldkey public address
        coldkeypub_path = wallet_path / "coldkeypub.txt"
        if not coldkeypub_path.exists():
            raise HTTPException(status_code=404, detail=f"Coldkey public file not found for wallet {wallet_name}")
        
        with open(coldkeypub_path, 'r') as f:
            coldkey_content = f.read()
        
        # Extract SS58 address using regex
        coldkey_match = re.search(r'"ss58Address":\s*"([^"]+)"', coldkey_content)
        if not coldkey_match:
            raise HTTPException(status_code=500, detail=f"Could not extract coldkey address from {coldkeypub_path}")
        
        coldkey_address = coldkey_match.group(1)
        
        # Read hotkey public address - hotkey files are directly in hotkeys directory
        hotkey_path = wallet_path / "hotkeys" / hotkey_name
        if not hotkey_path.exists():
            raise HTTPException(status_code=404, detail=f"Hotkey file not found for wallet {wallet_name}, hotkey {hotkey_name}")
        
        with open(hotkey_path, 'r') as f:
            hotkey_content = f.read()
        
        # Extract SS58 address using regex
        hotkey_match = re.search(r'"ss58Address":\s*"([^"]+)"', hotkey_content)
        if not hotkey_match:
            raise HTTPException(status_code=500, detail=f"Could not extract hotkey address from {hotkey_path}")
        
        hotkey_address = hotkey_match.group(1)
        
        return {
            "hotkey_address": hotkey_address,
            "coldkey_address": coldkey_address
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get wallet public addresses for {wallet_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get wallet public addresses: {str(e)}")


@router.post("/sign")
def sign_message(
    request: SignMessageRequest,
):
    """sign message"""
    try:
        logger.debug(f"request: {request}")
        wallet = load_wallet(request.wallet_name, request.hotkey_name)
        
        # choose signature method based on message type
        if request.message_type == "coldkey":
            signature = wallet.coldkey.sign(data=request.message)
        else:
            signature = wallet.hotkey.sign(data=request.message)
        
        # Convert signature from bytes to hex string for JSON serialization
        signature_hex = signature.hex() if isinstance(signature, bytes) else str(signature)
        
        return {
            "signature": signature_hex,
            "message": request.message,
            "ss58_address": wallet.hotkey.ss58_address
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign message failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/verify")
def verify_message(
    request: VerifyMessageRequest,
):
    """verify message signature"""
    try:
        logger.debug(f"request: {request}")
        wallet = load_wallet(request.wallet_name, request.hotkey_name)
        
        # Convert hex signature string back to bytes
        try:
            signature_bytes = bytes.fromhex(request.signature)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid signature format: {str(e)}")
        
        # choose signature method based on message type
        if request.message_type == "coldkey":
            is_valid = wallet.coldkey.verify(data=request.message, signature=signature_bytes)
        else:
            is_valid = wallet.hotkey.verify(data=request.message, signature=signature_bytes)

        return {
            "is_valid": is_valid,
            "ss58_address": wallet.hotkey.ss58_address,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify message failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet_info")
def get_wallet_status(
    wallet_name: str,
    hotkey_name: str = "default",
):
    """check if wallet is unlocked and accessible"""
    try:
        if not wallet_name:
            raise HTTPException(status_code=400, detail="wallet_name is required")
        
        wallet = load_wallet(wallet_name, hotkey_name)
        
        # Try to access private key to test if wallet is unlocked
        try:
            _ = wallet.hotkey.private_key
            is_unlocked = True
        except Exception:
            is_unlocked = False
        
        # Get public addresses from key files to avoid decryption
        addresses = get_wallet_public_addresses(wallet_name, hotkey_name)
        
        return {
            "wallet_name": wallet_name,
            "hotkey_name": hotkey_name,
            "hotkey_address": addresses["hotkey_address"],
            "coldkey_address": addresses["coldkey_address"],
            "is_unlocked": is_unlocked
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get wallet status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
