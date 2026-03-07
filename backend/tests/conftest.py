"""
Pytest configuration and fixtures for API Centrum Backend tests
"""

import pytest
import os
from unittest.mock import patch
from typing import Generator
from fastapi.testclient import TestClient

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import app and models
from app.config import settings

# Force testing environment
settings.ENV = "testing"
settings.JWT_SECRET = "test_jwt_secret_key_for_testing"
settings.WEBSUPPORT_API_KEY = "test_key"
settings.WEBSUPPORT_SECRET = "test_secret"
settings.ALLOWED_HOSTS = "testserver,localhost,127.0.0.1"

from app.main import app
from app.db import get_db, Base
from app.models import User, Role, AuditLog
from app.crud import CRUDUser
from app.auth import AuthService
from app.instrumentation import limiter

# Disable slowapi rate limiting during tests to prevent 429s
limiter.enabled = False


# ---------------------------------------------------------------------------
# Autouse mock: block all real Websupport network calls during tests
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_websupport_requests(request):
    """Prevent tests from making real HTTP requests to Websupport API.
    Skipped for test_websupport.py which has its own request-level mocking.
    """
    if "test_websupport" in request.module.__name__:
        yield None
        return
    with patch("app.websupport.make_websupport_request") as mock:
        mock.return_value = {"items": [], "status": "ok"}
        yield mock

# ---------------------------------------------------------------------------
# Test database engine
# ---------------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Ensure we start with a fresh database file
if os.path.exists("./test.db"):
    try:
        os.remove("./test.db")
    except Exception:
        pass

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the DB dependency so the app uses the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------------
# Session-scoped table lifecycle
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all tables once at the start of the test session."""
    # Ensure all models are imported so they are registered on Base
    from app.domains.models import Domain
    Base.metadata.create_all(bind=engine)
    yield
    # Base.metadata.drop_all(bind=engine) # Keep for session to avoid "no such table" in parallel? 
    # Actually, keep it but maybe it's cleaner to drop at the very end.
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Function-scoped data cleanup (runs after every test)
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clean_db_state(create_test_tables):
    """Truncate all table data after each test to ensure isolation."""
    yield
    session = TestingSessionLocal()
    try:
        # Delete in reverse dependency order to avoid FK violations
        session.execute(text("DELETE FROM audit_logs"))
        session.execute(text("DELETE FROM domains"))
        session.execute(text("DELETE FROM users"))
        session.execute(text("DELETE FROM roles"))
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session() -> Generator:
    """Provide a clean database session for direct DB manipulation in tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def test_user_data():
    return {"email": "test@example.com", "password": "testpassword123"}


@pytest.fixture
def admin_user_data():
    return {"email": "admin@example.com", "password": "adminpassword123"}


@pytest.fixture
def authenticated_client(client, db_session, test_user_data):
    """Test client pre-authenticated as test_user."""
    user = CRUDUser.create(db_session, test_user_data["email"], test_user_data["password"])
    auth_result = AuthService.authenticate_user(
        test_user_data["email"], test_user_data["password"], db_session
    )
    client.headers.update({"Authorization": f"Bearer {auth_result['access_token']}"})
    yield client
    client.headers.pop("Authorization", None)


@pytest.fixture
def multiple_test_users(db_session):
    """Create three test users."""
    users = []
    for i in range(3):
        user = CRUDUser.create(db_session, f"user{i}@example.com", "password123")
        users.append(user)
    return users


@pytest.fixture
def test_domains_data():
    return [
        {"name": "example.com", "description": "Test domain 1"},
        {"name": "test.com", "description": "Test domain 2"},
        {"name": "demo.com", "description": "Test domain 3"},
    ]


@pytest.fixture
def test_ssl_data():
    return {"domain": "example.com", "email": "admin@example.com"}


@pytest.fixture
def audit_logs_data(db_session, multiple_test_users):
    logs = []
    for user in multiple_test_users:
        for i in range(3):
            log = AuditLog(user_id=user.id, action=f"action_{i}", detail=f"Test action {i}")
            logs.append(log)
            db_session.add(log)
    db_session.commit()
    return logs


# ---------------------------------------------------------------------------
# Service mock fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_websupport_service():
    with patch("app.websupport.WebsupportService") as mock:
        yield mock


@pytest.fixture
def mock_neon_auth_service():
    with patch("app.neon_auth.NeonAuthService") as mock:
        yield mock


@pytest.fixture
def mock_ssl_service():
    with patch("app.ssl.services.SSLService") as mock:
        yield mock


# ---------------------------------------------------------------------------
# Test data factory
# ---------------------------------------------------------------------------
class TestDataFactory:
    @staticmethod
    def create_user_data(index=0):
        return {"email": f"testuser{index}@example.com", "password": "testpassword123"}

    @staticmethod
    def create_domain_data(index=0):
        return {"name": f"testdomain{index}.com", "description": f"Test domain {index}"}

    @staticmethod
    def create_ssl_data(domain="example.com"):
        return {"domain": domain, "email": f"admin@{domain}"}


@pytest.fixture
def test_data_factory():
    return TestDataFactory


# ---------------------------------------------------------------------------
# Session-level test config
# ---------------------------------------------------------------------------
TEST_CONFIG = {
    "WEBSUPPORT_API_KEY": "test_key",
    "WEBSUPPORT_SECRET": "test_secret",
    "DATABASE_URL": SQLALCHEMY_DATABASE_URL,
    "JWT_SECRET": "test_jwt_secret_key_for_testing",
    "JWT_EXPIRE_MINUTES": 60,
    "ENV": "testing",
}


@pytest.fixture(scope="session")
def test_config():
    return TEST_CONFIG
