"""
Authentication endpoints
Provides login, registration, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .crud import CRUDUser
from .auth import AuthService, create_access_token, create_refresh_token
from .auth_composite import login_composite, AuthMigrationService
from .auth_neon import is_neon_trial_active
from . import models
# Importujeme limiter z instrumentation
from .instrumentation import limiter

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class MigrateRequest(BaseModel):
    neon_token: str
    new_password: str

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password (local auth)"""
    try:
        result = AuthService.authenticate_user(login_data.email, login_data.password, db)
        
        # Audit log
        user = CRUDUser.get_by_email(db, login_data.email)
        if user:
            new_log = models.AuditLog(user_id=user.id, action="login", detail="Successful login via auth endpoint")
            db.add(new_log)
            db.commit()
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/auth/register")
@limiter.limit("3/hour")
async def register(request: Request, register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user with email and password"""
    try:
        # Check if user already exists
        existing = CRUDUser.get_by_email(db, register_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user = CRUDUser.create(db, register_data.email, register_data.password)
        
        # Create access and refresh tokens
        access_token = create_access_token(user.email)
        refresh_token = create_refresh_token(user.email)

        # Audit log
        new_log = models.AuditLog(user_id=user.id, action="register", detail="User registered via auth endpoint")
        db.add(new_log)
        db.commit()

        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/auth/refresh")
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        result = AuthService.refresh_access_token(request.refresh_token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@router.get("/auth/status")
async def auth_status():
    """Get authentication system status"""
    return AuthMigrationService.check_auth_status()

@router.post("/auth/migrate")
async def migrate_to_local(request: MigrateRequest, db: Session = Depends(get_db)):
    """Migrate user from Neon Auth to local authentication"""
    try:
        user = AuthMigrationService.migrate_neon_to_local(request.neon_token, request.new_password, db)
        return {
            "message": "Successfully migrated to local authentication",
            "user_id": user.id,
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@router.get("/auth/neon/login-url")
async def get_neon_login_url():
    """Get Neon Auth login URL for trial users"""
    from .neon_auth import neon_auth_service
    
    if not is_neon_trial_active():
        raise HTTPException(status_code=400, detail="Neon Auth trial is not available")
    
    login_url = neon_auth_service.get_login_url()
    return {
        "login_url": login_url,
        "message": "Redirect user to this URL for Neon Auth login"
    }

@router.get("/auth/neon/callback")
async def neon_auth_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Neon Auth callback (simplified version)
    In reality, this would exchange the code for a token
    """
    if not is_neon_trial_active():
        raise HTTPException(status_code=400, detail="Neon Auth trial is not available")
    
    # This is a simplified version - in reality, you'd exchange the code for a token
    # and then verify the token to get user info
    return {
        "message": "Neon Auth callback received",
        "code": code,
        "note": "In production, exchange this code for an access token"
    }

# Add these endpoints to main.py
# app.include_router(auth_endpoints.router, prefix="/api")