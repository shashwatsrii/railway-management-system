from pydantic import BaseModel, validator, Field
from typing import List, Optional, Annotated
from datetime import datetime

class TrainBase(BaseModel):
    train_number: Annotated[str, Field(min_length=4, max_length=10)]
    name: Annotated[str, Field(min_length=3, max_length=100)]
    source: str
    destination: str
    total_seats: int

class TrainCreate(TrainBase):
    """Schema for creating a new train"""
    @validator('total_seats')
    def validate_total_seats(cls, v):
        if v <= 0:
            raise ValueError('Total seats must be a positive number')
        return v

class TrainUpdate(BaseModel):
    """Schema for updating train details"""
    name: Optional[str] = None
    total_seats: Optional[int] = None
    available_seats: Optional[int] = None

    @validator('total_seats')
    def validate_total_seats(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Total seats must be a positive number')
        return v

class TrainResponse(TrainBase):
    """Schema for returning train information"""
    id: int
    available_seats: int
    created_at: datetime

    class Config:
        orm_mode = True

class TrainAvailabilityResponse(BaseModel):
    """Schema for checking train availability between stations"""
    trains: List[TrainResponse]