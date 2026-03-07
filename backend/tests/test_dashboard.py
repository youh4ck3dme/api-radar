"""
Test suite for dashboard functionality
Tests dashboard statistics, health checks, and monitoring
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from unittest.mock import Mock, MagicMock, patch

from tests import test_user_data
from app.dashboard import DashboardStats, DashboardStats
from app.models import User, AuditLog
from app.crud import CRUDUser
from app.websupport import WebsupportService


class TestDashboardStats:
    """Test DashboardStats class methods"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.db_session = None  # Will be set in each test
    
    def test_get_user_stats_success(self, db_session: Session):
        """Test successful user statistics retrieval"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create some audit logs
        audit_log1 = AuditLog(
            user_id=user.id,
            action="domain_created",
            detail="Created domain example.com"
        )
        audit_log2 = AuditLog(
            user_id=user.id,
            action="ssl_generated",
            detail="Generated SSL for example.com"
        )
        
        db_session.add(audit_log1)
        db_session.add(audit_log2)
        db_session.commit()
        
        # Create DashboardStats instance
        stats = DashboardStats(db_session)
        result = stats.get_user_stats(user.id)
        
        assert "total_domains" in result
        assert "recent_activities" in result
        assert "last_login" in result
        assert "account_type" in result
        
        assert result["total_domains"] == 0  # No domains tracked locally
        assert result["recent_activities"] == 2
        assert result["account_type"] == "local"
    
    def test_get_user_stats_no_user(self, db_session: Session):
        """Test user statistics for non-existent user"""
        stats = DashboardStats(db_session)
        result = stats.get_user_stats(999)  # Non-existent user ID
        
        assert "total_domains" in result
        assert "recent_activities" in result
        assert "last_login" in result
        assert "account_type" in result
        
        assert result["total_domains"] == 0
        assert result["recent_activities"] == 0
        assert result["last_login"] is None
        assert result["account_type"] == "local"
    
    def test_get_user_stats_neon_auth_user(self, db_session: Session):
        """Test user statistics for Neon Auth user"""
        # Create test user with Neon Auth password
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            "neon_auth_temp"
        )
        
        stats = DashboardStats(db_session)
        result = stats.get_user_stats(user.id)
        
        assert result["account_type"] == "neon_auth"
    
    @patch('app.websupport.WebsupportService.get_user_info')
    def test_get_system_health_all_online(self, mock_get_user_info, db_session: Session):
        """Test system health when all services are online"""
        mock_get_user_info.return_value = {"id": 1, "email": "test@example.com"}
        
        stats = DashboardStats(db_session)
        result = stats.get_system_health()
        
        assert "websupport_api" in result
        assert "database" in result
        assert "neon_auth_trial" in result
        assert "timestamp" in result
        
        assert result["websupport_api"] == "online"
        assert result["database"] == "online"
        assert result["neon_auth_trial"] in ["active", "inactive"]  # Depends on actual status
        assert isinstance(result["timestamp"], str)
    
    @patch('app.websupport.WebsupportService.get_user_info')
    def test_get_system_health_websupport_offline(self, mock_get_user_info, db_session: Session):
        """Test system health when Websupport API is offline"""
        mock_get_user_info.side_effect = Exception("Connection failed")
        
        stats = DashboardStats(db_session)
        result = stats.get_system_health()
        
        assert result["websupport_api"] == "offline"
        assert result["database"] == "online"
    
    def test_get_system_health_database_offline(self, db_session: Session):
        """Test system health when database is offline"""
        # This would require more complex mocking to simulate DB failure
        # For now, test that the method doesn't crash
        stats = DashboardStats(db_session)
        
        # Mock the database check to fail
        original_execute = db_session.execute
        db_session.execute = Mock(side_effect=Exception("DB Error"))
        
        try:
            result = stats.get_system_health()
            assert result["database"] == "offline"
        finally:
            db_session.execute = original_execute
    
    @patch('app.neon_auth.is_neon_trial_active')
    def test_get_system_health_neon_auth_status(self, mock_is_active, db_session: Session):
        """Test system health with different Neon Auth statuses"""
        mock_is_active.return_value = True
        
        stats = DashboardStats(db_session)
        result = stats.get_system_health()
        
        assert result["neon_auth_trial"] == "active"
        
        # Test inactive status
        mock_is_active.return_value = False
        result = stats.get_system_health()
        assert result["neon_auth_trial"] == "inactive"
    
    def test_get_recent_activities_success(self, db_session: Session):
        """Test successful recent activities retrieval"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create audit logs
        now = datetime.utcnow()
        audit_logs = [
            AuditLog(user_id=user.id, action="login", detail="User logged in", created_at=now - timedelta(hours=1)),
            AuditLog(user_id=user.id, action="domain_created", detail="Created example.com", created_at=now - timedelta(hours=2)),
            AuditLog(user_id=user.id, action="ssl_generated", detail="Generated SSL", created_at=now - timedelta(hours=3)),
        ]
        
        for log in audit_logs:
            db_session.add(log)
        db_session.commit()
        
        stats = DashboardStats(db_session)
        result = stats.get_recent_activities(user.id, limit=2)
        
        assert len(result) == 2
        assert result[0]["action"] == "login"
        assert result[1]["action"] == "domain_created"
        assert "timestamp" in result[0]
        assert "timestamp" in result[1]
    
    def test_get_recent_activities_empty(self, db_session: Session):
        """Test recent activities retrieval with no activities"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        stats = DashboardStats(db_session)
        result = stats.get_recent_activities(user.id, limit=5)
        
        assert len(result) == 0
    
    def test_get_recent_activities_limit(self, db_session: Session):
        """Test recent activities retrieval with limit"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create more than limit audit logs
        for i in range(10):
            audit_log = AuditLog(
                user_id=user.id,
                action=f"action_{i}",
                detail=f"Action detail {i}"
            )
            db_session.add(audit_log)
        db_session.commit()
        
        stats = DashboardStats(db_session)
        result = stats.get_recent_activities(user.id, limit=3)
        
        assert len(result) == 3
        # Should be ordered by created_at desc (most recent first)
        assert result[0]["action"] == "action_9"
        assert result[1]["action"] == "action_8"
        assert result[2]["action"] == "action_7"


