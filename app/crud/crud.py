from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import user, train, booking
from utils.security import get_password_hash, verify_password
from fastapi import HTTPException

# User CRUD
class UserCRUD:
    @staticmethod
    def create_user(db: Session, user_data):
        hashed_password = get_password_hash(user_data.password)
        db_user = user.User(
            username=user_data.username, 
            email=user_data.email, 
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(user.User).filter(user.User.username == username).first()

# Train CRUD
class TrainCRUD:
    @staticmethod
    def create_train(db: Session, train_data):
        db_train = train.Train(
            train_number=train_data.train_number,
            train_name=train_data.train_name,
            source=train_data.source,
            destination=train_data.destination,
            total_seats=train_data.total_seats,
            available_seats=train_data.total_seats
        )
        db.add(db_train)
        db.commit()
        db.refresh(db_train)
        return db_train

    @staticmethod
    def get_trains_by_route(db: Session, source: str, destination: str):
        return db.query(train.Train).filter(
            and_(train.Train.source == source, 
                 train.Train.destination == destination)
        ).all()

# Booking CRUD
class BookingCRUD:
    @staticmethod
    def book_seat(db: Session, user_id: int, train_id: int):
        # Start a transaction
        with db.begin_nested():
            # Lock the train row to prevent race conditions
            db_train = db.query(train.Train).filter(
                train.Train.id == train_id
            ).with_for_update().first()

            # Check seat availability
            if not db_train or db_train.available_seats <= 0:
                raise HTTPException(status_code=400, detail="No seats available")

            # Create booking
            db_booking = booking.Booking(
                user_id=user_id, 
                train_id=train_id, 
                seat_number=f"SEAT-{db_train.total_seats - db_train.available_seats + 1}"
            )
            
            # Update available seats
            db_train.available_seats -= 1
            
            # Add and commit
            db.add(db_booking)
            db.add(db_train)
            db.commit()
            db.refresh(db_booking)
        
        return db_booking