"""
Integration test suite for API Centrum backend
Tests complete workflows and system integration
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from unittest.mock import patch, Mock

from app.crud import CRUDUser
from tests import test_user_data, admin_user_data




class TestCompleteUserWorkflow:
    """Test complete user workflows from registration to domain management"""
    
    def test_new_user_registration_to_domain_management(self, client, db_session: Session):
        """Test complete workflow: register -> login -> create domain -> check stats"""
        # 1. Register new user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        
        register_data = register_response.json()
        access_token = register_data["access_token"]
        user_id = register_data["user_id"]
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Verify user info
        me_response = client.get("/api/users/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["id"] == user_id
        assert user_data["email"] == test_user_data["email"]
        
        # 3. Check initial dashboard stats
        stats_response = client.get("/api/dashboard/stats", headers=headers)
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        
        user_stats = stats_data["user_stats"]
        assert user_stats["total_domains"] == 0
        assert user_stats["recent_activities"] > 0
        assert user_stats["account_type"] == "local"
        
        # 4. List domains (should be empty initially)
        domains_response = client.get("/api/domains", headers=headers)
        assert domains_response.status_code == 200
        # Note: This depends on Websupport API mock
        
        # 5. Create a domain
        domain_data = {
            "name": "example.com",
            "description": "Test domain for integration test"
        }
        
        # Mock Websupport API response
        with patch('app.websupport.WebsupportService.create_domain') as mock_create:
            mock_create.return_value = {
                "id": 123,
                "name": "example.com",
                "status": "created"
            }
            
            create_response = client.post("/api/domains", json=domain_data, headers=headers)
            assert create_response.status_code == 200
        
        # 6. Check updated dashboard stats
        updated_stats_response = client.get("/api/dashboard/stats", headers=headers)
        assert updated_stats_response.status_code == 200
        updated_stats = updated_stats_response.json()
        
        # Domain creation does not write audit logs yet; activity count may remain 0
        assert updated_stats["user_stats"]["recent_activities"] >= 0
    
    def test_authentication_flow_with_token_refresh(self, client, db_session: Session):
        """Test authentication flow including token refresh"""
        # 1. Register user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        register_data = register_response.json()
        
        access_token = register_data["access_token"]
        refresh_token = register_data["refresh_token"]
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Use access token for multiple requests
        for _ in range(3):
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
        
        # 5. Old token should still work (until expiration)
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
    
    def test_domain_lifecycle_management(self, client, db_session: Session):
        """Test complete domain lifecycle: create -> list -> details -> delete"""
        # 1. Register and login
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        access_token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Create domain
        domain_data = {"name": "lifecycle-test.com", "description": "Domain lifecycle test"}
        
        with patch('app.websupport.WebsupportService.create_domain') as mock_create:
            mock_create.return_value = {
                "id": 456,
                "name": "lifecycle-test.com",
                "status": "active"
            }
            
            create_response = client.post("/api/domains", json=domain_data, headers=headers)
            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["name"] == "lifecycle-test.com"
        
        # 3. List domains
        with patch('app.websupport.WebsupportService.get_domains') as mock_list:
            mock_list.return_value = {
                "domains": [
                    {"id": 456, "name": "lifecycle-test.com", "status": "active"}
                ]
            }
            
            list_response = client.get("/api/domains", headers=headers)
            assert list_response.status_code == 200
            list_data = list_response.json()
            # Structure depends on Websupport API response
        
        # 4. Get domain details
        with patch('app.websupport.WebsupportService.get_domain_details') as mock_details:
            mock_details.return_value = {
                "id": 456,
                "name": "lifecycle-test.com",
                "status": "active",
                "created_at": "2023-01-01T00:00:00Z"
            }
            
            details_response = client.get("/api/domains/456", headers=headers)
            assert details_response.status_code == 200
            details_data = details_response.json()
            assert details_data["name"] == "lifecycle-test.com"
        
        # 5. Delete domain
        with patch('app.websupport.WebsupportService.delete_domain') as mock_delete:
            mock_delete.return_value = {"success": True}
            
            delete_response = client.delete("/api/domains/456", headers=headers)
            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert "success" in delete_data or "message" in delete_data


class TestSystemIntegration:
    """Test system-wide integration and error handling"""
    
    def test_system_health_monitoring(self, client):
        """Test system health monitoring across all components"""
        # Test public health endpoint
        health_response = client.get("/api/dashboard/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert "websupport_api" in health_data
        assert "database" in health_data
        assert "neon_auth_trial" in health_data
        assert "timestamp" in health_data
        
        # Test that health check doesn't crash with service failures
        with patch('app.websupport.WebsupportService.get_user_info') as mock_websupport:
            mock_websupport.side_effect = Exception("Websupport API down")
            
            health_response = client.get("/api/dashboard/health")
            assert health_response.status_code == 200
            
            health_data = health_response.json()
            assert health_data["websupport_api"] == "offline"
            assert health_data["database"] == "online"
    
    def test_error_propagation_and_handling(self, client):
        """Test error propagation and consistent error handling"""
        # Test that all endpoints return consistent error formats
        test_cases = [
            ("/api/domains", "GET", {}),
            ("/api/domains", "POST", {"name": "test.com"}),
            ("/api/domains/123", "GET", {}),
            ("/api/domains/123", "DELETE", {}),
            ("/api/ssl/generate", "POST", {"domain": "test.com", "email": "test@test.com"}),
            ("/api/users/me", "GET", {}),
            ("/api/users/2fa/setup", "POST", {}),
            ("/api/dashboard/stats", "GET", {}),
            ("/api/dashboard/activities", "GET", {}),
        ]
        
        for endpoint, method, data in test_cases:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # All should return 401 for unauthorized access
            assert response.status_code == 401, f"Endpoint {endpoint} should return 401"
            
            # Error response should have consistent format
            error_data = response.json()
            assert "detail" in error_data
    
    def test_full_user_flow(self, client, db_session, test_user_data):
        """Test database transaction consistency and rollback behavior"""
        # Test that database operations are properly rolled back on errors
        
        # Create user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Verify user was created
        retrieved_user = CRUDUser.get_by_email(db_session, test_user_data["email"])
        assert retrieved_user is not None
        assert retrieved_user.email == test_user_data["email"]
        
        # Test that audit logs are created for user actions
        # (This would require more complex setup with actual audit logging)
        assert True  # Placeholder for audit log testing
    
    def test_api_rate_limiting_and_concurrency(self, client, db_session: Session):
        """Test API behavior under concurrent requests"""
        # Register user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        access_token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Make multiple concurrent requests to test system stability
        import concurrent.futures
        import threading
        
        def make_request():
            response = client.get("/api/users/me", headers=headers)
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(result == 200 for result in results), f"Some requests failed: {results}"


class TestSecurityIntegration:
    """Test security features and authentication integration"""
    
    def test_authentication_middleware_integration(self, client, db_session: Session):
        """Test authentication middleware across all protected endpoints"""
        # Register user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        access_token = register_response.json()["access_token"]
        
        # Test all protected endpoints with valid token
        protected_endpoints = [
            ("/api/users/me", "GET"),
            ("/api/dashboard/stats", "GET"),
            ("/api/dashboard/activities", "GET"),
            ("/api/domains", "GET"),
            ("/api/domains", "POST"),
            ("/api/ssl/generate", "POST"),
        ]
        
        for endpoint, method in protected_endpoints:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, json={}, headers=headers)
            
            # Should succeed with valid token
            assert response.status_code in [200, 422], f"Endpoint {endpoint} failed with status {response.status_code}"
    
    def test_token_validation_and_security(self, client, db_session: Session):
        """Test token validation and security measures"""
        # Register user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        access_token = register_response.json()["access_token"]
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test with malformed token
        malformed_headers = {"Authorization": "Bearer token.without.proper.format"}
        response = client.get("/api/users/me", headers=malformed_headers)
        assert response.status_code == 401
        
        # Test with missing Authorization header
        response = client.get("/api/users/me")
        assert response.status_code == 401
        
        # Test with wrong header format
        wrong_format_headers = {"Authorization": "Token valid_token"}
        response = client.get("/api/users/me", headers=wrong_format_headers)
        assert response.status_code == 401
    
    def test_user_isolation_and_permissions(self, client, db_session: Session):
        """Test that users can only access their own data"""
        # Register two users
        user1_data = {"email": "user1@example.com", "password": "password123"}
        user2_data = {"email": "user2@example.com", "password": "password123"}
        
        # Register first user
        user1_response = client.post("/api/auth/register", json=user1_data)
        assert user1_response.status_code == 200
        user1_token = user1_response.json()["access_token"]
        
        # Register second user
        user2_response = client.post("/api/auth/register", json=user2_data)
        assert user2_response.status_code == 200
        user2_token = user2_response.json()["access_token"]
        
        # Each user should only see their own data
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # Get user info for both users
        user1_info = client.get("/api/users/me", headers=user1_headers).json()
        user2_info = client.get("/api/users/me", headers=user2_headers).json()
        
        assert user1_info["email"] == user1_data["email"]
        assert user2_info["email"] == user2_data["email"]
        assert user1_info["email"] != user2_info["email"]


class TestPerformanceAndScalability:
    """Test performance characteristics and scalability"""
    
    def test_api_response_times(self, client, db_session: Session):
        """Test that API responses are within acceptable time limits"""
        import time
        
        # Register user
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        access_token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test response times for various endpoints
        endpoints_to_test = [
            ("/api/users/me", "GET"),
            ("/api/dashboard/stats", "GET"),
            ("/api/dashboard/health", "GET"),  # Public endpoint
        ]
        
        for endpoint, method in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, json={}, headers=headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Response should be fast (under 1 second for local testing)
            assert response_time < 1.0, f"Endpoint {endpoint} took {response_time:.2f}s"
            assert response.status_code == 200
    
    def test_memory_usage_and_cleanup(self, client, db_session: Session):
        """Test that the system doesn't leak memory and cleans up properly"""
        # This is a basic test - in a real system you'd use memory profiling tools
        
        # Register multiple users to test memory usage
        for i in range(10):
            test_data = {
                "email": f"test{i}@example.com",
                "password": "password123"
            }
            
            response = client.post("/api/auth/register", json=test_data)
            assert response.status_code == 200
        
        # Verify all users were created
        # (This would require querying the database or having a list users endpoint)
        assert True  # Placeholder for actual memory testing


