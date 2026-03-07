# API Centrum Backend - Test Suite

## Prehľad

Komplexný testovací framework pre API Centrum Backend systém s integráciou Neon Auth.

### Štruktúra Testov

```
backend/tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Pytest configuration and fixtures
├── test_requirements.txt   # Test dependencies
├── test_auth_local.py      # Local authentication tests
├── test_auth_neon.py       # Neon Auth integration tests
├── test_websupport.py      # Websupport API tests
├── test_domain_management.py # Domain management tests
├── test_ssl_management.py  # SSL certificate tests
├── test_dashboard.py       # Dashboard and monitoring tests
├── test_api_endpoints.py   # API endpoint tests
└── test_integration.py     # Integration and workflow tests
```

### Testovacie Kategórie

#### **1. Autentifikačné Testy**
- **Lokálna autentifikácia** (`test_auth_local.py`)
  - Password hashing a verification
  - JWT token creation a verification
  - Token refresh mechanism
  - User authentication flow
  - Error handling

- **Neon Auth integrácia** (`test_auth_neon.py`)
  - JWT verification from Neon Auth
  - User info extraction
  - Trial status checking
  - JWKS caching
  - Error handling

#### **2. API Integrácie**
- **Websupport API** (`test_websupport.py`)
  - API signature generation
  - Request/response handling
  - Error responses
  - Domain operations
  - Authentication

- **SSL Management** (`test_ssl_management.py`)
  - Certificate generation
  - Domain validation
  - Email validation
  - Certificate operations
  - File path management

#### **3. Business Logic**
- **Domain Management** (`test_domain_management.py`)
  - Domain CRUD operations
  - Database models
  - Validation rules
  - Business logic
  - User isolation

- **Dashboard** (`test_dashboard.py`)
  - Statistics calculation
  - Health checks
  - Activity tracking
  - System monitoring
  - API endpoints

#### **4. API Testy**
- **Endpoint Testy** (`test_api_endpoints.py`)
  - Authentication endpoints
  - Domain endpoints
  - SSL endpoints
  - User endpoints
  - Dashboard endpoints
  - Error handling

#### **5. Integrácia**
- **Komplexné Workflows** (`test_integration.py`)
  - Complete user workflows
  - System integration
  - Security testing
  - Performance testing
  - Error recovery
  - Hybrid auth testing

### Spustenie Testov

#### **Základné Spustenie**
```bash
# Spustenie všetkých testov
pytest

# Spustenie s coverage
pytest --cov=app --cov-report=html

# Spustenie konkrétnej testovej triedy
pytest tests/test_auth_local.py::TestPasswordHashing

# Spustenie konkrétneho testu
pytest tests/test_auth_local.py::TestPasswordHashing::test_password_hashing
```

#### **Pokročilé Spustenie**
```bash
# Spustenie s verbose output
pytest -v

# Spustenie s output pre padnuté testy
pytest --tb=short

# Spustenie len rýchlych testov (bez integračných)
pytest -m "not integration"

# Spustenie len integračných testov
pytest -m "integration"
```

#### **Testovanie s Mockingom**
```bash
# Spustenie s disabled external calls
pytest --disable-external-calls

# Spustenie s mockovanými službami
pytest tests/test_integration.py -v
```

### Testovacie Fixtures

#### **Základné Fixtures**
- `db_session` - Clean database session
- `test_user_data` - Test user credentials
- `authenticated_client` - Authenticated test client
- `multiple_test_users` - Multiple users for isolation testing

#### **Mock Fixtures**
- `mock_websupport_service` - Mock Websupport API
- `mock_neon_auth_service` - Mock Neon Auth service
- `mock_ssl_service` - Mock SSL service

#### **Data Fixtures**
- `test_domains_data` - Test domain data
- `test_ssl_data` - Test SSL certificate data
- `audit_logs_data` - Test audit logs

### Testovacie Stratégie

#### **Unit Testy**
- Testujú jednotlivé funkcie a metódy
- Používajú mockovanie externých závislostí
- Rýchle spustenie
- Vysoká krytosť kódu

