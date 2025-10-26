import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.config import jwt_config

# Security scheme for Swagger UI
security = HTTPBearer()


def extract_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Extract token from Authorization header.
    Supports both 'Bearer token' and 'token' formats.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=jwt_config.access_token_expire_minutes)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=jwt_config.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_config.refresh_secret_key, algorithm=jwt_config.algorithm)
    
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, jwt_config.refresh_secret_key, algorithms=[jwt_config.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None