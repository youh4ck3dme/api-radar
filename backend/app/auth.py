# backend/app/auth.py

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import pyotp
from fastapi import HTTPException, status
from .config import settings

# Create bcrypt context with manual backend to avoid passlib version detection issues
import bcrypt as _bcrypt

class BcryptContext:
    """Simple bcrypt wrapper to avoid passlib version detection issues"""
    
    def hash(self, password: str) -> str:
        """Hash password using bcrypt directly"""
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
    
    def verify(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

pwd_context = BcryptContext()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    # Truncate password to 72 bytes to avoid bcrypt limitation
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Truncate password to 72 bytes to avoid bcrypt limitation
    if len(plain.encode('utf-8')) > 72:
        plain = plain[:72]
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token"""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": subject, 
        "iat": now.timestamp(), 
        "exp": expire.timestamp(),
        "auth_type": "local" # Added for compatibility with auth_local.py logic
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT access token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("auth_type") not in ("local", None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def create_refresh_token(subject: str) -> str:
    """Create refresh token with longer expiration"""
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": expire.timestamp(),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def authenticate_user(email: str, password: str, db) -> dict:
        """Authenticate user with email and password"""
        from .crud import CRUDUser
        
        user = CRUDUser.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        # Create tokens
        access_token = create_access_token(user.email)
        refresh_token = create_refresh_token(user.email)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Create new access token
            access_token = create_access_token(payload["sub"])
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer_name: str = "DSM") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)


def verify_totp(token: str, secret: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

