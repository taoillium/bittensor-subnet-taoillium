import subprocess
import json
from services.config import settings
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import re
import logging
from services.cli import stake_add

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stake", tags=["stake"])


def remove_ansi_escape(s):
    # match all ANSI escape sequences
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)


class StakeAddRequest(BaseModel):
    amount: str

@router.post("/add")
async def stake_add(request: StakeAddRequest):
    """Stake add."""
    return stake_amount(request.amount)

@router.get("/overview")
async def get_wallet_overview():
    """Get wallet overview."""
    return get_wallet_overview()

def get_wallet_overview():
    # use btcli to query balance
    try:
        result = subprocess.check_output([
            "btcli", "wallet", "overview",
            "--wallet.name", settings.VALIDATOR_WALLET,
            "--subtensor.chain_endpoint", settings.CHAIN_ENDPOINT,
            "--netuid", str(settings.CHAIN_NETUID),
            "--json-output"
        ])
        return json.loads(result)
    except Exception as e:
        logger.error(f"query balance failed: {e}")
        return {"error": "Failed to get wallet overview"}
    


def stake_amount(amount):
    return stake_add(settings.VALIDATOR_WALLET, settings.VALIDATOR_HOTKEY, amount, settings.CHAIN_NETUID, settings.VALIDATOR_PASSWORD, settings.CHAIN_ENDPOINT, settings.CHAIN_NETWORK)
