from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from database import Base
from typing import Optional

# SQLAlchemy Train Model
class Train(Base):
    __tablename__ = "trains"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, unique=True, index=True)
    train_name = Column(String)
    source = Column(String)
    destination = Column(String)
    total_seats = Column(Integer)
    available_seats = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with bookings
    bookings = relationship("Booking", back_populates="train")

# Pydantic Train Schemas
class TrainCreate(BaseModel):
    train_number: str
    train_name: str
    source: str
    destination: str
    total_seats: int

class TrainUpdate(BaseModel):
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    total_seats: Optional[int] = None

class TrainResponse(BaseModel):
    id: int
    train_number: str
    train_name: str
    source: str
    destination: str
    total_seats: int
    available_seats: int

    class Config:
        from_attributes = True  # Updated for Pydantic V2