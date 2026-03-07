# Security Blueprint

## Prehľad
Tento blueprint definuje komplexné bezpečnostné opatrenia pre API Centrum Backend systém.

## Ciele
- Ochrana pred bežnými web bezpečnostnými hrozbami
- Validácia a sanitizácia všetkých vstupov
- Ochrana citlivých údajov
- Audit logovanie všetkých dôležitých operácií
- Rate limiting a ochrana proti DDoS

## 1. Input Validation & Sanitization

### 1.1 Validácia dátových typov
```python
# Validácia emailových adries
def validate_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Validácia doménových mien
def validate_domain(domain: str) -> bool:
    domain_regex = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    return re.match(domain_regex, domain) is not None and len(domain) <= 253

# Validácia hesiel
def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

### 1.2 Sanitizácia vstupov
```python
import html
import bleach

def sanitize_input(input_string: str) -> str:
    """Ochrana proti XSS útokom"""
    # Odstránenie HTML tagov
    clean = bleach.clean(input_string, tags=[], attributes={}, strip=True)
    # HTML escaping
    return html.escape(clean)

def sanitize_filename(filename: str) -> str:
    """Bezpečné spracovanie názvov súborov"""
    # Povoliť iba alfanumerické znaky, bodky a podčiarkovníky
    safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Odstrániť viacnásobné podčiarkovníky
    safe_chars = re.sub(r'_+', '_', safe_chars)
    return safe_chars[:255]  # Obmedzenie dĺžky
```

### 1.3 SQL Injection ochrana
```python
from sqlalchemy import text

# NIKDY nepoužívať string formatting v SQL dopytoch
def get_user_by_id(user_id: int):
    # ZLE: f"SELECT * FROM users WHERE id = {user_id}"
    # DOBRE: Použitie parametrizovaných dopytov
    query = text("SELECT * FROM users WHERE id = :user_id")
    result = db.execute(query, {"user_id": user_id})
    return result.fetchone()
```

## 2. Rate Limiting

### 2.1 Redis-based rate limiting
```python
import redis
import time
from functools import wraps

class RateLimiter:
    def __init__(self, redis_client, limit=100, window=3600):
        self.redis = redis_client
        self.limit = limit
        self.window = window
    
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        
        # Odstrániť staré záznamy
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Získať aktuálny počet požiadaviek
        current_requests = self.redis.zcard(key)
        
        if current_requests >= self.limit:
            return False
        
        # Pridať novú požiadavku
        self.redis.zadd(key, {str(now): now})
        self.redis.expire(key, self.window)
        
        return True

# Decorátor pre rate limiting
def rate_limit(limit=100, window=3600):
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    limiter = RateLimiter(redis_client, limit, window)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Získať IP adresu z requestu
            request = kwargs.get('request') or args[0]
            client_ip = request.client.host
            
            if not limiter.is_allowed(f"rate_limit:{client_ip}"):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Použitie
@router.get("/api/protected")
@rate_limit(limit=60, window=3600)  # 60 požiadaviek za hodinu
async def protected_endpoint(request: Request):
    return {"message": "OK"}
```

### 2.2 API Key-based rate limiting
```python
def api_key_rate_limit(api_key: str, endpoint: str):
    """Rôzne limity pre rôzne API kľúče a endpointy"""
    limits = {
        "free_tier": {"requests_per_hour": 1000, "requests_per_minute": 100},
        "premium_tier": {"requests_per_hour": 10000, "requests_per_minute": 1000},
        "enterprise_tier": {"requests_per_hour": 100000, "requests_per_minute": 10000}
    }
    
    # Získať typ účtu z databázy
    user_tier = get_user_tier(api_key)
    limit_config = limits.get(user_tier, limits["free_tier"])
    
    # Aplikovať rate limiting
    # Implementácia podobná vyššie, ale s dynamickými limitmi
```

## 3. Audit Logging

### 3.1 Audit log model
```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from .db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, nullable=True)  # None pre anonymné akcie
    action = Column(String(100), nullable=False)  # login, domain_create, ssl_generate atd.
    resource_type = Column(String(50), nullable=False)  # user, domain, ssl_certificate
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)  # Dodatočné informácie
    ip_address = Column(String(45), nullable=True)  # IPv6 podpora
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
```

### 3.2 Audit log middleware
```python
from fastapi import Request
import logging
import json

