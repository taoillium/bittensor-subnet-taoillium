from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    VALIDATOR_HOST: str = os.getenv("VALIDATOR_HOST", "127.0.0.1")
    VALIDATOR_PORT: int = int(os.getenv("VALIDATOR_PORT", "8080"))
    DETECT_IP: str = os.getenv("DETECT_IP", "8.8.8.8")
    SRV_API_URL: str = os.getenv("SRV_API_URL")
    SRV_API_JWT_SECRET_KEY: str = os.getenv("SRV_API_JWT_SECRET_KEY")
    SRV_API_JWT_EXPIRE_IN: int = int(os.getenv("SRV_API_JWT_EXPIRE_IN", "30"))
    SRV_API_JWT_ALGORITHM: str = os.getenv("SRV_API_JWT_ALGORITHM", "HS256")

    CHAIN_ENDPOINT: str = os.getenv("CHAIN_ENDPOINT", "ws://127.0.0.1:9944")
    VALIDATOR_WALLET: str = os.getenv("VALIDATOR_WALLET", "validator")
    VALIDATOR_HOTKEY: str = os.getenv("VALIDATOR_HOTKEY", "default")
    VALIDATOR_PASSWORD: str = os.getenv("VALIDATOR_PASSWORD", "")
    MANAGER_HOST: str = os.getenv("MANAGER_HOST", "127.0.0.1")
    MANAGER_PORT: int = int(os.getenv("MANAGER_PORT", "8000"))
    MANAGER_DEBUG: str = os.getenv("MANAGER_DEBUG", "INFO").upper()
    MANAGER_RELOAD: bool = os.getenv("MANAGER_RELOAD", "false").lower() == "true"
    CHAIN_NETUID: int = int(os.getenv("CHAIN_NETUID", "1"))

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings() 