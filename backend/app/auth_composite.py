"""
Composite authentication system
Integrates Neon Auth (trial) with local authentication
Provides seamless fallback and migration capabilities
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .crud import CRUDUser
from .neon_auth import verify_neon_auth_token, is_neon_trial_active
from .auth import decode_access_token, AuthService
from .auth_neon import get_neon_auth_user

security = HTTPBearer()

class CompositeAuthService:
    """Service that handles both Neon Auth and local authentication"""
    
    def __init__(self):
        self.neon_fallback_count = 0
        self.max_fallbacks = 3  # Max consecutive Neon Auth failures before switching
    
    def authenticate_composite(
        self, 
        credentials: HTTPAuthorizationCredentials, 
        db: Session
    ) -> User:
        """
        Authenticate using Neon Auth first, fall back to local auth
        """
        token = credentials.credentials
        
        # Try Neon Auth first if trial is active
        if is_neon_trial_active():
            try:
                return get_neon_auth_user(credentials, db)
            except HTTPException as e:
                # If Neon Auth fails with 503 (not available), try local auth
                if e.status_code == 503:
                    pass  # Continue to local auth
                else:
                    raise  # Re-raise other errors
        
        # Fall back to local authentication
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
    
    def login_composite(
        self, 
        email: str, 
        password: str, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Login using composite authentication
        """
        # Try local authentication first
        try:
            return AuthService.authenticate_user(email, password, db)
        except HTTPException as e:
            # If local auth fails and Neon Auth is available, try Neon Auth
            if e.status_code == 401 and is_neon_trial_active():
                # For Neon Auth, we would need to redirect to their login page
                # This is a simplified version - in reality, you'd redirect to Neon Auth
                raise HTTPException(
                    status_code=400, 
                    detail="Local authentication failed. Please use Neon Auth login."
                )
            else:
                raise

# Global instance
composite_auth_service = CompositeAuthService()

def get_current_user_composite(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user using composite authentication"""
    return composite_auth_service.authenticate_composite(credentials, db)

def login_composite(
    email: str, 
    password: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Login using composite authentication"""
    return composite_auth_service.login_composite(email, password, db)

# Migration utilities
class AuthMigrationService:
    """Service for migrating between authentication systems"""
    
    @staticmethod
    def migrate_neon_to_local(neon_token: str, new_password: str, db: Session) -> User:
        """
        Migrate user from Neon Auth to local authentication
        """
        try:
            # Verify Neon Auth token
            user_info = verify_neon_auth_token(neon_token)
            email = user_info.get("email")
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in Neon token")
            
            # Get existing user
            user = CRUDUser.get_by_email(db, email)
            if not user:
                # Create new user with local auth
                user = CRUDUser.create(db, email, new_password)
            else:
                # Update existing user to use local auth
                from .auth_local import hash_password
                user.hashed_password = hash_password(new_password)
                user.is_active = True
                db.add(user)
                db.commit()
                db.refresh(user)
            
            return user
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Migration failed: {str(e)}")
    
    @staticmethod
    def check_auth_status() -> Dict[str, Any]:
        """Check status of both authentication systems"""
        from datetime import datetime, timezone
        return {
            "neon_auth_active": is_neon_trial_active(),
            "local_auth_available": True,  # Always available
            "recommended_auth": "neon" if is_neon_trial_active() else "local",
            "last_checked": datetime.now(timezone.utc).isoformat()
        }