import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from database import Base
from typing import Optional

# SQLAlchemy Booking Model
class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    train_id = Column(Integer, ForeignKey('trains.id'))
    seat_number = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    train = relationship("Train", back_populates="bookings")

# Pydantic Booking Schemas
class BookingCreate(BaseModel):
    train_id: int

class BookingResponse(BaseModel):
    id: int
    train_id: int
    user_id: int
    seat_number: str
    created_at: datetime.datetime  # Updated the type to datetime.datetime

    class Config:
        from_attributes = True  # Updated for Pydantic V2
