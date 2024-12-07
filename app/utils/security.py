import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # If you need OAuth2 password bearer

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode the JWT token and retrieve the current user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Admin API Key
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "your-admin-api-key")

def verify_password(plain_password, hashed_password):
    """Verify a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password for storing"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_admin_api_key(api_key: str = Security(APIKeyHeader(name="X-Admin-API-Key"))):
    """Verify Admin API Key"""
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Admin API Key")
    return api_key