class TestDashboardEndpoints:
    """Test dashboard API endpoints"""
    
    def test_dashboard_stats_endpoint(self, client, db_session: Session):
        """Test dashboard stats endpoint"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create auth token
        from app.auth_local import create_local_access_token
        access_token = create_local_access_token(user.email)
        
        # Make request
        response = client.get(
            "/api/dashboard/stats",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_stats" in data
        assert "system_health" in data
        assert "timestamp" in data
        
        user_stats = data["user_stats"]
        assert "total_domains" in user_stats
        assert "recent_activities" in user_stats
        assert "account_type" in user_stats
    
    def test_dashboard_activities_endpoint(self, client, db_session: Session):
        """Test dashboard activities endpoint"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create auth token
        from app.auth_local import create_local_access_token
        access_token = create_local_access_token(user.email)
        
        # Make request
        response = client.get(
            "/api/dashboard/activities",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activities" in data
        assert "count" in data
        assert isinstance(data["activities"], list)
        assert isinstance(data["count"], int)
    
    def test_dashboard_health_endpoint(self, client, db_session: Session):
        """Test dashboard health endpoint"""
        response = client.get("/api/dashboard/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "websupport_api" in data
        assert "database" in data
        assert "neon_auth_trial" in data
        assert "timestamp" in data
    
    def test_dashboard_endpoints_unauthorized(self, client):
        """Test dashboard endpoints without authentication"""
        # Test stats endpoint
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 401
        
        # Test activities endpoint
        response = client.get("/api/dashboard/activities")
        assert response.status_code == 401
    
    def test_dashboard_endpoints_invalid_token(self, client):
        """Test dashboard endpoints with invalid token"""
        # Test with invalid token
        response = client.get(
            "/api/dashboard/stats",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestDashboardIntegration:
    """Integration tests for dashboard functionality"""
    
    @patch('app.websupport.WebsupportService.get_user_info')
    @patch('app.neon_auth.is_neon_trial_active')
    def test_full_dashboard_workflow(self, mock_is_active, mock_get_user_info, client, db_session: Session):
        """Test complete dashboard workflow"""
        # Setup mocks
        mock_get_user_info.return_value = {"id": 1, "email": "test@example.com"}
        mock_is_active.return_value = True
        
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create audit logs
        audit_logs = [
            AuditLog(user_id=user.id, action="login", detail="User logged in"),
            AuditLog(user_id=user.id, action="domain_created", detail="Created example.com"),
        ]
        
        for log in audit_logs:
            db_session.add(log)
        db_session.commit()
        
        # Create auth token
        from app.auth_local import create_local_access_token
        access_token = create_local_access_token(user.email)
        
        # Test all dashboard endpoints
        endpoints = [
            ("/api/dashboard/stats", "user_stats"),
            ("/api/dashboard/activities", "activities"),
            ("/api/dashboard/health", "websupport_api")
        ]
        
        for endpoint, expected_key in endpoints:
            response = client.get(
                endpoint,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert expected_key in data
    
    def test_dashboard_with_neon_auth_user(self, client, db_session: Session):
        """Test dashboard with Neon Auth user"""
        # Create Neon Auth user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            "neon_auth_temp"
        )
        
        # Create auth token
        from app.auth_local import create_local_access_token
        access_token = create_local_access_token(user.email)
        
        # Test dashboard stats
        response = client.get(
            "/api/dashboard/stats",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_stats"]["account_type"] == "neon_auth"
    
    @patch('app.websupport.WebsupportService.get_user_info')
    def test_dashboard_health_with_service_failures(self, mock_get_user_info, client, db_session: Session):
        """Test dashboard health with simulated service failures"""
        # Simulate Websupport API failure
        mock_get_user_info.side_effect = Exception("Websupport API down")
        
        response = client.get("/api/dashboard/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["websupport_api"] == "offline"
        assert data["database"] == "online"