from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookingBase(BaseModel):
    train_id: int
    seats_booked: int = Field(1, gt=0, le=6)  # Limit booking to 6 seats per transaction

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    total_price: float
    booking_status: str
    booked_at: datetime

    class Config:
        orm_mode = True

class BookingDetailRequest(BaseModel):
    booking_id: int