class AuditLogger:
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_action(self, request: Request, action: str, resource_type: str, 
                        resource_id: str = None, details: dict = None, success: bool = True):
        
        # Získať informácie o používateľovi
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = decode_access_token(token)
                user_id = payload.get("sub")
            except:
                pass
        
        # Vytvoriť audit záznam
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            success=success
        )
        
        self.db.add(audit_log)
        self.db.commit()

# Middleware pre automatické logovanie
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Zaznamenať request
    response = await call_next(request)
    
    # Vypočítať trvanie requestu
    duration = time.time() - start_time
    
    # Logovať akciu
    audit_logger = AuditLogger(db_session)
    await audit_logger.log_action(
        request=request,
        action=f"{request.method}_{request.url.path}",
        resource_type="api_endpoint",
        details={"duration": duration, "status_code": response.status_code},
        success=response.status_code < 400
    )
    
    return response
```

### 3.3 Security event monitoring
```python
class SecurityMonitor:
    def __init__(self, db_session):
        self.db = db_session
    
    def detect_suspicious_activity(self, user_id: int, action: str):
        """Detekcia podozrivých aktivít"""
        
        # Príliš veľa neúspešných pokusov o prihlásenie
        if action == "login_failed":
            failed_attempts = self.get_failed_login_attempts(user_id, minutes=15)
            if failed_attempts >= 5:
                self.trigger_security_alert(user_id, "multiple_failed_logins")
        
        # Príliš veľa požiadaviek na jeden endpoint
        if self.is_rate_limit_exceeded(user_id, action, window_minutes=5):
            self.trigger_security_alert(user_id, "rate_limit_exceeded")
    
    def get_failed_login_attempts(self, user_id: int, minutes: int = 15):
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        count = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login_failed",
            AuditLog.timestamp >= cutoff_time
        ).count()
        
        return count
    
    def trigger_security_alert(self, user_id: int, alert_type: str):
        """Spustenie bezpečnostného alertu"""
        alert = SecurityAlert(
            user_id=user_id,
            alert_type=alert_type,
            timestamp=datetime.utcnow(),
            severity="high" if alert_type in ["multiple_failed_logins"] else "medium"
        )
        
        self.db.add(alert)
        self.db.commit()
        
        # Odoslať notifikáciu
        self.send_security_notification(user_id, alert_type)
```

## 4. Data Encryption

### 4.1 Field-level encryption
```python
from cryptography.fernet import Fernet
import base64

class FieldEncryptor:
    def __init__(self, encryption_key: str):
        # Kľúč by mal byť uložený v environment variable
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, value: str) -> str:
        if not value:
            return value
        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_value: str) -> str:
        if not encrypted_value:
            return encrypted_value
        encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')

# Použitie v modeloch
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    # Šifrované pole pre citlivé údaje
    encrypted_api_key = Column(String(500))
    
    @property
    def api_key(self):
        if self.encrypted_api_key:
            return FieldEncryptor(settings.ENCRYPTION_KEY).decrypt(self.encrypted_api_key)
        return None
    
    @api_key.setter
    def api_key(self, value: str):
        if value:
            self.encrypted_api_key = FieldEncryptor(settings.ENCRYPTION_KEY).encrypt(value)
```

### 4.2 Database connection encryption
```python
# Konfigurácia databázy s SSL
DATABASE_URL = "postgresql://user:password@localhost/dbname?sslmode=require"

# Alebo v SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "sslcert": "/path/to/client-cert.pem",
        "sslkey": "/path/to/client-key.pem",
        "sslrootcert": "/path/to/ca-cert.pem"
    }
)
```

## 5. CORS Configuration

### 5.1 Bezpečné CORS nastavenie
```python
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    """Nastavenie bezpečného CORS"""
    
    # Povolené originy by mali byť explicitne definované
    allowed_origins = [
        "https://api-centrum.sk",
        "https://admin.api-centrum.sk",
        "https://localhost:3000",  # Iba pre vývoj
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Iba ak je potrebné
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key"],
        max_age=3600  # Cache pre OPTIONS requesty
    )
