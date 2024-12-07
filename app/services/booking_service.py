from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import Depends, HTTPException
from typing import List
import uuid

from app.models.train import Train
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse, BookingSearchCriteria
from app.db.session import get_db
from app.core.exceptions import ResourceNotFoundError

class BookingService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def book_seat(self, user: User, booking_data: BookingCreate):
        """
        Book a seat for a train
        
        Handles race conditions using optimistic locking and transactions
        
        Args:
            user (User): Current user booking the seat
            booking_data (BookingCreate): Booking details
        
        Returns:
            Booking: Created booking object
        """
        try:
            # Start a transaction
            with self.db.begin():
                # Retrieve the train with a lock
                train = (
                    self.db.query(Train)
                    .with_for_update()  # Pessimistic locking
                    .filter(Train.id == booking_data.train_id)
                    .first()
                )

                # Validate train exists
                if not train:
                    raise ResourceNotFoundError("Train not found")

                # Check seat availability
                if train.available_seats <= 0:
                    raise HTTPException(
                        status_code=400, 
                        detail="No seats available on this train"
                    )

                # Generate unique seat number
                seat_number = self._generate_seat_number(train)

                # Create booking
                booking = Booking(
                    user_id=user.id,
                    train_id=train.id,
                    seat_number=seat_number
                )

                # Reduce available seats
                train.available_seats -= 1

                # Add and commit booking
                self.db.add(booking)
                self.db.add(train)

                # Fetch the booking to get full details
                self.db.flush()
                self.db.refresh(booking)

                return booking

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def _generate_seat_number(self, train: Train):
        """
        Generate a unique seat number for a train
        
        Args:
            train (Train): Train for which seat number is generated
        
        Returns:
            str: Unique seat number
        """
        # Simple seat number generation strategy
        # In a real-world scenario, this would be more complex
        existing_bookings = self.db.query(Booking).filter(
            Booking.train_id == train.id
        ).count()

        # Generate seat like A1, A2, B1, B2, etc.
        rows = 'ABCDEFGH'
        row = rows[existing_bookings // 10]
        number = (existing_bookings % 10) + 1
        return f"{row}{number}"

    def get_user_bookings(self, user: User, search_criteria: BookingSearchCriteria = None):
        """
        Retrieve bookings for a user with optional filtering
        
        Args:
            user (User): Current user
            search_criteria (BookingSearchCriteria): Optional search filters
        
        Returns:
            List[Booking]: List of user's bookings
        """
        query = self.db.query(Booking).filter(Booking.user_id == user.id)

        if search_criteria:
            if search_criteria.train_id:
                query = query.filter(Booking.train_id == search_criteria.train_id)
            
            if search_criteria.start_date:
                query = query.filter(Booking.booking_date >= search_criteria.start_date)
            
            if search_criteria.end_date:
                query = query.filter(Booking.booking_date <= search_criteria.end_date)

        return query.all()

    def cancel_booking(self, user: User, booking_id: int):
        """
        Cancel a user's booking
        
        Args:
            user (User): Current user
            booking_id (int): ID of booking to cancel
        
        Returns:
            bool: Cancellation status
        """
        try:
            with self.db.begin():
                # Find the booking
                booking = (
                    self.db.query(Booking)
                    .with_for_update()
                    .filter(
                        and_(
                            Booking.id == booking_id, 
                            Booking.user_id == user.id
                        )
                    )
                    .first()
                )

                if not booking:
                    raise ResourceNotFoundError("Booking not found")

                # Retrieve associated train
                train = self.db.query(Train).filter(Train.id == booking.train_id).first()
                
                # Increase available seats
                train.available_seats += 1

                # Remove booking
                self.db.delete(booking)
                self.db.add(train)

                return True

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))