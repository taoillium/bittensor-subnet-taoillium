from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

# Get the project root directory (parent of services directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file_path = os.path.join(project_root, ".env")
load_dotenv(env_file_path, override=True)


class Settings(BaseSettings):
    VALIDATOR_HOST: str = os.getenv("VALIDATOR_HOST", "127.0.0.1")
    VALIDATOR_PORT: int = int(os.getenv("VALIDATOR_PORT", "8080"))
    DETECT_IP: str = os.getenv("DETECT_IP", "8.8.8.8")
    SRV_API_URL: str = os.getenv("SRV_API_URL")
    SRV_API_JWT_SECRET_KEY: str = os.getenv("SRV_API_JWT_SECRET_KEY")
    SRV_API_JWT_EXPIRE_IN: int = int(os.getenv("SRV_API_JWT_EXPIRE_IN", "30"))
    SRV_API_JWT_ALGORITHM: str = os.getenv("SRV_API_JWT_ALGORITHM", "HS256")

    CHAIN_NETWORK: str = os.getenv("CHAIN_NETWORK", "local")
    CHAIN_ENDPOINT: str = os.getenv("CHAIN_ENDPOINT", "")
    VALIDATOR_WALLET: str = os.getenv("VALIDATOR_WALLET", "validator")
    VALIDATOR_HOTKEY: str = os.getenv("VALIDATOR_HOTKEY", "default")
    VALIDATOR_PASSWORD: str = os.getenv("VALIDATOR_PASSWORD", "")
    MANAGER_HOST: str = os.getenv("MANAGER_HOST", "127.0.0.1")
    MANAGER_PORT: int = int(os.getenv("MANAGER_PORT", "8000"))
    MANAGER_DEBUG: str = os.getenv("MANAGER_DEBUG", "INFO").upper()
    MANAGER_RELOAD: bool = os.getenv("MANAGER_RELOAD", "false").lower() == "true"
    CHAIN_NETUID: int = int(os.getenv("CHAIN_NETUID", "1"))

    VALIDATOR_SLEEP_TIME: int = int(os.getenv("VALIDATOR_SLEEP_TIME", "1"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        default_chain_endpoint = "ws://127.0.0.1:9944"
        if self.CHAIN_NETWORK == "finney":
            default_chain_endpoint = "wss://entrypoint-finney.opentensor.ai"
        elif self.CHAIN_NETWORK == "test":
            default_chain_endpoint = "wss://test.finney.opentensor.ai"

        self.CHAIN_ENDPOINT = self.CHAIN_ENDPOINT or default_chain_endpoint

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings() 