```

### 5.2 Dynamic CORS pre rôzne prostredia
```python
def get_cors_origins():
    """Získať CORS originy na základe prostredia"""
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return [
            "https://api-centrum.sk",
            "https://admin.api-centrum.sk"
        ]
    elif environment == "staging":
        return [
            "https://staging.api-centrum.sk",
            "https://staging-admin.api-centrum.sk"
        ]
    else:  # development
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080"
        ]
```

## 6. Security Headers

### 6.1 Security headers middleware
```python
from fastapi import Response

class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                
                # Pridať bezpečnostné hlavičky
                security_headers = [
                    (b"X-Content-Type-Options", b"nosniff"),
                    (b"X-Frame-Options", b"DENY"),
                    (b"X-XSS-Protection", b"1; mode=block"),
                    (b"Strict-Transport-Security", b"max-age=31536000; includeSubDomains"),
                    (b"Content-Security-Policy", b"default-src 'self'"),
                    (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
                ]
                
                headers.extend(security_headers)
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Použitie
app.add_middleware(SecurityHeadersMiddleware)
```

## 7. API Key Management

### 7.1 API Key model
```python
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_hash = Column(String(255), unique=True, index=True)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_minute = Column(Integer, default=100)
    
    user = relationship("User", back_populates="api_keys")

class User(Base):
    # ... existujúce polia
    api_keys = relationship("APIKey", back_populates="user")
```

### 7.2 API Key authentication
```python
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    
    # Overiť API kľúč
    api_key_hash = hash_api_key(api_key)
    db_key = db.query(APIKey).filter(
        APIKey.key_hash == api_key_hash,
        APIKey.is_active == True
    ).first()
    
    if not db_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Aktualizovať posledné použitie
    db_key.last_used = datetime.utcnow()
    db.commit()
    
    return db_key

# Použitie v endpointoch
@router.get("/api/protected")
async def protected_endpoint(api_key: APIKey = Depends(get_api_key)):
    return {"message": "Protected endpoint accessed"}
```

## 8. Dependency Requirements

### 8.1 Security dependencies
```txt
# requirements.txt
# ... existujúce závislosti

# Security libraries
cryptography>=3.4.8
bleach>=5.0.0
redis>=4.0.0
pyjwt[crypto]>=2.4.0

# Rate limiting
slowapi>=0.1.8

# Input validation
pydantic[email]>=1.9.0
```

## 9. Testing

### 9.1 Security test cases
```python
# tests/test_security.py

class TestInputValidation:
    def test_xss_protection(self):
        """Test XSS ochrany"""
        malicious_input = "<script>alert('xss')</script>"
        sanitized = sanitize_input(malicious_input)
        assert "<script>" not in sanitized
        assert "<script>" in sanitized
    
    def test_sql_injection_protection(self):
        """Test SQL injection ochrany"""
        malicious_input = "'; DROP TABLE users; --"
        # Test by running through actual database queries
        # Should not cause any damage
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Simulovať viacero požiadaviek z rovnakej IP
        # Overiť, že po prekročení limitu sa vráti 429 status

class TestAuthentication:
    def test_invalid_token_rejection(self):
        """Test odmietnutia neplatných tokenov"""
        invalid_tokens = [
            "invalid_token",
            "Bearer ",
            "Bearer invalid",
            ""
        ]
        
        for token in invalid_tokens:
            response = client.get("/api/protected", headers={"Authorization": token})
            assert response.status_code == 401
    
    def test_expired_token_handling(self):
        """Test spracovania expirovaných tokenov"""
        # Vytvoriť expirovaný token
        # Overiť, že API vráti 401 status

class TestAuditLogging:
    def test_audit_log_creation(self):
        """Test vytvárania audit logov"""
        # Vykonajte akciu, ktorá by mala byť zalogovaná
        # Overiť, že záznam existuje v databáze
    
    def test_security_alerts(self):
        """Test bezpečnostných alertov"""
        # Simulovať podozrivú aktivitu
        # Overiť, že bol vytvorený security alert
```

## 10. Deployment Considerations

### 10.1 Environment variables
```bash
# .env.production
# ... existujúce premenné

# Security keys
ENCRYPTION_KEY=your-32-byte-encryption-key-here
JWT_SECRET=your-jwt-secret-key-here
API_KEY_SALT=your-api-key-salt-here

# Rate limiting
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=https://api-centrum.sk,https://admin.api-centrum.sk
```

### 10.2 Docker security
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Vytvoriť non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Nastaviť working directory
WORKDIR /app

# Skopírovať requirements a nainštalovať závislosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopírovať aplikáciu
COPY . .

# Zmeniť vlastníka súborov
RUN chown -R appuser:appuser /app

# Spustiť ako non-root user
USER appuser

# Exponovať port
EXPOSE 8000

# Spustiť aplikáciu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 11. Monitoring & Alerting

### 11.1 Security metrics
```python
# Prometheus metrics pre security
from prometheus_client import Counter, Histogram

# Počítadlá pre rôzne typy bezpečnostných udalostí
security_events = Counter(
    'security_events_total',
    'Total number of security events',
    ['event_type', 'severity']
)

failed_logins = Counter(
    'failed_login_attempts_total',
    'Total number of failed login attempts',
    ['user_id', 'ip_address']
)

rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Total number of rate limit hits',
    ['endpoint', 'client_ip']
)

