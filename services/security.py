from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import time
from services.config import settings


def create_neuron_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token.
    
    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): Token expiration time.
        
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.NEURON_JWT_EXPIRE_IN)
    to_encode.update({"salt": time.time()})
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.NEURON_JWT_SECRET_KEY, algorithm=settings.NEURON_JWT_ALGORITHM)
    token = verify_neuron_token(encoded_jwt)
    return {"token": encoded_jwt, "exp": token.get("exp")}

def verify_neuron_token(token: str) -> Optional[dict]:
    """Verify a JWT token.
    
    Args:
        token (str): The JWT token to verify.
        
    Returns:
        Optional[dict]: The decoded token payload if valid, None otherwise.
    """
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, settings.NEURON_JWT_SECRET_KEY, algorithms=[settings.NEURON_JWT_ALGORITHM])
        return payload
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
    

def create_manage_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token.
    
    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): Token expiration time.
        
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.MANAGER_JWT_EXPIRE_IN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.MANAGER_JWT_SECRET_KEY, algorithm=settings.MANAGER_JWT_ALGORITHM)
    return encoded_jwt

def verify_manage_token(token: str) -> Optional[dict]:
    """Verify a JWT token.
    
    Args:
        token (str): The JWT token to verify.
        
    Returns:
        Optional[dict]: The decoded token payload if valid, None otherwise.
    """
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, settings.MANAGER_JWT_SECRET_KEY, algorithms=[settings.MANAGER_JWT_ALGORITHM])
        return payload
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None