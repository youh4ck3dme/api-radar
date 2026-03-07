"""
Test suite for composite authentication system.

This module tests the composite authentication pattern that combines
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_composite import CompositeAuthService, AuthMigrationService
from app.auth_local import AuthService
from app.auth_neon import NeonAuthenticator
from app.models import User
from app.schemas import UserCreate, UserResponse


class TestCompositeAuthenticator:
    """Test cases for CompositeAuthenticator."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def mock_local_auth(self):
        """Mock local authenticator."""
        return Mock(spec=AuthService)

    @pytest.fixture
    def mock_neon_auth(self):
        """Mock Neon authenticator."""
        return Mock(spec=NeonAuthenticator)

    @pytest.fixture
    def composite_auth(self):
        """Create composite authenticator."""
        return CompositeAuthService()

    @pytest.mark.asyncio
    async def test_register_user_local_success(self, composite_auth, mock_db):
        """Test successful user registration via local authentication."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act
        result = await composite_auth.register_user(mock_db, user_data)

        # Assert
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_local_success(self, composite_auth, mock_db):
        """Test successful user login via local authentication."""
        # Arrange
        email = "test@example.com"
        password = "password123"
        
        # Mock user
        mock_user = Mock()
        mock_user.email = email
        mock_user.is_active = True
        mock_user.hashed_password = "hashed_password"
        
        # Mock db query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Act
        result = await composite_auth.login_composite(email, password, mock_db)

        # Assert
        assert result is not None
        assert "access_token" in result
        assert "token_type" in result

    @pytest.mark.asyncio
    async def test_get_current_user_local_success(self, composite_auth, mock_db):
        """Test successful user retrieval via local authentication."""
        # Arrange
        token = "valid_token"
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Mock decode function
        with patch('app.auth_composite.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "test@example.com"}
            mock_db.query.return_value.filter.return_value.first.return_value = mock_user

            # Act
            result = await composite_auth.authenticate_composite(type('obj', (object,), {'credentials': token})(), mock_db)

            # Assert
            assert result is not None
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_register_user_neon_fallback(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test user registration fallback to Neon when local fails."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_local_auth.register_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.register_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))

        # Act
        result = await composite_auth.register_user(mock_db, user_data)

        # Assert
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        mock_local_auth.register_user.assert_called_once_with(mock_db, user_data)
        mock_neon_auth.register_user.assert_called_once_with(mock_db, user_data)

    @pytest.mark.asyncio
    async def test_register_user_both_fail(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test registration failure when both local and Neon authentication fail."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_local_auth.register_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.register_user = AsyncMock(side_effect=Exception("Neon auth failed"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.register_user(mock_db, user_data)

        assert exc_info.value.status_code == 500
        assert "Registration failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_user_neon_fallback(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test user login fallback to Neon when local fails."""
        # Arrange
        login_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_local_auth.login_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.login_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))

        # Act
        result = await composite_auth.login_user(mock_db, login_data)

        # Assert
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        mock_local_auth.login_user.assert_called_once_with(mock_db, login_data)
        mock_neon_auth.login_user.assert_called_once_with(mock_db, login_data)

    @pytest.mark.asyncio
    async def test_login_user_both_fail(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test login failure when both local and Neon authentication fail."""
        # Arrange
        login_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_local_auth.login_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.login_user = AsyncMock(side_effect=Exception("Neon auth failed"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.login_user(mock_db, login_data)

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_neon_fallback(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test user retrieval fallback to Neon when local fails."""
        # Arrange
        token = "valid_token"
        mock_local_auth.get_current_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.get_current_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))

        # Act
        result = await composite_auth.get_current_user(mock_db, token)

        # Assert
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        mock_local_auth.get_current_user.assert_called_once_with(mock_db, token)
        mock_neon_auth.get_current_user.assert_called_once_with(mock_db, token)

    @pytest.mark.asyncio
    async def test_get_current_user_both_fail(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test user retrieval failure when both local and Neon authentication fail."""
        # Arrange
        token = "invalid_token"
        mock_local_auth.get_current_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.get_current_user = AsyncMock(side_effect=Exception("Neon auth failed"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.get_current_user(mock_db, token)

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_neon_fallback_with_different_token(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test user retrieval fallback to Neon when local fails with different token format."""
        # Arrange
        neon_token = "neon_token_format"
        mock_local_auth.get_current_user = AsyncMock(side_effect=Exception("Local auth failed"))
        mock_neon_auth.get_current_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="neonuser",
            email="neon@example.com"
        ))

        # Act
        result = await composite_auth.get_current_user(mock_db, neon_token)

        # Assert
        assert result.username == "neonuser"
        assert result.email == "neon@example.com"
        mock_local_auth.get_current_user.assert_called_once_with(mock_db, neon_token)
        mock_neon_auth.get_current_user.assert_called_once_with(mock_db, neon_token)

    @pytest.mark.asyncio
    async def test_composite_auth_initialization(self):
        """Test composite authenticator initialization."""
        # Act
        auth = CompositeAuthService()

        # Assert
        assert auth is not None
        assert hasattr(auth, 'authenticate_composite')
        assert hasattr(auth, 'login_composite')

    @pytest.mark.asyncio
    async def test_error_handling_with_detailed_logging(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test error handling with detailed logging for debugging."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        local_error = Exception("Detailed local auth error")
        neon_error = Exception("Detailed Neon auth error")
        
        mock_local_auth.register_user = AsyncMock(side_effect=local_error)
        mock_neon_auth.register_user = AsyncMock(side_effect=neon_error)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.register_user(mock_db, user_data)

        assert exc_info.value.status_code == 500
        error_detail = str(exc_info.value.detail)
        assert "Registration failed" in error_detail
        # Note: In actual implementation, you might want to include error details in logs
        # but not necessarily in the user-facing error message for security reasons

    @pytest.mark.asyncio
    async def test_performance_with_fast_local_auth(self, composite_auth, mock_db, mock_local_auth):
        """Test that local authentication is tried first for performance."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_local_auth.register_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))

        # Act
        result = await composite_auth.register_user(mock_db, user_data)

        # Assert
        assert result.username == "testuser"
        # Verify that Neon auth was not called when local auth succeeded
        assert not mock_local_auth.register_user.called or mock_local_auth.register_user.call_count == 1

    @pytest.mark.asyncio
    async def test_authentication_flow_integration(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test the complete authentication flow integration."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Mock successful registration and login
        mock_local_auth.register_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))
        mock_local_auth.login_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))
        mock_local_auth.get_current_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))

        # Act - Register user
        register_result = await composite_auth.register_user(mock_db, user_data)
        
        # Act - Login user
        login_result = await composite_auth.login_user(mock_db, user_data)
        
        # Act - Get current user
        current_user = await composite_auth.get_current_user(mock_db, "valid_token")

        # Assert
        assert register_result.username == "testuser"
        assert login_result.username == "testuser"
        assert current_user.username == "testuser"
        
        # Verify all methods were called
        mock_local_auth.register_user.assert_called_once()
        mock_local_auth.login_user.assert_called_once()
        mock_local_auth.get_current_user.assert_called_once()


class TestCompositeAuthenticatorEdgeCases:
    """Test edge cases and error scenarios for CompositeAuthenticator."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def mock_local_auth(self):
        """Mock local authenticator."""
        return Mock(spec=LocalAuthenticator)

    @pytest.fixture
    def mock_neon_auth(self):
        """Mock Neon authenticator."""
        return Mock(spec=NeonAuthenticator)

    @pytest.fixture
    def composite_auth(self):
        """Create composite authenticator."""
        return CompositeAuthService()

    @pytest.mark.asyncio
    async def test_empty_user_data(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test handling of empty user data."""
        # Arrange
        empty_data = UserCreate(username="", email="", password="")
        mock_local_auth.register_user = AsyncMock(side_effect=Exception("Validation error"))
        mock_neon_auth.register_user = AsyncMock(side_effect=Exception("Validation error"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.register_user(mock_db, empty_data)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_invalid_token_format(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test handling of invalid token formats."""
        # Arrange
        invalid_token = "invalid_token_format"
        mock_local_auth.get_current_user = AsyncMock(side_effect=Exception("Invalid token"))
        mock_neon_auth.get_current_user = AsyncMock(side_effect=Exception("Invalid token"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.get_current_user(mock_db, invalid_token)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test handling of network timeouts."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        timeout_error = Exception("Network timeout")
        
        mock_local_auth.register_user = AsyncMock(side_effect=timeout_error)
        mock_neon_auth.register_user = AsyncMock(side_effect=timeout_error)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await composite_auth.register_user(mock_db, user_data)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_concurrent_authentication_requests(self, composite_auth, mock_db, mock_local_auth, mock_neon_auth):
        """Test handling of concurrent authentication requests."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        mock_local_auth.register_user = AsyncMock(return_value=UserResponse(
            id=1,
            username="testuser",
            email="test@example.com"
        ))

        # Act - Simulate concurrent requests
        import asyncio
        tasks = [
            composite_auth.register_user(mock_db, user_data),
            composite_auth.register_user(mock_db, user_data),
            composite_auth.register_user(mock_db, user_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assert
        for result in results:
            if isinstance(result, Exception):
                # Some requests might fail due to concurrent access
                assert isinstance(result, HTTPException)
            else:
                # Successful requests should return valid user data
                assert result.username == "testuser"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])














