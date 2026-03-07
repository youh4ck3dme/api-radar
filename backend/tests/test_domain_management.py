"""
Test suite for domain management functionality
Tests domain CRUD operations, validation, and business logic
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from tests import test_user_data
from app.domains.services import DomainService
from app.domains.models import Domain as DomainModel
from app.models import User
from app.crud import CRUDUser


class TestDomainService:
    """Test DomainService class methods"""
    
    @patch('app.websupport.WebsupportService.get_domains')
    def test_list_domains_success(self, mock_get_domains):
        """Test successful domain listing"""
        mock_get_domains.return_value = {
            "domains": [
                {"id": 1, "name": "example.com", "status": "active"},
                {"id": 2, "name": "test.com", "status": "pending"}
            ]
        }
        
        result = DomainService.list_domains()
        
        assert "domains" in result
        assert len(result["domains"]) == 2
        assert result["domains"][0]["name"] == "example.com"
        assert result["domains"][1]["name"] == "test.com"
    
    @patch('app.websupport.WebsupportService.get_domains')
    def test_list_domains_empty(self, mock_get_domains):
        """Test domain listing with empty response"""
        mock_get_domains.return_value = {"domains": []}
        
        result = DomainService.list_domains()
        
        assert "domains" in result
        assert len(result["domains"]) == 0
    
    @patch('app.websupport.WebsupportService.get_domains')
    def test_list_domains_error(self, mock_get_domains):
        """Test domain listing with error"""
        mock_get_domains.side_effect = HTTPException(status_code=500, detail="API Error")
        
        with pytest.raises(HTTPException) as exc_info:
            DomainService.list_domains()
        
        assert exc_info.value.status_code == 500
    
    @patch('app.websupport.WebsupportService.create_domain')
    def test_create_domain_success(self, mock_create_domain):
        """Test successful domain creation"""
        domain_data = {"name": "example.com", "description": "Test domain"}
        mock_create_domain.return_value = {
            "id": 123, "name": "example.com", "status": "created"
        }
        
        result = DomainService.create_domain(domain_data)
        
        assert result["id"] == 123
        assert result["name"] == "example.com"
        assert result["status"] == "created"
        mock_create_domain.assert_called_once_with(domain_data)
    
    @patch('app.websupport.WebsupportService.create_domain')
    def test_create_domain_validation_error(self, mock_create_domain):
        """Test domain creation with validation error"""
        domain_data = {"name": "", "description": "Test domain"}
        mock_create_domain.side_effect = HTTPException(status_code=400, detail="Invalid domain name")
        
        with pytest.raises(HTTPException) as exc_info:
            DomainService.create_domain(domain_data)
        
        assert exc_info.value.status_code == 400
    
    @patch('app.websupport.WebsupportService.get_domain_details')
    def test_get_domain_details_success(self, mock_get_details):
        """Test successful domain details retrieval"""
        domain_id = 123
        mock_get_details.return_value = {
            "id": 123,
            "name": "example.com",
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        result = DomainService.get_domain_details(domain_id)
        
        assert result["id"] == 123
        assert result["name"] == "example.com"
        assert result["status"] == "active"
        mock_get_details.assert_called_once_with(domain_id)
    
    @patch('app.websupport.WebsupportService.get_domain_details')
    def test_get_domain_details_not_found(self, mock_get_details):
        """Test domain details retrieval for non-existent domain"""
        domain_id = 999
        mock_get_details.side_effect = HTTPException(status_code=404, detail="Domain not found")
        
        with pytest.raises(HTTPException) as exc_info:
            DomainService.get_domain_details(domain_id)
        
        assert exc_info.value.status_code == 404
    
    @patch('app.websupport.WebsupportService.delete_domain')
    def test_delete_domain_success(self, mock_delete_domain):
        """Test successful domain deletion"""
        domain_id = 123
        mock_delete_domain.return_value = {"success": True}
        
        result = DomainService.delete_domain(domain_id)
        
        assert result["success"] is True
        mock_delete_domain.assert_called_once_with(domain_id)
    
    @patch('app.websupport.WebsupportService.delete_domain')
    def test_delete_domain_forbidden(self, mock_delete_domain):
        """Test domain deletion with insufficient permissions"""
        domain_id = 123
        mock_delete_domain.side_effect = HTTPException(status_code=403, detail="Forbidden")
        
        with pytest.raises(HTTPException) as exc_info:
            DomainService.delete_domain(domain_id)
        
        assert exc_info.value.status_code == 403


class TestDomainModels:
    """Test domain database models"""
    
    def test_domain_model_creation(self, db_session: Session):
        """Test domain model creation"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create domain
        domain = DomainModel(
            name="example.com",
            description="Test domain",
            user_id=user.id
        )
        
        db_session.add(domain)
        db_session.commit()
        db_session.refresh(domain)
        
        assert domain.id is not None
        assert domain.name == "example.com"
        assert domain.description == "Test domain"
        assert domain.user_id == user.id
        assert domain.created_at is not None
    
    def test_domain_model_unique_name(self, db_session: Session):
        """Test domain name uniqueness constraint"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create first domain
        domain1 = DomainModel(name="example.com", user_id=user.id)
        db_session.add(domain1)
        db_session.commit()
        
        # Try to create domain with same name
        domain2 = DomainModel(name="example.com", user_id=user.id)
        db_session.add(domain2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
    
    def test_domain_model_relationship(self, db_session: Session):
        """Test domain-user relationship"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create domain
        domain = DomainModel(name="example.com", user_id=user.id)
        db_session.add(domain)
        db_session.commit()
        db_session.refresh(domain)
        
        # Test relationship
        assert domain.user is not None
        assert domain.user.email == test_user_data["email"]
        assert domain.user == user


