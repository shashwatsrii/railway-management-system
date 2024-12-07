from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, Field, constr
from database import Base
from typing import Optional
import uuid

# SQLAlchemy User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    uuid: str
    username: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True  # Updated for Pydantic V2