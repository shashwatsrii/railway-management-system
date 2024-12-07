from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class BookingBase(BaseModel):
    train_id: int
    seat_number: Optional[str] = None

class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    @validator('train_id')
    def validate_train_id(cls, v):
        if v <= 0:
            raise ValueError('Invalid train ID')
        return v

class BookingResponse(BookingBase):
    """Schema for returning booking details"""
    id: int
    user_id: int
    booking_date: datetime
    train_details: dict  # Can be populated with additional train information

    class Config:
        orm_mode = True

class BookingSearchCriteria(BaseModel):
    """Schema for searching bookings"""
    user_id: Optional[int] = None
    train_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None