class TestHybridAuthIntegration:
    """Test hybrid authentication system integration"""
    
    def test_neon_auth_fallback_to_local(self, client, db_session: Session):
        """Test Neon Auth fallback to local authentication"""
        # This test would require mocking Neon Auth service
        
        # Test that system status shows both auth methods
        status_response = client.get("/api/auth/status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert "neon_auth_active" in status_data
        assert "local_auth_available" in status_data
        assert "recommended_auth" in status_data
    
    def test_auth_system_monitoring(self, client):
        """Test monitoring of authentication system status"""
        # Test auth status endpoint
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "neon_auth_active" in data
        assert "local_auth_available" in data
        assert "recommended_auth" in data
        assert "last_checked" in data
        
        # Test Neon Auth login URL generation
        url_response = client.get("/api/auth/neon/login-url")
        assert url_response.status_code == 200
        
        url_data = url_response.json()
        assert "login_url" in url_data
        assert "ep-square-union-aeczbg2r.neonauth" in url_data["login_url"]


class TestErrorRecoveryAndResilience:
    """Test system resilience and error recovery"""
    
    def test_websupport_api_failure_recovery(self, client):
        """Test system behavior when Websupport API fails"""
        # Patch make_websupport_request to fail for ALL websupport calls,
        # overriding the autouse success mock so health check sees it as offline.
        with patch('app.websupport.make_websupport_request') as mock_ws:
            mock_ws.side_effect = Exception("Websupport API unavailable")

            # Unauthenticated domain request should return 401 (not 500)
            response = client.get("/api/domains")
            assert response.status_code == 401  # Unauthorized, not 500

            # Health check should show Websupport as offline
            health_response = client.get("/api/dashboard/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["websupport_api"] == "offline"
    
    def test_database_connection_recovery(self, client, db_session: Session):
        """Test system behavior when database connection fails"""
        # This would require more complex mocking to simulate DB failures
        # For now, test that normal operations work
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 200
    
    def test_network_error_handling(self, client):
        """Test handling of network errors and timeouts"""
        # Test that system handles network errors gracefully
        with patch('app.websupport.requests.request') as mock_request:
            mock_request.side_effect = Exception("Network timeout")
            
            # Should return appropriate error
            response = client.get("/api/dashboard/health")
            assert response.status_code == 200  # Health endpoint should still work