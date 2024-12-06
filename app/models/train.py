from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.config import Base
from datetime import datetime

class Train(Base):
    __tablename__ = "trains"
    __table_args__ = (
        UniqueConstraint('train_number', name='_train_number_uc'),
    )

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, unique=True, index=True, nullable=False)
    train_name = Column(String, nullable=False)
    source_station = Column(String, nullable=False)
    destination_station = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    ticket_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="train")