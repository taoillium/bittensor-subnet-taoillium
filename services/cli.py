import subprocess
import json
import pexpect
import re
import logging


logger = logging.getLogger(__name__)

def remove_ansi_escape(s):
    # match all ANSI escape sequences
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)

def stake_add(wallet_name, hotkey, amount, netuid, password, chain_endpoint=None, network=None, partial=False):
    if not wallet_name or not hotkey or not amount or not netuid or not password:
        raise ValueError("wallet_name, hotkey, amount, netuid, password are required")
    
    if not network and not chain_endpoint:
        raise ValueError("network or chain_endpoint is required")
    
    try:
        cmd = [
            "btcli", "stake", "add",
            "--wallet.name", wallet_name,
            "--wallet.hotkey", hotkey,
            "--amount", str(amount),
            "--netuid", str(netuid),
            "--json-output"
        ]

        if network:
            cmd.append("--network")
            cmd.append(network)
        if chain_endpoint:
            cmd.append("--subtensor.chain_endpoint")
            cmd.append(chain_endpoint)
        if partial:
            cmd.append("--partial")

        logger.debug(f"cmd: {' '.join(cmd)}")
        child = pexpect.spawn(" ".join(cmd), encoding="utf-8")
        child.expect('Would you like to continue?')
        child.sendline('y')
        child.expect('Enter your password:')
        child.sendline(password)
        child.expect(pexpect.EOF, timeout=60)
        output = child.before
        child.close()

        logger.debug(f"stake result: {output}")
        output = remove_ansi_escape(output)

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
