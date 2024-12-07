from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreate, BookingResponse, BookingSearchCriteria
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/book", response_model=BookingResponse)
def book_seat(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint for booking a seat
    
    - Requires user authentication
    - Handles seat availability
    - Manages race conditions during booking
    """
    booking_service = BookingService(db)
    booking = booking_service.book_seat(current_user, booking_data)
    
    # Enhance response with train details
    booking_response = BookingResponse(
        **booking.__dict__,
        train_details={
            "train_number": booking.train.train_number,
            "name": booking.train.name,
            "source": booking.train.source,
            "destination": booking.train.destination
        }
    )
    
    return booking_response

@router.get("/my-bookings", response_model=list[BookingResponse])
def get_user_bookings(
    search_criteria: BookingSearchCriteria = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve user's bookings
    
    - Requires user authentication
    - Supports optional filtering
    """
    booking_service = BookingService(db)
    bookings = booking_service.get_user_bookings(current_user, search_criteria)
    
    # Enhance bookings with train details
    enhanced_bookings = [
        BookingResponse(
            **booking.__dict__,
            train_details={
                "train_number": booking.train.train_number,
                "name": booking.train.name,
                "source": booking.train.source,
                "destination": booking.train.destination
            }
        ) for booking in bookings
    ]
    
    return enhanced_bookings

@router.delete("/cancel/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint to cancel a booking
    
    - Requires user authentication
    - Allows user to cancel their own bookings
    """
    booking_service = BookingService(db)
    cancellation_status = booking_service.cancel_booking(current_user, booking_id)
    
    return {"message": "Booking cancelled successfully"}