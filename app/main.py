from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, train, booking
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

def create_tables():
    Base.metadata.create_all(bind=engine)

def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Railway Management System API"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(train.router, prefix="/trains", tags=["Trains"])
    app.include_router(booking.router, prefix="/booking", tags=["Bookings"])

    # Create database tables
    create_tables()

    return app

app = start_application()