import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

SECRET_KEY = "your_secret_key"
REFRESH_SECRET_KEY = "your_refresh_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None