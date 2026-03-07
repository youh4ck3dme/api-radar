# backend/app/users/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from .. import crud, auth, models
from ..auth_neon import get_current_user_or_neon

router = APIRouter()


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    totp: str | None = None


@router.post("/users/register", response_model=dict)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = crud.CRUDUser.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.CRUDUser.create(db, payload.email, payload.password)
    
    # Audit log
    new_log = models.AuditLog(user_id=user.id, action="register", detail="User registered via local auth")
    db.add(new_log)
    db.commit()
    
    return {"id": user.id, "email": user.email}


@router.post("/users/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = crud.CRUDUser.get_by_email(db, payload.email)
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.two_factor_enabled:
        if not payload.totp or not auth.verify_totp(payload.totp, user.totp_secret):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="2FA required or invalid token")
    token = auth.create_access_token(subject=user.email)
    
    # Audit log
    new_log = models.AuditLog(user_id=user.id, action="login", detail="Successful login")
    db.add(new_log)
    db.commit()
    
    return {"access_token": token}


@router.post("/users/2fa/setup", response_model=dict)
def setup_2fa(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_or_neon)):
    # Only allow 2FA setup for local users, not Neon Auth users
    if current_user.hashed_password == "neon_auth_temp":
        raise HTTPException(status_code=400, detail="2FA not available for Neon Auth users")
    
    secret = auth.generate_totp_secret()
    uri = auth.get_totp_uri(secret, current_user.email, issuer_name="Domain-SSL-Manager")
    return {"secret": secret, "otp_auth_url": uri}


class Verify2FAIn(BaseModel):
    token: str
    secret: str


@router.post("/users/2fa/verify", response_model=dict)
def verify_2fa(payload: Verify2FAIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_or_neon)):
    # Only allow 2FA setup for local users, not Neon Auth users
    if current_user.hashed_password == "neon_auth_temp":
        raise HTTPException(status_code=400, detail="2FA not available for Neon Auth users")
    
    if not auth.verify_totp(payload.token, payload.secret):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP token")
    crud.CRUDUser.enable_2fa(db, current_user, payload.secret)
    
    # Audit log
    new_log = models.AuditLog(user_id=current_user.id, action="2fa_enabled", detail="TOTP 2FA enabled")
    db.add(new_log)
    db.commit()
    
    return {"status": "2fa_enabled"}


@router.get("/users/me", response_model=dict)
def me(current_user: models.User = Depends(get_current_user_or_neon)):
    return {"id": current_user.id, "email": current_user.email, "two_factor_enabled": current_user.two_factor_enabled}

