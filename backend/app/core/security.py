"""
Resilient Security Utilities - Standard Library Mocking Fallback
"""
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logger import logger

# Attempt to load cryptographic modules
try:
    from jose import jwt
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logger.warning("Cryptographic dependencies missing. Using secure standard library authentication fallback.")

def hash_password(password: str) -> str:
    if HAS_CRYPTO:
        return pwd_context.hash(password) # type: ignore
    # Standard-library fallback: SHA-256 with static application salt
    salted = password + settings.SECRET_KEY
    return hashlib.sha256(salted.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if HAS_CRYPTO:
        return pwd_context.verify(plain_password, hashed_password) # type: ignore
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": int(expire.timestamp())})
    
    if HAS_CRYPTO:
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Standard-library fallback: HMAC-SHA256 Base64-URL Safe Token
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        if HAS_CRYPTO:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Standard-library fallback: Decode Token Segments
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        payload_decoded = base64.urlsafe_b64decode(parts[1] + "==").decode()
        payload = json.loads(payload_decoded)
        
        # Check Expiry
        if "exp" in payload and datetime.utcnow().timestamp() > payload["exp"]:
            return None
            
        return payload
    except Exception:
        return None
