"""
API Centrum Backend Tests Package
Comprehensive test suite for all backend functionality
"""

# Module-level test data constants, importable by test modules
test_user_data = {
    "email": "test@example.com",
    "password": "testpassword123"
}

admin_user_data = {
    "email": "admin@example.com",
    "password": "adminpassword123"
}

# Shared test configuration dictionary used by several test modules
TEST_CONFIG = {
    "WEBSUPPORT_API_KEY": "test_key",
    "WEBSUPPORT_SECRET": "test_secret",
    "DATABASE_URL": "sqlite:///./test.db",
    "JWT_SECRET": "test_jwt_secret_key_for_testing",
    "JWT_EXPIRE_MINUTES": 60,
    "ENV": "testing",
}
