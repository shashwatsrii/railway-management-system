from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.config import settings
from app.core.exceptions import AuthenticationError, InsufficientPermissionsError

# API Key for admin authentication
api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)

def verify_admin_api_key(api_key: str = Security(api_key_header)):
    """
    Verify the admin API key for protected endpoints
    """
    if not api_key or api_key != settings.ADMIN_API_KEY:
        raise InsufficientPermissionsError("Invalid admin API key")
    return True

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    User registration endpoint
    
    - Validates user input
    - Checks for existing username/email
    - Creates user with hashed password
    """
    try:
        auth_service = AuthService(db)
        created_user = auth_service.create_user(user)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login_user(
    login_data: UserLogin, 
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    
    - Authenticates user credentials
    - Generates JWT access token
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(login_data)
        access_token = auth_service.create_user_token(user)
        
        return {
            "access_token": access_token, 
            "token_type": "bearer"
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(lambda: None),  # This will be replaced by a proper token dependency
    db: Session = Depends(get_db)
):
    """
    Get current user details
    
    - Validates JWT token
    - Retrieves user information
    """
    try:
        auth_service = AuthService(db)
        current_user = auth_service.get_current_user(token)
        return current_user
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.post("/admin/register", response_model=UserResponse)
def register_admin(
    user: UserCreate, 
    _: bool = Depends(verify_admin_api_key),
    db: Session = Depends(get_db)
):
    """
    Admin user registration endpoint
    
    - Requires valid admin API key
    - Creates an admin user
    """
    try:
        auth_service = AuthService(db)
        created_user = auth_service.create_user(user)
        
        # Mark the user as admin
        created_user.is_admin = True
        db.commit()
        db.refresh(created_user)
        
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))