# Histogram pre dobu trvania overovania
auth_duration = Histogram(
    'auth_duration_seconds',
    'Time spent on authentication'
)
```

### 11.2 Security dashboard queries
```sql
-- Počet neúspešných prihlásení za posledných 24 hodín
SELECT COUNT(*) as failed_logins
FROM audit_logs 
WHERE action = 'login_failed' 
AND timestamp >= NOW() - INTERVAL '24 hours';

-- Top 10 IP adries s najviac neúspešnými prihláseniami
SELECT ip_address, COUNT(*) as failed_attempts
FROM audit_logs 
WHERE action = 'login_failed' 
AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY ip_address
ORDER BY failed_attempts DESC
LIMIT 10;

-- Počet API volaní podľa endpointu
SELECT 
    SUBSTRING(action FROM '^[A-Z]+_(.+)') as endpoint,
    COUNT(*) as request_count
FROM audit_logs 
WHERE action LIKE 'GET_%' OR action LIKE 'POST_%'
GROUP BY endpoint
ORDER BY request_count DESC;
```

## 12. Implementation Steps

1. **Základná validácia** (Týždeň 1)
   - Implementovať input validation funkcie
   - Pridať sanitizáciu všetkých endpointov
   - Testovanie XSS a SQL injection ochrany

2. **Rate limiting** (Týždeň 2)
   - Nastaviť Redis pre rate limiting
   - Implementovať rate limiting middleware
   - Pridať API key-based limity

3. **Audit logging** (Týždeň 3)
   - Vytvoriť audit log model
   - Implementovať audit middleware
   - Pridať security monitoring

4. **Šifrovanie** (Týždeň 4)
   - Implementovať field-level encryption
   - Nastaviť database SSL
   - Pridať environment variables pre kľúče

5. **CORS & Headers** (Týždeň 5)
   - Nastaviť bezpečné CORS
   - Pridať security headers
   - Konfigurovať pre rôzne prostredia

6. **API Keys** (Týždeň 6)
   - Vytvoriť API key model
   - Implementovať API key authentication
   - Pridať rate limiting pre API kľúče

7. **Testing & Documentation** (Týždeň 7)
   - Napísať komplexné security testy
   - Vytvoriť dokumentáciu
   - Performance testing

8. **Deployment & Monitoring** (Týždeň 8)
   - Nastaviť production deployment
   - Implementovať monitoring
   - Nastaviť alerting

## 13. Best Practices

- **Princíp najmenších výsad**: Každý komponent by mal mať iba tie oprávnenia, ktoré potrebuje
- **Defense in depth**: Viacvrstvová ochrana - žiadna jediná vrstva by nemala byť závislá
- **Fail secure**: Systém by mal byť v bezpečnom stave aj pri chybách
- **Logging & Monitoring**: Všetky dôležité akcie by mali byť zalogované a monitorované
- **Regular security audits**: Pravidelné kontroly a aktualizácie bezpečnostných opatrení

Tento blueprint poskytuje komplexný návod na implementáciu robustných bezpečnostných opatrení pre API Centrum Backend systém.