from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
import logging

# Get the project root directory (parent of services directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file_path = os.path.join(project_root, ".env")
load_dotenv(env_file_path, override=True)

class Settings(BaseSettings):
    DETECT_IP: str = os.getenv("DETECT_IP", "8.8.8.8")
    SRV_API_URL: str = os.getenv("SRV_API_URL", "https://api.taoillium.ai")
    SRV_API_KEY: str = os.getenv("SRV_API_KEY")

    NEURON_JWT_SECRET_KEY: str = os.getenv("NEURON_JWT_SECRET_KEY")
    NEURON_JWT_EXPIRE_IN: int = int(os.getenv("NEURON_JWT_EXPIRE_IN", "30"))
    NEURON_JWT_ALGORITHM: str = os.getenv("NEURON_JWT_ALGORITHM", "HS256")

    CHAIN_NETWORK: str = os.getenv("CHAIN_NETWORK", "local")
    CHAIN_ENDPOINT: str = os.getenv("CHAIN_ENDPOINT", "")
    WALLET_NAME: str = os.getenv("WALLET_NAME", "validator")
    HOTKEY_NAME: str = os.getenv("HOTKEY_NAME", "default")
    
    CHAIN_NETUID: int = int(os.getenv("CHAIN_NETUID", "2"))
    VALIDATOR_SLEEP_TIME: int = int(os.getenv("VALIDATOR_SLEEP_TIME", "5"))
    MINER_SLEEP_TIME: int = int(os.getenv("MINER_SLEEP_TIME", "5"))

    # Manager service configuration
    MANAGER_HOST: str = os.getenv("MANAGER_HOST", "0.0.0.0")
    MANAGER_PORT: int = int(os.getenv("MANAGER_PORT", "8000"))
    MANAGER_DEBUG: str = os.getenv("MANAGER_DEBUG", "INFO").upper()
    MANAGER_RELOAD: bool = os.getenv("MANAGER_RELOAD", "false").lower() == "true"
    MANAGER_JWT_SECRET_KEY: str = os.getenv("MANAGER_JWT_SECRET_KEY", "your-secret-api-key")
    MANAGER_JWT_EXPIRE_IN: int = int(os.getenv("MANAGER_JWT_EXPIRE_IN", "30"))
    MANAGER_JWT_ALGORITHM: str = os.getenv("MANAGER_JWT_ALGORITHM", "HS256")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Only set default if CHAIN_ENDPOINT is not provided or empty
        if not self.CHAIN_ENDPOINT or self.CHAIN_ENDPOINT.strip() == "":
            default_chain_endpoint = "ws://127.0.0.1:9944"
            if self.CHAIN_NETWORK == "finney":
                default_chain_endpoint = "wss://entrypoint-finney.opentensor.ai"
            elif self.CHAIN_NETWORK == "test":
                default_chain_endpoint = "wss://test.finney.opentensor.ai"
            
            self.CHAIN_ENDPOINT = default_chain_endpoint

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

    
    def record_api_key_to_env(self, key, value):
        """Record the current API key to .env file"""
        if not key or not value:
            print(f"No API key to record: key={key}, value={'*' * len(value) if value else 'None'}")
            return

        try:
            # Read existing .env file
            env_lines = []
            key_found = False
            
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    env_lines = f.readlines()
                
                # Check if the key already exists
                for i, line in enumerate(env_lines):
                    if line.strip().startswith(f"{key}="):
                        env_lines[i] = f"{key}={value}\n"
                        key_found = True
                        break
                
                # If key not found, add it
                if not key_found:
                    env_lines.append(f"{key}={value}\n")
                
                # Write back to .env file
                with open(env_file_path, 'w') as f:
                    f.writelines(env_lines)
                
                # Log success
                print(f"Recorded {key} to .env file")
                
        except Exception as e:
            # Log error
            print(f"Failed to record API key to .env file: {e}")

settings = Settings() 