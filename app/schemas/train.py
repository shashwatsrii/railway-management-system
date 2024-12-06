from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TrainBase(BaseModel):
    train_number: str = Field(..., min_length=3, max_length=10)
    train_name: str = Field(..., min_length=3, max_length=100)
    source_station: str = Field(..., min_length=2, max_length=50)
    destination_station: str = Field(..., min_length=2, max_length=50)
    total_seats: int = Field(..., gt=0)
    ticket_price: float = Field(..., gt=0)

class TrainCreate(TrainBase):
    pass

class TrainResponse(TrainBase):
    id: int
    available_seats: int
    created_at: datetime

    class Config:
        orm_mode = True

class TrainAvailabilityRequest(BaseModel):
    source: str
    destination: str