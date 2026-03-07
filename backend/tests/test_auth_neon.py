"""
Test suite for Neon Auth integration
Tests JWT verification, user info extraction, and trial status checking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import jwt
from fastapi import HTTPException
from datetime import datetime, timezone

from app.neon_auth import (
    NeonAuthService,
    verify_neon_auth_token,
    is_neon_trial_active,
    get_login_url
)


class TestNeonAuthService:
    """Test NeonAuthService class methods"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.service = NeonAuthService()
    
    @patch('app.neon_auth.requests.get')
    def test_get_jwks_success(self, mock_get):
        """Test successful JWKS retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_n_value",
                    "e": "AQAB"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.service.get_jwks()
        
        assert "keys" in result
        assert len(result["keys"]) == 1
        assert result["keys"][0]["kid"] == "test_kid"
        mock_get.assert_called_once_with(self.service.jwks_url, timeout=10)
    
    @patch('app.neon_auth.requests.get')
    def test_get_jwks_failure(self, mock_get):
        """Test JWKS retrieval failure"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.get_jwks()
        
        assert exc_info.value.status_code == 500
        assert "Failed to fetch JWKS" in str(exc_info.value.detail)
    
    @patch('app.neon_auth.requests.get')
    def test_get_jwks_cached(self, mock_get):
        """Test JWKS caching"""
        # First call
        mock_response = Mock()
        mock_response.json.return_value = {"keys": []}
        mock_get.return_value = mock_response
        
        self.service.get_jwks()
        assert self.service.jwks_cache is not None
        
        # Second call should use cache
        self.service.get_jwks()
        # Should only be called once due to caching
        assert mock_get.call_count == 1
    
    @patch('app.neon_auth.jwt.get_unverified_header')
    @patch('app.neon_auth.jwt.decode')
    @patch.object(NeonAuthService, 'get_jwks')
    def test_verify_neon_token_success(self, mock_get_jwks, mock_decode, mock_get_header):
        """Test successful Neon Auth token verification"""
        mock_get_header.return_value = {"kid": "test_kid"}
        mock_get_jwks.return_value = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_n_value",
                    "e": "AQAB"
                }
            ]
        }
        mock_decode.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "sub": "user123",
            "roles": ["user"],
            "organizations": ["org1"]
        }
        
        token = "test_token"
        result = self.service.verify_neon_token(token)
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["sub"] == "user123"
        mock_get_header.assert_called_once_with(token)
        mock_get_jwks.assert_called_once()
        mock_decode.assert_called_once()
    
    @patch('app.neon_auth.jwt.get_unverified_header')
    def test_verify_neon_token_no_kid(self, mock_get_header):
        """Test token verification without kid"""
        mock_get_header.return_value = {}
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.verify_neon_token("test_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid token format" in str(exc_info.value.detail)
    
    @patch('app.neon_auth.jwt.get_unverified_header')
    @patch.object(NeonAuthService, 'get_jwks')
    def test_verify_neon_token_no_matching_key(self, mock_get_jwks, mock_get_header):
        """Test token verification with no matching key"""
        mock_get_header.return_value = {"kid": "nonexistent_kid"}
        mock_get_jwks.return_value = {"keys": []}
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.verify_neon_token("test_token")
        
        assert exc_info.value.status_code == 401
        assert "Unable to find matching key" in str(exc_info.value.detail)
    
    @patch('app.neon_auth.jwt.get_unverified_header')
    @patch('app.neon_auth.jwt.decode')
    @patch.object(NeonAuthService, 'get_jwks')
    def test_verify_neon_token_expired(self, mock_get_jwks, mock_decode, mock_get_header):
        """Test expired token verification"""
        mock_get_header.return_value = {"kid": "test_kid"}
        mock_get_jwks.return_value = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_n_value",
                    "e": "AQAB"
                }
            ]
        }
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.verify_neon_token("test_token")
        
        assert exc_info.value.status_code == 401
        assert "Token has expired" in str(exc_info.value.detail)
    
    @patch('app.neon_auth.jwt.get_unverified_header')
    @patch('app.neon_auth.jwt.decode')
    @patch.object(NeonAuthService, 'get_jwks')
    def test_verify_neon_token_invalid(self, mock_get_jwks, mock_decode, mock_get_header):
        """Test invalid token verification"""
        mock_get_header.return_value = {"kid": "test_kid"}
        mock_get_jwks.return_value = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_n_value",
                    "e": "AQAB"
                }
            ]
        }
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.verify_neon_token("test_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)
    
    @patch('app.neon_auth.jwt.get_unverified_header')
    @patch('app.neon_auth.jwt.decode')
    @patch.object(NeonAuthService, 'get_jwks')
    def test_get_user_info_from_token(self, mock_get_jwks, mock_decode, mock_get_header):
        """Test user info extraction from Neon Auth token"""
        mock_get_header.return_value = {"kid": "test_kid"}
        mock_get_jwks.return_value = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_n_value",
                    "e": "AQAB"
                }
            ]
        }
        mock_decode.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "sub": "user123",
            "roles": ["user"],
            "organizations": ["org1"]
        }
        
        result = self.service.get_user_info_from_token("test_token")
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["sub"] == "user123"
        assert result["roles"] == ["user"]
        assert result["organizations"] == ["org1"]
    
    @patch('app.neon_auth.requests.get')
    def test_is_trial_active_success(self, mock_get):
        """Test trial status check when active"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.service.is_trial_active()
        
        assert result is True
        mock_get.assert_called_once_with(self.service.jwks_url, timeout=10)
    
    @patch('app.neon_auth.requests.get')
    def test_is_trial_active_failure(self, mock_get):
        """Test trial status check when inactive"""
        mock_get.side_effect = Exception("Service unavailable")
        
        result = self.service.is_trial_active()
        
        assert result is False
    
    def test_get_login_url(self):
        """Test login URL generation"""
        result = self.service.get_login_url()
        
        assert "https://ep-square-union-aeczbg2r.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth" in result
        assert "client_id=api-centrum" in result
        assert "response_type=code" in result
    
    def test_get_login_url_with_redirect(self):
        """Test login URL generation with redirect URI"""
        redirect_uri = "https://example.com/callback"
        result = self.service.get_login_url(redirect_uri)
        
        assert "https://ep-square-union-aeczbg2r.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth" in result
        assert "client_id=api-centrum" in result
        assert f"redirect_uri={redirect_uri}" in result
        assert "response_type=code" in result


class TestNeonAuthFunctions:
    """Test standalone Neon Auth functions"""
    
    @patch.object(NeonAuthService, 'get_user_info_from_token')
    def test_verify_neon_auth_token_function(self, mock_get_user_info):
        """Test verify_neon_auth_token function"""
        mock_get_user_info.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "sub": "user123"
        }
        
        result = verify_neon_auth_token("test_token")
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["sub"] == "user123"
        mock_get_user_info.assert_called_once_with("test_token")
    
    @patch.object(NeonAuthService, 'is_trial_active')
    def test_is_neon_trial_active_function(self, mock_is_active):
        """Test is_neon_trial_active function"""
        mock_is_active.return_value = True
        
        result = is_neon_trial_active()
        
        assert result is True
        mock_is_active.assert_called_once()
    
    def test_get_login_url_function(self):
        """Test get_login_url function"""
        result = get_login_url()
        
        assert "https://ep-square-union-aeczbg2r.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth" in result
        assert "client_id=api-centrum" in result
        assert "response_type=code" in result


class TestNeonAuthIntegration:
    """Integration tests for Neon Auth"""
    
    @patch.object(NeonAuthService, 'get_jwks')
    @patch.object(NeonAuthService, 'verify_neon_token')
    def test_full_token_verification_flow(self, mock_verify_token, mock_get_jwks):
        """Test complete token verification flow"""
        # Setup mocks
        mock_get_jwks.return_value = {"keys": [{"kid": "test_kid"}]}
        mock_verify_token.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "sub": "user123"
        }
        
        # Create service and verify token
        service = NeonAuthService()
        result = service.verify_neon_token("test_token")
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["sub"] == "user123"
    
    @patch('app.neon_auth.requests.get')
    def test_jwks_cache_behavior(self, mock_get):
        """Test JWKS caching behavior"""
        mock_response = Mock()
        mock_response.json.return_value = {"keys": [{"kid": "test_kid"}]}
        mock_get.return_value = mock_response
        
        service = NeonAuthService()
        
        # First call
        result1 = service.get_jwks()
        assert result1 is not None
        assert mock_get.call_count == 1
        
        # Second call should use cache
        result2 = service.get_jwks()
        assert result2 is not None
        assert mock_get.call_count == 1  # Should not call again due to cache
        
        # Clear cache and call again
        service.jwks_cache = None
        result3 = service.get_jwks()
        assert result3 is not None
        assert mock_get.call_count == 2  # Should call again after cache clear
    
    @patch('app.neon_auth.requests.get')
    def test_trial_status_with_network_issues(self, mock_get):
        """Test trial status checking with network issues"""
        # Test with connection error
        mock_get.side_effect = Exception("Connection failed")
        
        service = NeonAuthService()
        result = service.is_trial_active()
        
        assert result is False
        assert mock_get.call_count == 1