#### **Integration Testy**
- Testujú interakcie medzi komponentami
- Testujú kompletné workflowny
- Simulujú reálne použitie
- Testujú error handling

#### **API Testy**
- Testujú HTTP endpointy
- Testujú autentifikáciu a autorizáciu
- Testujú request/response formáty
- Testujú error responses

### Testovacie Scenáre

#### **Autentifikačné Scenáre**
1. **Úspešná registrácia a login**
2. **Neplatné prihlasovacie údaje**
3. **Token refresh**
4. **Token expirácia**
5. **Neon Auth fallback**

#### **Domain Management Scenáre**
1. **Domain lifecycle** (create → list → details → delete)
2. **Domain validation**
3. **User isolation**
4. **Error handling**

#### **SSL Management Scenáre**
1. **Certificate generation**
2. **Domain validation**
3. **Email validation**
4. **Certificate operations**

#### **System Integration Scenáre**
1. **Complete user workflow**
2. **Authentication flow**
3. **Error recovery**
4. **Performance testing**

### Coverage Reporting

#### **Generovanie Coverage**
```bash
# HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=app --cov-report=term

# XML report (pre CI/CD)
pytest --cov=app --cov-report=xml
```

#### **Coverage Ciele**
- **Line coverage**: >90%
- **Branch coverage**: >85%
- **Function coverage**: >95%

### CI/CD Integrácia

#### **GitHub Actions**
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/test_requirements.txt
      - name: Run tests
        run: pytest
      - name: Coverage report
        run: pytest --cov=app --cov-report=xml
```

#### **Pre-commit Hooks**
```bash
# Nastavenie pre-commit
pre-commit install

# Spustenie pre-commit
pre-commit run --all-files
```

### Testovacie Best Practices

#### **Test Naming**
- Používať descriptive názvy
- Používať `test_` prefix
- Rozlišovať medzi unit a integration testami

#### **Test Isolation**
- Každý test by mal byť nezávislý
- Používať clean database pre každý test
- Vyčisťovať mocky po testoch

#### **Mocking Strategy**
- Mockovať externé API volania
- Mockovať databázové operácie
- Nepoužívať mocky pre business logic

#### **Error Testing**
- Testovať všetky error scenáre
- Testovať edge cases
- Testovať input validation

### Debugging Testov

#### **Verbose Output**
```bash
pytest -v -s tests/test_auth_local.py
```

#### **Debug Specific Test**
```bash
pytest tests/test_auth_local.py::TestPasswordHashing::test_password_hashing -v -s
```

#### **Using pdb**
```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    # Test code here
```

### Test Data Management

#### **Test Data Factory**
Používať `TestDataFactory` pre vytváranie testovacích dát:

```python
@pytest.fixture
def test_user(test_data_factory):
    return test_data_factory.create_user_data(1)
```

#### **Test Data Cleanup**
Automatické čistenie dát po každom teste:

```python
@pytest.fixture(autouse=True)
def cleanup_database():
    yield
    # Cleanup handled by db_session fixture
```

### Performance Testing

#### **Response Time Testing**
```python
def test_api_response_time(performance_timer):
    timer.start()
    response = client.get("/api/users/me")
    timer.stop()
    
    assert response.status_code == 200
    assert timer.elapsed() < 1.0  # Under 1 second
```

#### **Concurrent Testing**
```python
import concurrent.futures

def test_concurrent_requests():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    assert all(result == 200 for result in results)
```

### Test Documentation

Každý test by mal mať:
- **Clear description** v docstringu
- **Test scenario** description
- **Expected behavior** documentation
- **Edge cases** coverage

```python
def test_user_registration_success(self):
    """
    Test successful user registration.
    
    Scenario: User provides valid email and password
    Expected: User is created and access token is returned
    Edge cases: None
    """
    # Test implementation
```

Tento testovací framework poskytuje komplexné pokrytie všetkých funkcií API Centrum Backend systému a zabezpečuje kvalitný kód, robustné error handling a spoľahlivé fungovanie systému.