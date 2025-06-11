import subprocess
import json
from services.config import settings
from fastapi import APIRouter, Depends, HTTPException, Query
import pexpect
from pydantic import BaseModel
import re
import logging

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
            "--netuid", str(settings.NETUID),
            "--json-output"
        ])
        return json.loads(result)
    except Exception as e:
        logger.error(f"query balance failed: {e}")
        return {"error": "Failed to get wallet overview"}
    


def stake_amount(amount):
    try:
        cmd = [
            "btcli", "stake", "add",
            "--wallet.name", settings.VALIDATOR_WALLET,
            "--wallet.hotkey", settings.VALIDATOR_HOTKEY,
            "--subtensor.chain_endpoint", settings.CHAIN_ENDPOINT,
            "--amount", str(amount),
            "--netuid", str(settings.NETUID),
            "--json-output"
        ]

        logger.debug(f"cmd: {' '.join(cmd)}")
        child = pexpect.spawn(" ".join(cmd), encoding="utf-8")
        child.expect('Would you like to continue?')
        child.sendline('y')
        child.expect('Enter your password:')
        child.sendline(settings.VALIDATOR_PASSWORD)
        child.expect(pexpect.EOF, timeout=60)
        output = child.before
        child.close()

        output = remove_ansi_escape(output)
        logger.debug(f"stake result: {output}")

        # use regex to extract the first complete {...} JSON block (supports multiple lines)
        json_match = re.search(r'(\{[\s\S]*\})', output)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except Exception as e:
                logger.error(f"JSON decode failed: {e}")
                return {"error": "Invalid JSON output", "json_str": json_str}
        # if no JSON output found
        return {"error": "No JSON output found", "output": output}

    except Exception as e:
        logger.error(f"stake failed: {e}")
        error_msg = str(e).split('\n')[0]
        return {"error": error_msg}
