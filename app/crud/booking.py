from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.models.train import Train
from app.schemas.booking import BookingCreate
from fastapi import HTTPException
import asyncio

def create_booking(db: Session, booking: BookingCreate, user_id: int):
    # Use a lock to prevent race conditions
    with db.begin_nested():
        # Lock the train record to prevent concurrent bookings
        train = db.query(Train).filter(Train.id == booking.train_id).with_for_update().first()
        
        if not train:
            raise HTTPException(status_code=404, detail="Train not found")
        
        if train.available_seats < booking.seats_booked:
            raise HTTPException(
                status_code=400, 
                detail="Not enough seats available"
            )
        
        # Calculate total price
        total_price = train.ticket_price * booking.seats_booked
        
        # Create booking
        db_booking = Booking(
            user_id=user_id,
            train_id=booking.train_id,
            seats_booked=booking.seats_booked,
            total_price=total_price
        )
        
        # Reduce available seats
        train.available_seats -= booking.seats_booked
        
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        
        return db_booking

def get_user_bookings(db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).all()

def get_booking_details(db: Session, booking_id: int, user_id: int):
    booking = db.query(Booking).filter(
        Booking.id == booking_id, 
        Booking.user_id == user_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking