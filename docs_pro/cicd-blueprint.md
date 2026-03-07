# CI/CD Pipeline Blueprint

## Prehľad
Tento blueprint definuje kompletný CI/CD pipeline pre API Centrum Backend systém pomocou GitHub Actions.

## Ciele
- Automatizovať testovanie a deployment
- Nastaviť linting a code quality checks
- Implementovať multi-environment deployment
- Zabezpečiť rollback mechanizmy
- Optimalizovať build a deployment proces

## 1. GitHub Actions Workflow

### 1.1 Basic workflow structure
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Job 1: Code Quality & Testing
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r tests/test_requirements.txt
    
    - name: Run linting
      run: |
        flake8 app/ tests/
        black --check app/ tests/
        isort --check-only app/ tests/
    
    - name: Run type checking
      run: mypy app/ --ignore-missing-imports
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        JWT_SECRET: test-secret-key
        ENCRYPTION_KEY: test-encryption-key
      run: |
        pytest tests/ -v --cov=app --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  # Job 2: Security Scanning
  security:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: Run Bandit security linter
      run: |
        pip install bandit
        bandit -r app/ -f json -o bandit-report.json
        bandit -r app/

  # Job 3: Build Docker Image
  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        build-args: |
          BUILD_VERSION=${{ github.sha }}
          BUILD_TIME=${{ github.run_number }}

  # Job 4: Deploy to Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to Staging
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USER }}
        key: ${{ secrets.STAGING_SSH_KEY }}
        script: |
          cd /opt/api-centrum-staging
          docker-compose -f docker-compose.staging.yml pull
          docker-compose -f docker-compose.staging.yml up -d
          docker system prune -f

  # Job 5: Deploy to Production
  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to Production
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_SSH_KEY }}
        script: |
          cd /opt/api-centrum-production
          docker-compose -f docker-compose.production.yml pull
          docker-compose -f docker-compose.production.yml up -d
          docker system prune -f
```

### 1.2 Environment-specific workflows
```yaml
# .github/workflows/staging.yml
name: Staging Deployment

on:
  workflow_dispatch:
  push:
    branches: [ develop ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to Staging
      run: |
        # Staging deployment script
        echo "Deploying to staging environment..."
        
        # Run integration tests
        pytest tests/integration/ -v
        
        # Deploy to staging
        ansible-playbook deploy-staging.yml
        
        # Health check
        curl -f http://staging.api-centrum.sk/health || exit 1
```

```yaml
# .github/workflows/production.yml
name: Production Deployment

on:
  workflow_dispatch:
  release:
    types: [published]

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    concurrency: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Pre-deployment checks
      run: |
        # Run full test suite
        pytest tests/ -v
        
        # Security scan
        bandit -r app/
        
        # Performance tests
        pytest tests/performance/ -v
    
    - name: Blue-Green Deployment
      run: |
        # Blue-Green deployment strategy
        echo "Starting blue-green deployment..."
        
        # Deploy to green environment
        ansible-playbook deploy-green.yml
        
        # Health check green
        curl -f http://green.api-centrum.sk/health || exit 1
        
        # Switch traffic to green
        ansible-playbook switch-traffic.yml
        
        # Health check production
        curl -f http://api-centrum.sk/health || exit 1
        
        # Cleanup blue environment
        ansible-playbook cleanup-blue.yml
```

## 2. Docker Configuration

### 2.1 Multi-stage Dockerfile
```dockerfile
# Dockerfile
# Build stage
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Create logs directory
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Environment-specific docker-compose
```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/api_centrum_staging
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - LOG_LEVEL=INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - api-network
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: api_centrum_staging
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - api-network
  
  redis:
    image: redis:7
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - api-network
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/nginx.conf
      - ./ssl/staging:/etc/nginx/ssl
    depends_on:
      - api
    networks:
      - api-network

volumes:
  postgres_staging_data:

networks:
  api-network:
    driver: bridge
```

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  api:
    image: ghcr.io/your-org/api-centrum:latest
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/api_centrum_prod
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - LOG_LEVEL=WARNING
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - api-network
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: api_centrum_prod
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - api-network
    deploy:
      placement:
        constraints:
          - node.role == manager
  
  redis:
    image: redis:7
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_prod_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - api-network
    deploy:
      resources:
        limits:
          memory: 512M
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/production.conf:/etc/nginx/nginx.conf
      - ./ssl/production:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - api
    networks:
      - api-network
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.role == manager

volumes:
  postgres_prod_data:
    driver: local
  redis_prod_data:
    driver: local

networks:
  api-network:
    driver: overlay
    attachable: true
```

## 3. Environment Management

### 3.1 Environment configuration
```bash
# .env.staging
ENVIRONMENT=staging
DATABASE_URL=postgresql://postgres:password@localhost:5433/api_centrum_staging
REDIS_URL=redis://localhost:6380/0
JWT_SECRET=staging-jwt-secret-key
ENCRYPTION_KEY=staging-encryption-key
LOG_LEVEL=INFO
DEBUG=True

# Websupport API
WEBSUPPORT_API_KEY=staging-websupport-key
WEBSUPPORT_API_SECRET=staging-websupport-secret

# Neon Auth
NEON_AUTH_CLIENT_ID=staging-client-id
NEON_AUTH_CLIENT_SECRET=staging-client-secret
NEON_AUTH_REDIRECT_URI=https://staging.api-centrum.sk/auth/callback

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_URL=https://staging-grafana.api-centrum.sk
```

```bash
# .env.production
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/api_centrum_prod
REDIS_URL=redis://redis:6379/0
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
LOG_LEVEL=WARNING
DEBUG=False

# Websupport API
WEBSUPPORT_API_KEY=${WEBSUPPORT_API_KEY}
WEBSUPPORT_API_SECRET=${WEBSUPPORT_API_SECRET}

# Neon Auth
NEON_AUTH_CLIENT_ID=${NEON_AUTH_CLIENT_ID}
NEON_AUTH_CLIENT_SECRET=${NEON_AUTH_CLIENT_SECRET}
NEON_AUTH_REDIRECT_URI=https://api-centrum.sk/auth/callback

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_URL=https://grafana.api-centrum.sk
```

### 3.2 Environment deployment scripts
```bash
#!/bin/bash
# scripts/deploy-staging.sh

set -e

echo "🚀 Deploying to Staging Environment"

# Load environment variables
source .env.staging

# Run database migrations
echo "📦 Running database migrations..."
docker-compose -f docker-compose.staging.yml exec -T postgres psql -U postgres -d api_centrum_staging -f migrations/001_initial.sql

# Build and deploy
echo "🏗️ Building and deploying..."
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d

# Run health checks
echo "🏥 Running health checks..."
sleep 30
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed"
    exit 1
}

echo "✅ Staging deployment completed successfully"
```

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

echo "🚀 Deploying to Production Environment"

# Load environment variables
source .env.production

# Backup database
echo "💾 Creating database backup..."
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U postgres api_centrum_prod > backups/$(date +%Y%m%d_%H%M%S).sql

# Blue-Green deployment
echo "🔄 Starting blue-green deployment..."

# Deploy to green environment
docker-compose -f docker-compose.green.yml up -d

# Health check green
sleep 30
curl -f http://green.api-centrum.sk/health || {
    echo "❌ Green environment health check failed"
    docker-compose -f docker-compose.green.yml down
    exit 1
}

# Switch traffic to green
echo "🔀 Switching traffic to green environment..."
docker-compose -f docker-compose.nginx.yml exec nginx nginx -s reload

# Health check production
sleep 10
curl -f http://api-centrum.sk/health || {
    echo "❌ Production health check failed"
    # Rollback to blue
    docker-compose -f docker-compose.nginx.yml exec nginx nginx -s reload
    docker-compose -f docker-compose.green.yml down
    exit 1
}

# Cleanup blue environment
echo "🧹 Cleaning up blue environment..."
docker-compose -f docker-compose.blue.yml down

echo "✅ Production deployment completed successfully"
```

## 4. Rollback Mechanisms

### 4.1 Automated rollback script
```bash
#!/bin/bash
# scripts/rollback.sh

set -e

ENVIRONMENT=${1:-production}
TARGET_VERSION=${2:-previous}

echo "🔄 Starting rollback to $TARGET_VERSION in $ENVIRONMENT"

case $ENVIRONMENT in
    "staging")
        COMPOSE_FILE="docker-compose.staging.yml"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.production.yml"
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# Get previous image tag
if [ "$TARGET_VERSION" = "previous" ]; then
    PREVIOUS_IMAGE=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep api-centrum | sed -n '2p')
else
    PREVIOUS_IMAGE="ghcr.io/your-org/api-centrum:$TARGET_VERSION"
fi

echo "📦 Rolling back to image: $PREVIOUS_IMAGE"

# Update compose file with previous image
sed -i "s|image: ghcr.io/your-org/api-centrum:.*|image: $PREVIOUS_IMAGE|g" $COMPOSE_FILE

# Deploy previous version
docker-compose -f $COMPOSE_FILE down
docker-compose -f $COMPOSE_FILE up -d

# Health check
sleep 30
curl -f http://localhost:8000/health || {
    echo "❌ Rollback health check failed"
    exit 1
}

echo "✅ Rollback completed successfully"
```

### 4.2 Database rollback
```python
# scripts/rollback_database.py
"""
Database rollback script for API Centrum
"""

import os
import subprocess
import datetime
from pathlib import Path

def rollback_database(environment: str, backup_file: str = None):
    """Rollback database to previous state"""
    
    # Environment configuration
    env_config = {
        "staging": {
            "host": "localhost",
            "port": "5433",
            "database": "api_centrum_staging",
            "user": "postgres",
            "password": "password"
        },
        "production": {
            "host": "postgres",
            "port": "5432",
            "database": "api_centrum_prod",
            "user": "postgres",
            "password": os.environ.get("DB_PASSWORD")
        }
    }
    
    config = env_config[environment]
    
    if not backup_file:
        # Find latest backup
        backup_dir = Path(f"./backups/{environment}")
        backup_files = list(backup_dir.glob("*.sql"))
        if not backup_files:
            raise Exception(f"No backup files found in {backup_dir}")
        
        backup_file = max(backup_files, key=lambda p: p.stat().st_mtime)
    
    print(f"🔄 Rolling back database {environment} from {backup_file}")
    
    # Create current backup before rollback
    current_backup = f"./backups/{environment}/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_pre_rollback.sql"
    subprocess.run([
        "pg_dump",
        f"--host={config['host']}",
        f"--port={config['port']}",
        f"--username={config['user']}",
        f"--dbname={config['database']}",
        f"--file={current_backup}"
    ], check=True)
    
    # Restore from backup
    subprocess.run([
        "psql",
        f"--host={config['host']}",
        f"--port={config['port']}",
        f"--username={config['user']}",
        f"--dbname={config['database']}",
        f"--file={backup_file}"
    ], check=True)
    
    print(f"✅ Database rollback completed")

if __name__ == "__main__":
    import sys
    environment = sys.argv[1] if len(sys.argv) > 1 else "production"
    backup_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    rollback_database(environment, backup_file)
```

## 5. Testing in CI/CD

### 5.1 Integration tests
```python
# tests/integration/test_api_integration.py
"""
Integration tests for API Centrum
"""

import pytest
import requests
import time
from typing import Dict, Any

class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Get API base URL from environment"""
        import os
        return os.getenv("API_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, api_base_url):
        """Get authentication headers"""
        # Login to get token
        login_response = requests.post(f"{api_base_url}/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        return {"Authorization": f"Bearer {token}"}
    
    def test_health_check(self, api_base_url):
        """Test health check endpoint"""
        response = requests.get(f"{api_base_url}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_domain_crud(self, api_base_url, auth_headers):
        """Test domain CRUD operations"""
        # Create domain
        create_response = requests.post(f"{api_base_url}/api/domains", 
                                      headers=auth_headers,
                                      json={
                                          "name": "test-integration.com",
                                          "description": "Integration test domain"
                                      })
        assert create_response.status_code == 201
        
        domain_data = create_response.json()
        domain_id = domain_data["id"]
        
        # Get domain
        get_response = requests.get(f"{api_base_url}/api/domains/{domain_id}",
                                  headers=auth_headers)
        assert get_response.status_code == 200
        
        # Update domain
        update_response = requests.put(f"{api_base_url}/api/domains/{domain_id}",
                                     headers=auth_headers,
                                     json={
                                         "description": "Updated integration test domain"
                                     })
        assert update_response.status_code == 200
        
        # Delete domain
        delete_response = requests.delete(f"{api_base_url}/api/domains/{domain_id}",
                                        headers=auth_headers)
        assert delete_response.status_code == 204
    
    def test_ssl_operations(self, api_base_url, auth_headers):
        """Test SSL operations"""
        # Generate SSL certificate
        ssl_response = requests.post(f"{api_base_url}/api/ssl/generate",
                                   headers=auth_headers,
                                   json={
                                       "domain": "test-integration.com",
                                       "email": "admin@test-integration.com"
                                   })
        
        # SSL generation might take time, so we check if request was accepted
        assert ssl_response.status_code in [200, 201, 202]
    
    def test_rate_limiting(self, api_base_url):
        """Test rate limiting"""
        # Make multiple requests rapidly
        for i in range(100):
            response = requests.get(f"{api_base_url}/api/health")
            if response.status_code == 429:
                # Rate limit hit
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                break
        else:
            # Rate limit not hit, which might be expected in test environment
            pass

class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_database_connection(self):
        """Test database connection"""
        from app.db import engine
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_user_creation(self):
        """Test user creation in database"""
        from app.crud import CRUDUser
        from app.db import SessionLocal
        
        db = SessionLocal()
        try:
            # Create test user
            user = CRUDUser.create(db, "integration@test.com", "testpassword123")
            assert user.email == "integration@test.com"
            assert user.is_active == True
            
            # Clean up
            db.delete(user)
            db.commit()
        finally:
            db.close()

class TestExternalAPIIntegration:
    """Integration tests for external APIs"""
    
    def test_websupport_api(self):
        """Test Websupport API integration"""
        from app.websupport import WebsupportService
        
        service = WebsupportService()
        
        # Test listing domains (should work even if empty)
        domains = service.list_domains()
        assert isinstance(domains, list)
    
    def test_neon_auth(self):
        """Test Neon Auth integration"""
        from app.neon_auth import NeonAuthService
        
        service = NeonAuthService()
        
        # Test trial status check
        status = service.check_trial_status()
        assert isinstance(status, dict)
        assert "active" in status
```

