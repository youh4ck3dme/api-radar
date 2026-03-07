"""
Neon Auth integration for trial period
Provides authentication using Neon Auth while building our own system
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .neon_auth import verify_neon_auth_token, is_neon_trial_active
from .models import User
from .crud import CRUDUser
from .db import get_db
from sqlalchemy.orm import Session

security = HTTPBearer(auto_error=False)

def get_neon_auth_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user from Neon Auth token
    Falls back to local auth if Neon Auth trial is not active
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    
    # Check if Neon Auth trial is active
    if not is_neon_trial_active():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neon Auth trial is not available. Please use local authentication."
        )
    
    try:
        # Verify Neon Auth token
        user_info = verify_neon_auth_token(token)
        
        # Get or create user in local database
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")
        
        user = CRUDUser.get_by_email(db, email)
        
        # Create user if doesn't exist
        if not user:
            user = CRUDUser.create(
                db=db,
                email=email,
                password="neon_auth_temp",  # Temporary password for Neon Auth users
                role=None
            )
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def get_current_user_or_neon(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Try Neon Auth first, fall back to local JWT auth
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    
    # Try Neon Auth first
    if is_neon_trial_active():
        try:
            return get_neon_auth_user(credentials, db)
        except HTTPException as e:
            # If Neon Auth fails, try local auth
            if e.status_code == 401 or e.status_code == 503:
                pass  # Continue to local auth
            else:
                raise
    
    # Fall back to local JWT authentication
    from .auth import decode_access_token
    from .deps import get_current_user
    
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = CRUDUser.get_by_email(db, email)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive user")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Add to requirements.txt: pyjwt[crypto]