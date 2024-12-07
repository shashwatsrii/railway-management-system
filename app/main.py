from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import OperationalError
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from routes.routes import auth_router, train_router, booking_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Railway Management System",
    description="IRCTC-like Railway Booking API",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(train_router, prefix="/trains", tags=["Trains"])
app.include_router(booking_router, prefix="/bookings", tags=["Bookings"])

@app.get("/")
async def root():
    return {"message": "Welcome to Railway Management System"}

