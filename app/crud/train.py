from sqlalchemy.orm import Session
from app.models.train import Train
from app.schemas.train import TrainCreate, TrainAvailabilityRequest
from fastapi import HTTPException
from typing import List

def create_train(db: Session, train: TrainCreate):
    # Check if train with same train number already exists
    existing_train = db.query(Train).filter(
        Train.train_number == train.train_number
    ).first()
    
    if existing_train:
        raise HTTPException(
            status_code=400, 
            detail="Train with this number already exists"
        )
    
    db_train = Train(
        train_number=train.train_number,
        train_name=train.train_name,
        source_station=train.source_station,
        destination_station=train.destination_station,
        total_seats=train.total_seats,
        available_seats=train.total_seats,
        ticket_price=train.ticket_price
    )
    
    db.add(db_train)
    db.commit()
    db.refresh(db_train)
    return db_train

def get_train_availability(db: Session, request: TrainAvailabilityRequest) -> List[Train]:
    return db.query(Train).filter(
        Train.source_station == request.source,
        Train.destination_station == request.destination,
        Train.available_seats > 0
    ).all()

def update_train_seats(db: Session, train_id: int, seats_to_reduce: int):
    train = db.query(Train).filter(Train.id == train_id).first()
    
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    if train.available_seats < seats_to_reduce:
        raise HTTPException(
            status_code=400, 
            detail="Not enough seats available"
        )
    
    train.available_seats -= seats_to_reduce
    db.commit()
    db.refresh(train)
    return train
