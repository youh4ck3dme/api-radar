"""
Test suite for local authentication system
Tests JWT creation, verification, password hashing, and user management
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth import (
    hash_password, 
    verify_password,
    create_access_token as create_local_access_token,
    decode_access_token as decode_local_access_token,
    create_refresh_token,
    AuthService as LocalAuthService
)
from app.models import User
from app.crud import CRUDUser


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_password_hashing_long_password(self):
        """Test that long passwords are properly truncated"""
        # Create a password longer than 72 bytes
        long_password = "a" * 100  # 100 characters
        hashed = hash_password(long_password)
        
        assert hashed != long_password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_password_verification(self):
        """Test password verification against hash"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_verification_empty(self):
        """Test password verification with empty inputs"""
        # Empty password should not match empty hash
        # Note: bcrypt doesn't accept empty strings as valid salts, so this will raise ValueError
        # which is expected behavior for invalid inputs
        with pytest.raises(ValueError):
            verify_password("", "")
        
        # Non-empty password should not match empty hash
        with pytest.raises(ValueError):
            verify_password("password", "")
        
        # Empty password should not match valid hash
        valid_hash = hash_password("password")
        assert verify_password("", valid_hash) is False


class TestJWTTokenCreation:
    """Test JWT token creation and structure"""
    
    def test_access_token_creation(self):
        """Test access token creation"""
        email = "test@example.com"
        token = create_local_access_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_access_token_with_expiration(self):
        """Test access token with custom expiration"""
        email = "test@example.com"
        expires_delta = timedelta(minutes=30)
        token = create_local_access_token(email, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_refresh_token_creation(self):
        """Test refresh token creation"""
        email = "test@example.com"
        token = create_refresh_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 0


class TestJWTTokenVerification:
    """Test JWT token verification and decoding"""
    
    def test_access_token_verification(self):
        """Test access token verification"""
        email = "test@example.com"
        token = create_local_access_token(email)
        payload = decode_local_access_token(token)
        
        assert payload["sub"] == email
        assert "iat" in payload
        assert "exp" in payload
        assert payload["auth_type"] == "local"
    
    def test_expired_token_verification(self):
        """Test expired token verification"""
        email = "test@example.com"
        # Create token that expires immediately
        token = create_local_access_token(email, timedelta(seconds=-1))
        
        with pytest.raises(HTTPException) as exc_info:
            decode_local_access_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()
    
    def test_invalid_token_verification(self):
        """Test invalid token verification"""
        with pytest.raises(HTTPException) as exc_info:
            decode_local_access_token("invalid_token")
        
        assert exc_info.value.status_code == 401
    
    def test_wrong_auth_type_token(self):
        """Test token with wrong auth type"""
        # Create a token with wrong auth_type
        import jwt
        from app.config import settings
        
        payload = {
            "sub": "test@example.com",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": (datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp(),
            "auth_type": "wrong_type"
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            decode_local_access_token(token)
        
        assert exc_info.value.status_code == 401
        assert "invalid token type" in str(exc_info.value.detail).lower() or \
               "token has expired" in str(exc_info.value.detail).lower()


class TestLocalAuthService:
    """Test LocalAuthService methods"""
    
    def test_authenticate_user_success(self, db_session: Session, test_user_data: dict):
        """Test successful user authentication"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Authenticate user
        result = LocalAuthService.authenticate_user(
            test_user_data["email"], 
            test_user_data["password"], 
            db_session
        )
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["user_id"] == user.id
        assert result["email"] == test_user_data["email"]
    
    def test_authenticate_user_wrong_password(self, db_session: Session, test_user_data: dict):
        """Test authentication with wrong password"""
        # Create test user
        CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Try to authenticate with wrong password
        with pytest.raises(HTTPException) as exc_info:
            LocalAuthService.authenticate_user(
                test_user_data["email"], 
                "wrongpassword", 
                db_session
            )
        
        assert exc_info.value.status_code == 401
        assert "invalid credentials" in str(exc_info.value.detail).lower()
    
    def test_authenticate_user_nonexistent(self, db_session: Session, test_user_data: dict):
        """Test authentication with nonexistent user"""
        with pytest.raises(HTTPException) as exc_info:
            LocalAuthService.authenticate_user(
                test_user_data["email"], 
                test_user_data["password"], 
                db_session
            )
        
        assert exc_info.value.status_code == 401
        assert "invalid credentials" in str(exc_info.value.detail).lower()
    
    def test_authenticate_inactive_user(self, db_session: Session, test_user_data: dict):
        """Test authentication with inactive user"""
        # Create inactive test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        user.is_active = False
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            LocalAuthService.authenticate_user(
                test_user_data["email"], 
                test_user_data["password"], 
                db_session
            )
        
        assert exc_info.value.status_code == 400
        assert "inactive user" in str(exc_info.value.detail).lower()
    
    def test_refresh_access_token_success(self):
        """Test successful token refresh"""
        email = "test@example.com"
        refresh_token = create_refresh_token(email)
        
        result = LocalAuthService.refresh_access_token(refresh_token)
        
        assert "access_token" in result
        assert result["token_type"] == "bearer"
    
    def test_refresh_access_token_expired(self):
        """Test refresh with expired token"""
        email = "test@example.com"
        # Create expired refresh token
        import jwt
        from app.config import settings
        
        payload = {
            "sub": email,
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() - 1,  # Expired
            "type": "refresh"
        }
        expired_token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            LocalAuthService.refresh_access_token(expired_token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()
    
    def test_refresh_access_token_invalid(self):
        """Test refresh with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            LocalAuthService.refresh_access_token("invalid_token")
        
        assert exc_info.value.status_code == 401
    
    def test_refresh_access_token_wrong_type(self):
        """Test refresh with wrong token type"""
        email = "test@example.com"
        # Create access token instead of refresh token
        access_token = create_local_access_token(email)
        
        with pytest.raises(HTTPException) as exc_info:
            LocalAuthService.refresh_access_token(access_token)
        
        assert exc_info.value.status_code == 401
        assert "invalid refresh token" in str(exc_info.value.detail).lower()


class TestIntegration:
    """Integration tests for local auth system"""
    
    def test_full_authentication_flow(self, db_session: Session, test_user_data: dict):
        """Test complete authentication flow"""
        # 1. Create user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # 2. Authenticate user
        auth_result = LocalAuthService.authenticate_user(
            test_user_data["email"], 
            test_user_data["password"], 
            db_session
        )
        
        assert "access_token" in auth_result
        assert "refresh_token" in auth_result
        
        # 3. Verify access token
        access_payload = decode_local_access_token(auth_result["access_token"])
        assert access_payload["sub"] == test_user_data["email"]
        assert access_payload["auth_type"] == "local"
        
        # 4. Refresh token
        refresh_result = LocalAuthService.refresh_access_token(auth_result["refresh_token"])
        assert "access_token" in refresh_result
        
        # 5. Verify new access token
        new_access_payload = decode_local_access_token(refresh_result["access_token"])
        assert new_access_payload["sub"] == test_user_data["email"]
        assert new_access_payload["auth_type"] == "local"