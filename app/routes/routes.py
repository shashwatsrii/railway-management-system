from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import user, train, booking
from models import user as user_schema, train as train_schema, booking as booking_schema
from crud.crud import UserCRUD, TrainCRUD, BookingCRUD
from utils import security

# Authentication Router
auth_router = APIRouter()

@auth_router.post("/register", response_model=user_schema.UserResponse)
def register_user(user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(user.User).filter(
        (user.User.username == user_data.username) | 
        (user.User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    return UserCRUD.create_user(db, user_data)

@auth_router.post("/login")
def login_user(user_data: user_schema.UserLogin, db: Session = Depends(get_db)):
    db_user = UserCRUD.get_user_by_username(db, user_data.username)
    
    if not db_user or not security.verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = security.create_access_token(
        data={"sub": db_user.username, "is_admin": db_user.is_admin}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Train Router
train_router = APIRouter()

@train_router.post("/", response_model=train_schema.TrainResponse, dependencies=[Depends(security.verify_admin_api_key)])
def create_train(train_data: train_schema.TrainCreate, db: Session = Depends(get_db)):
    return TrainCRUD.create_train

@train_router.get("/search", response_model=List[train_schema.TrainResponse])
def search_trains(source: str, destination: str, db: Session = Depends(get_db)):
    """
    Search for trains between source and destination
    """
    trains = TrainCRUD.get_trains_by_route(db, source, destination)
    return trains

@train_router.put("/{train_id}", response_model=train_schema.TrainResponse, dependencies=[Depends(security.verify_admin_api_key)])
def update_train(train_id: int, train_data: train_schema.TrainUpdate, db: Session = Depends(get_db)):
    """
    Update train details (Admin only)
    """
    db_train = db.query(train.Train).filter(train.Train.id == train_id).first()
    if not db_train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    # Update train details
    for key, value in train_data.dict(exclude_unset=True).items():
        setattr(db_train, key, value)
    
    db.commit()
    db.refresh(db_train)
    return db_train

# Booking Router
booking_router = APIRouter()

@booking_router.post("/", response_model=booking_schema.BookingResponse)
def book_seat(
    booking_data: booking_schema.BookingCreate, 
    db: Session = Depends(get_db), 
    current_user: user.User = Depends(security.get_current_user)
):
    """
    Book a seat for the logged-in user
    """
    try:
        booking = BookingCRUD.book_seat(db, current_user.id, booking_data.train_id)
        return booking
    except HTTPException as e:
        raise e

@booking_router.get("/", response_model=List[booking_schema.BookingResponse])
def get_user_bookings(
    db: Session = Depends(get_db), 
    current_user: user.User = Depends(security.get_current_user)
):
    """
    Get all bookings for the current user
    """
    bookings = db.query(booking.Booking).filter(booking.Booking.user_id == current_user.id).all()
    return bookings

# Additional Security Utilities
def get_current_user(token: str):
    """
    Decode JWT token and retrieve current user
    """
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")