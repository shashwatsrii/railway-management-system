from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError, InsufficientPermissionsError

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """
    Dependency to get the current authenticated user
    
    - Validates JWT token
    - Retrieves user details
    - Raises authentication errors if token is invalid
    """
    auth_service = AuthService(db)
    try:
        user = auth_service.get_current_user(token)
        return user
    except AuthenticationError:
        raise

def require_admin(current_user = Depends(get_current_user)):
    """
    Dependency to ensure only admin users can access an endpoint
    
    - Checks if the current user is an admin
    - Raises permission error if not
    """
    if not current_user.is_admin:
        raise InsufficientPermissionsError("Admin access required")
    return current_user