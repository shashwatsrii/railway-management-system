from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    train_id = Column(Integer, ForeignKey("trains.id"))
    seat_number = Column(String, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="bookings")
    train = relationship("Train", back_populates="bookings")