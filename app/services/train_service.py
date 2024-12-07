from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import Depends, HTTPException

from app.models.train import Train
from app.schemas.train import TrainCreate, TrainUpdate, TrainAvailabilityResponse
from app.db.session import get_db
from app.core.exceptions import ResourceNotFoundError

class TrainService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_train(self, train_data: TrainCreate):
        """
        Create a new train with initial available seats equal to total seats
        
        Args:
            train_data (TrainCreate): Details of the train to be created
        
        Returns:
            Train: Created train object
        """
        # Check if train number already exists
        existing_train = self.db.query(Train).filter(
            Train.train_number == train_data.train_number
        ).first()
        
        if existing_train:
            raise HTTPException(
                status_code=400, 
                detail="Train with this number already exists"
            )
        
        # Create new train
        db_train = Train(
            **train_data.dict(),
            available_seats=train_data.total_seats
        )
        
        self.db.add(db_train)
        self.db.commit()
        self.db.refresh(db_train)
        
        return db_train

    def update_train(self, train_id: int, train_data: TrainUpdate):
        """
        Update existing train details
        
        Args:
            train_id (int): ID of the train to update
            train_data (TrainUpdate): Updated train details
        
        Returns:
            Train: Updated train object
        """
        db_train = self.db.query(Train).filter(Train.id == train_id).first()
        
        if not db_train:
            raise ResourceNotFoundError("Train not found")
        
        # Update train details
        for key, value in train_data.dict(exclude_unset=True).items():
            setattr(db_train, key, value)
        
        self.db.commit()
        self.db.refresh(db_train)
        
        return db_train

    def get_train_availability(self, source: str, destination: str):
        """
        Find trains with availability between given source and destination
        
        Args:
            source (str): Starting station
            destination (str): Ending station
        
        Returns:
            TrainAvailabilityResponse: List of available trains
        """
        available_trains = self.db.query(Train).filter(
            and_(
                Train.source == source, 
                Train.destination == destination,
                Train.available_seats > 0
            )
        ).all()
        
        return TrainAvailabilityResponse(trains=available_trains)

    def get_train_by_id(self, train_id: int):
        """
        Retrieve train by its ID
        
        Args:
            train_id (int): ID of the train
        
        Returns:
            Train: Train object
        """
        train = self.db.query(Train).filter(Train.id == train_id).first()
        
        if not train:
            raise ResourceNotFoundError("Train not found")
        
        return train