### 5.2 Performance tests
```python
# tests/performance/test_performance.py
"""
Performance tests for API Centrum
"""

import pytest
import requests
import time
import concurrent.futures
from typing import List, Dict, Any

class TestPerformance:
    """Performance tests"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Get API base URL from environment"""
        import os
        return os.getenv("API_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, api_base_url):
        """Get authentication headers"""
        login_response = requests.post(f"{api_base_url}/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        return {"Authorization": f"Bearer {token}"}
    
    def test_response_time(self, api_base_url, auth_headers):
        """Test API response times"""
        # Test multiple endpoints
        endpoints = [
            "/api/health",
            "/api/dashboard/stats",
            "/api/domains"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{api_base_url}{endpoint}", headers=auth_headers)
            duration = time.time() - start_time
            
            assert response.status_code == 200
            assert duration < 2.0  # Response should be under 2 seconds
    
    def test_concurrent_requests(self, api_base_url, auth_headers):
        """Test concurrent request handling"""
        def make_request():
            return requests.get(f"{api_base_url}/api/health")
        
        # Make 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 50
    
    def test_database_performance(self):
        """Test database performance"""
        from app.db import SessionLocal
        from app.crud import CRUDUser
        import time
        
        db = SessionLocal()
        try:
            # Test bulk user creation
            start_time = time.time()
            
            users = []
            for i in range(100):
                user = CRUDUser.create(db, f"perf-test-{i}@example.com", "password123")
                users.append(user)
            
            creation_time = time.time() - start_time
            assert creation_time < 10.0  # Should create 100 users in under 10 seconds
            
            # Clean up
            for user in users:
                db.delete(user)
            db.commit()
            
        finally:
            db.close()
    
    def test_memory_usage(self, api_base_url, auth_headers):
        """Test memory usage under load"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests
        for _ in range(1000):
            requests.get(f"{api_base_url}/api/health", headers=auth_headers)
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100
```

## 6. Implementation Steps

### 6.1 Week 1: Basic CI/CD Setup
- [ ] Vytvoriť základný GitHub Actions workflow
- [ ] Nastaviť testovanie a linting
- [ ] Pridať Docker build a push
- [ ] Nastaviť environment secrets

### 6.2 Week 2: Environment Configuration
- [ ] Vytvoriť environment-specific docker-compose súbory
- [ ] Nastaviť environment variables
- [ ] Vytvoriť deployment skripty
- [ ] Nastaviť staging environment

### 6.3 Week 3: Production Deployment
- [ ] Nastaviť production environment
- [ ] Implementovať blue-green deployment
- [ ] Pridať health checks
- [ ] Nastaviť monitoring

### 6.4 Week 4: Rollback & Recovery
- [ ] Vytvoriť rollback skripty
- [ ] Nastaviť automatické backupy
- [ ] Implementovať disaster recovery
- [ ] Testovať rollback proces

### 6.5 Week 5: Performance & Security
- [ ] Pridať performance testy
- [ ] Nastaviť security scanning
- [ ] Implementovať vulnerability scanning
- [ ] Optimalizovať build proces

### 6.6 Week 6: Polish & Documentation
- [ ] Dokumentovať deployment proces
- [ ] Vytvoriť runbooks
- [ ] Nastaviť notifikácie
- [ ] Final testing a review

## 7. Best Practices

### 7.1 CI/CD best practices
- **Fail fast**: Rýchlo detekovať problémy v pipeline
- **Parallel execution**: Spúšťať nezávislé úlohy paralelne
- **Caching**: Používať caching pre rýchlejšie buildy
- **Security**: Skenovať image na vulnerabilities
- **Rollback**: Mať automatizovaný rollback proces

### 7.2 Docker best practices
- **Multi-stage builds**: Redukovať veľkosť finálnych image
- **Non-root user**: Spúšťať kontajnery ako non-root user
- **Health checks**: Implementovať health checks
- **Resource limits**: Nastaviť resource limity
- **Security scanning**: Skenuť image na vulnerabilities

### 7.3 Deployment best practices
- **Blue-green deployment**: Minimalizovať downtime
- **Canary releases**: Postupné nasadenie
- **Monitoring**: Sledovať metriky po deploymente
- **Rollback**: Mať rýchly rollback proces
- **Documentation**: Dokumentovať deployment proces

Tento blueprint poskytuje komplexný návod na implementáciu robustného CI/CD pipeline pre API Centrum Backend systém.