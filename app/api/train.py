from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.train_service import TrainService
from app.schemas.train import TrainCreate, TrainUpdate, TrainResponse, TrainAvailabilityResponse
from app.core.dependencies import require_admin, get_current_user
from app.core.config import settings

router = APIRouter()

@router.post("/add", response_model=TrainResponse)
def add_train(
    train_data: TrainCreate, 
    _: bool = Depends(require_admin),  # Ensures only admin can add trains
    db: Session = Depends(get_db)
):
    """
    Endpoint to add a new train
    
    - Requires admin authentication
    - Validates train data
    - Prevents duplicate train numbers
    """
    train_service = TrainService(db)
    return train_service.create_train(train_data)

@router.put("/{train_id}", response_model=TrainResponse)
def update_train(
    train_id: int,
    train_data: TrainUpdate,
    _: bool = Depends(require_admin),  # Ensures only admin can update trains
    db: Session = Depends(get_db)
):
    """
    Endpoint to update an existing train
    
    - Requires admin authentication
    - Allows partial updates
    """
    train_service = TrainService(db)
    return train_service.update_train(train_id, train_data)

@router.get("/availability", response_model=TrainAvailabilityResponse)
def check_train_availability(
    source: str, 
    destination: str,
    _: bool = Depends(get_current_user),  # Requires user authentication
    db: Session = Depends(get_db)
):
    """
    Endpoint to check train availability between stations
    
    - Requires user authentication
    - Returns trains with available seats
    """
    train_service = TrainService(db)
    return train_service.get_train_availability(source, destination)

@router.get("/{train_id}", response_model=TrainResponse)
def get_train_details(
    train_id: int,
    _: bool = Depends(get_current_user),  # Requires user authentication
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve train details by ID
    
    - Requires user authentication
    """
    train_service = TrainService(db)
    return train_service.get_train_by_id(train_id)