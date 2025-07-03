from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

# Get the project root directory (parent of services directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file_path = os.path.join(project_root, ".env")
load_dotenv(env_file_path, override=True)


class Settings(BaseSettings):
    DETECT_IP: str = os.getenv("DETECT_IP", "8.8.8.8")
    SRV_API_URL: str = os.getenv("SRV_API_URL")
    SRV_API_KEY: str = os.getenv("SRV_API_KEY")

    NEURON_JWT_SECRET_KEY: str = os.getenv("NEURON_JWT_SECRET_KEY")
    NEURON_JWT_EXPIRE_IN: int = int(os.getenv("NEURON_JWT_EXPIRE_IN", "30"))
    NEURON_JWT_ALGORITHM: str = os.getenv("NEURON_JWT_ALGORITHM", "HS256")

    CHAIN_NETWORK: str = os.getenv("CHAIN_NETWORK", "local")
    CHAIN_ENDPOINT: str = os.getenv("CHAIN_ENDPOINT", "")
    WALLET_NAME: str = os.getenv("WALLET_NAME", "validator")
    HOTKEY_NAME: str = os.getenv("HOTKEY_NAME", "default")
    
    CHAIN_NETUID: int = int(os.getenv("CHAIN_NETUID", "2"))
    VALIDATOR_SLEEP_TIME: int = int(os.getenv("VALIDATOR_SLEEP_TIME", "1"))

    # API Server configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

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

settings = Settings() 