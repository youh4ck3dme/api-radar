"""
Test suite for API endpoints
Tests all public API endpoints including auth, domains, SSL, and dashboard
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.crud import CRUDUser




class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    def test_auth_login_success(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Test successful login"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Test login
        response = client.post("/api/auth/login", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == user.id
        assert data["email"] == test_user_data["email"]
    
    def test_auth_login_wrong_password(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Test login with wrong password"""
        # Create test user
        CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Test login with wrong password
        wrong_data = test_user_data.copy()
        wrong_data["password"] = "wrongpassword"
        
        response = client.post("/api/auth/login", json=wrong_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_auth_login_nonexistent_user(self, client: TestClient, test_user_data: dict):
        """Test login with nonexistent user"""
        response = client.post("/api/auth/login", json=test_user_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_auth_register_success(self, client: TestClient, test_user_data: dict):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "user_id" in data
        assert "email" in data
        assert "access_token" in data
        assert data["email"] == test_user_data["email"]
        assert "registered successfully" in data["message"].lower()
    
    def test_auth_register_duplicate_email(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Test registration with duplicate email"""
        # Create existing user
        CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Try to register with same email
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_auth_refresh_success(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Test successful token refresh"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Get refresh token from login
        login_response = client.post("/api/auth/login", json=test_user_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Test refresh
        response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_auth_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token"""
        response = client.post("/api/auth/refresh", json={"refresh_token": "invalid_token"})
        
        assert response.status_code == 401
    
    def test_auth_status(self, client: TestClient):
        """Test auth system status endpoint"""
        response = client.get("/api/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "neon_auth_active" in data
        assert "local_auth_available" in data
        assert "recommended_auth" in data
        assert data["local_auth_available"] is True
    
    def test_auth_neon_login_url(self, client: TestClient):
        """Test Neon Auth login URL endpoint"""
        response = client.get("/api/auth/neon/login-url")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "login_url" in data
        assert "ep-square-union-aeczbg2r.neonauth" in data["login_url"]
        assert "client_id=api-centrum" in data["login_url"]


class TestDomainEndpoints:
    """Test domain API endpoints"""
    
    def test_domains_list_unauthorized(self, client: TestClient):
        """Test domains list without authentication"""
        response = client.get("/api/domains")
        
        assert response.status_code == 401
    
    def test_domains_list_success(self, client_with_auth: TestClient):
        """Test successful domains list"""
        response = client_with_auth.get("/api/domains")
        
        assert response.status_code == 200
        # Response structure depends on Websupport API mock
    
    def test_domains_create_unauthorized(self, client: TestClient):
        """Test domain creation without authentication"""
        response = client.post("/api/domains", json={"name": "example.com"})
        
        assert response.status_code == 401
    
    def test_domains_create_success(self, client_with_auth: TestClient):
        """Test successful domain creation"""
        domain_data = {"name": "example.com", "description": "Test domain"}
        response = client_with_auth.post("/api/domains", json=domain_data)
        
        assert response.status_code == 200
        # Response structure depends on Websupport API mock
    
    def test_domains_get_details_unauthorized(self, client: TestClient):
        """Test domain details without authentication"""
        response = client.get("/api/domains/123")
        
        assert response.status_code == 401
    
    def test_domains_delete_unauthorized(self, client: TestClient):
        """Test domain deletion without authentication"""
        response = client.delete("/api/domains/123")
        
        assert response.status_code == 401


class TestSSLEndpoints:
    """Test SSL API endpoints"""
    
    def test_ssl_generate_unauthorized(self, client: TestClient):
        """Test SSL generation without authentication"""
        response = client.post("/api/ssl/generate", json={
            "domain": "example.com",
            "email": "admin@example.com"
        })
        
        assert response.status_code == 401
    
    def test_ssl_generate_success(self, client_with_auth: TestClient):
        """Test successful SSL generation"""
        ssl_data = {
            "domain": "example.com",
            "email": "admin@example.com"
        }
        response = client_with_auth.post("/api/ssl/generate", json=ssl_data)
        
        assert response.status_code == 200
        # Response structure depends on SSL service implementation


class TestUserEndpoints:
    """Test user API endpoints"""
    
    def test_users_me_unauthorized(self, client: TestClient):
        """Test user info without authentication"""
        response = client.get("/api/users/me")
        
        assert response.status_code == 401
    
    def test_users_me_success(self, client_with_auth: TestClient):
        """Test successful user info retrieval"""
        response = client_with_auth.get("/api/users/me")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "email" in data
        assert "two_factor_enabled" in data
    
    def test_users_2fa_setup_unauthorized(self, client: TestClient):
        """Test 2FA setup without authentication"""
        response = client.post("/api/users/2fa/setup")
        
        assert response.status_code == 401
    
    def test_users_2fa_verify_unauthorized(self, client: TestClient):
        """Test 2FA verification without authentication"""
        response = client.post("/api/users/2fa/verify", json={
            "token": "123456",
            "secret": "test_secret"
        })
        
        assert response.status_code == 401


class TestDashboardEndpoints:
    """Test dashboard API endpoints"""
    
    def test_dashboard_stats_unauthorized(self, client: TestClient):
        """Test dashboard stats without authentication"""
        response = client.get("/api/dashboard/stats")
        
        assert response.status_code == 401
    
    def test_dashboard_stats_success(self, client_with_auth: TestClient):
        """Test successful dashboard stats"""
        response = client_with_auth.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_stats" in data
        assert "system_health" in data
        assert "timestamp" in data
    
    def test_dashboard_activities_unauthorized(self, client: TestClient):
        """Test dashboard activities without authentication"""
        response = client.get("/api/dashboard/activities")
        
        assert response.status_code == 401
    
    def test_dashboard_health(self, client: TestClient):
        """Test dashboard health endpoint (public)"""
        response = client.get("/api/dashboard/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "websupport_api" in data
        assert "database" in data
        assert "neon_auth_trial" in data
        assert "timestamp" in data


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "env" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "documentation" in data
        assert "neon_auth_trial" in data


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    def test_full_user_workflow(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Test complete user workflow through API"""
        # 1. Register user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        
        register_data = register_response.json()
        access_token = register_data["access_token"]
        
        # 2. Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/api/users/me", headers=headers)
        assert me_response.status_code == 200
        
        # 3. Get dashboard stats
        stats_response = client.get("/api/dashboard/stats", headers=headers)
        assert stats_response.status_code == 200
        
        # 4. List domains (should work even with empty response)
        domains_response = client.get("/api/domains", headers=headers)
        assert domains_response.status_code == 200
    
    def test_auth_flow_with_refresh(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Test authentication flow with token refresh"""
        # 0. Register user first so login can succeed
        client.post("/api/auth/register", json=test_user_data)

        # 1. Login
        login_response = client.post("/api/auth/login", json=test_user_data)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        
        # 2. Use access token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        
        # 3. Refresh token
        refresh_response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_response.status_code == 200
        
        refresh_data = refresh_response.json()
        new_access_token = refresh_data["access_token"]
        
        # 4. Use new access token
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        response = client.get("/api/users/me", headers=new_headers)
        assert response.status_code == 200
    
    def test_error_handling_consistency(self, client: TestClient):
        """Test consistent error handling across endpoints"""
        endpoints_to_test = [
            ("/api/domains", "GET"),
            ("/api/domains", "POST"),
            ("/api/domains/123", "GET"),
            ("/api/domains/123", "DELETE"),
            ("/api/ssl/generate", "POST"),
            ("/api/users/me", "GET"),
            ("/api/users/2fa/setup", "POST"),
            ("/api/dashboard/stats", "GET"),
            ("/api/dashboard/activities", "GET"),
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # All should return 401 for unauthorized access
            assert response.status_code == 401, f"Endpoint {endpoint} with method {method} should return 401"


# Helper fixture for authenticated client
@pytest.fixture
def client_with_auth(client: TestClient, db_session: Session, test_user_data: dict):
    """Create authenticated test client"""
    # Create test user
    user = CRUDUser.create(
        db_session, 
        test_user_data["email"], 
        test_user_data["password"]
    )
    
    # Get access token
    login_response = client.post("/api/auth/login", json=test_user_data)
    access_token = login_response.json()["access_token"]
    
    # Create authenticated client
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
    # Cleanup
    client.headers.pop("Authorization", None)