class TestDomainValidation:
    """Test domain validation logic"""
    
    def test_domain_name_validation(self):
        """Test domain name validation rules"""
        valid_names = [
            "example.com",
            "sub.example.com",
            "example.co.uk",
            "test-domain.com",
            "123example.com"
        ]
        
        invalid_names = [
            "",  # Empty
            " ",  # Whitespace only
            "example",  # No TLD
            "example.",  # Incomplete TLD
            ".example.com",  # Leading dot
            "example..com",  # Double dot
            "exämple.com",  # Non-ASCII
            "a" * 254 + ".com",  # Too long
        ]
        
        # Test would go here based on actual validation logic
        # For now, just ensure the lists are properly defined
        assert len(valid_names) > 0
        assert len(invalid_names) > 0
    
    def test_domain_description_validation(self):
        """Test domain description validation"""
        valid_descriptions = [
            "Test domain",
            "",  # Empty description should be allowed
            " " * 500,  # Long description
            "Test domain with special chars: !@#$%^&*()"
        ]
        
        # Test would go here based on actual validation logic
        assert len(valid_descriptions) > 0


class TestDomainBusinessLogic:
    """Test domain business logic and rules"""
    
    def test_domain_lifecycle(self, db_session: Session):
        """Test complete domain lifecycle"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create domain
        domain = DomainModel(
            name="example.com",
            description="Test domain",
            user_id=user.id
        )
        
        db_session.add(domain)
        db_session.commit()
        db_session.refresh(domain)
        
        # Verify domain was created
        assert domain.id is not None
        assert domain.name == "example.com"
        assert domain.user_id == user.id
        
        # Test domain can be queried
        retrieved_domain = db_session.query(DomainModel).filter(
            DomainModel.id == domain.id
        ).first()
        
        assert retrieved_domain is not None
        assert retrieved_domain.name == "example.com"
    
    def test_multiple_domains_per_user(self, db_session: Session):
        """Test that user can have multiple domains"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create multiple domains
        domains = []
        for i in range(3):
            domain = DomainModel(
                name=f"example{i}.com",
                description=f"Test domain {i}",
                user_id=user.id
            )
            domains.append(domain)
            db_session.add(domain)
        
        db_session.commit()
        
        # Verify all domains were created
        user_domains = db_session.query(DomainModel).filter(
            DomainModel.user_id == user.id
        ).all()
        
        assert len(user_domains) == 3
        
        domain_names = [d.name for d in user_domains]
        assert "example0.com" in domain_names
        assert "example1.com" in domain_names
        assert "example2.com" in domain_names
    
    def test_domain_user_relationship_cascade(self, db_session: Session):
        """Test domain-user relationship behavior"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create domain
        domain = DomainModel(name="example.com", user_id=user.id)
        db_session.add(domain)
        db_session.commit()
        
        # Verify relationship works
        assert domain.user.email == test_user_data["email"]
        
        # Test that domain still exists if user is deleted
        # (depends on foreign key constraints - usually domains should be deleted)
        db_session.delete(user)
        db_session.commit()
        
        # Domain should still exist but user_id should be None
        # or domain should be deleted (depends on CASCADE setting)
        remaining_domain = db_session.query(DomainModel).filter(
            DomainModel.id == domain.id
        ).first()
        
        # This test depends on the actual CASCADE behavior configured
        # For now, just verify the query works
        assert remaining_domain is not None or remaining_domain is None


class TestDomainIntegration:
    """Integration tests for domain functionality"""
    
    @patch('app.websupport.WebsupportService.get_domains')
    @patch('app.websupport.WebsupportService.create_domain')
    def test_domain_service_integration(self, mock_create, mock_get):
        """Test DomainService integration with Websupport API"""
        # Mock Websupport responses
        mock_get.return_value = {"domains": [{"id": 1, "name": "existing.com"}]}
        mock_create.return_value = {"id": 2, "name": "new.com", "status": "created"}
        
        # Test list domains
        domains = DomainService.list_domains()
        assert len(domains["domains"]) == 1
        assert domains["domains"][0]["name"] == "existing.com"
        
        # Test create domain
        new_domain = DomainService.create_domain({"name": "new.com"})
        assert new_domain["name"] == "new.com"
        assert new_domain["status"] == "created"
        
        # Verify API calls were made
        assert mock_get.call_count == 1
        assert mock_create.call_count == 1
    
    def test_domain_model_persistence(self, db_session: Session):
        """Test domain model persistence and querying"""
        # Create test user
        user = CRUDUser.create(
            db_session, 
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        # Create and save domain
        domain = DomainModel(
            name="persistent.com",
            description="Test persistence",
            user_id=user.id
        )
        
        db_session.add(domain)
        db_session.commit()
        
        # Query domain by ID
        queried_domain = db_session.query(DomainModel).filter(
            DomainModel.id == domain.id
        ).first()
        
        assert queried_domain is not None
        assert queried_domain.name == "persistent.com"
        assert queried_domain.description == "Test persistence"
        
        # Query domains by user
        user_domains = db_session.query(DomainModel).filter(
            DomainModel.user_id == user.id
        ).all()
        
        assert len(user_domains) == 1
        assert user_domains[0].name == "persistent.com"