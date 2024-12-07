from sqlalchemy.orm import Session
from fastapi import Depends
from jose import jwt, JWTError
from datetime import timedelta

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenData
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.db.session import get_db

class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_user(self, user: UserCreate):
        # Check if username already exists
        existing_user = self.db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already registered")

        # Create new user
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def authenticate_user(self, credentials: UserLogin):
        # Find user by username
        user = self.db.query(User).filter(User.username == credentials.username).first()
        
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        if not verify_password(credentials.password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")
        
        return user

    def create_user_token(self, user: User):
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username, 
                "is_admin": user.is_admin
            }, 
            expires_delta=access_token_expires
        )
        
        return access_token

    def get_current_user(self, token: str):
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            is_admin: bool = payload.get("is_admin", False)
            
            if username is None:
                raise AuthenticationError()
            
            token_data = TokenData(username=username, is_admin=is_admin)
        except JWTError:
            raise AuthenticationError()
        
        user = self.db.query(User).filter(User.username == token_data.username).first()
        
        if not user:
            raise AuthenticationError()
        
        return user