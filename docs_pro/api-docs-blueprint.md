# API Documentation Blueprint

## Prehľad
Tento blueprint definuje komplexnú API dokumentáciu pre API Centrum Backend systém pomocou OpenAPI/Swagger.

## Ciele
- Vytvoriť kompletnú OpenAPI špecifikáciu
- Poskytnúť podrobné popisy všetkých endpointov
- Vytvoriť interaktívnu dokumentáciu
- Zahrnúť príklady request/response
- Definovať všetky dátové modely a schémy

## 1. OpenAPI Configuration

### 1.1 Basic OpenAPI setup
```python
# app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="API Centrum Backend",
    description="Backend API pre správu domén a SSL certifikátov",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="API Centrum Backend",
        version="1.0.0",
        description="Backend API pre správu domén a SSL certifikátov",
        routes=app.routes,
    )
    
    # Pridať custom informácie
    openapi_schema["info"]["contact"] = {
        "name": "API Centrum Team",
        "email": "support@api-centrum.sk",
        "url": "https://api-centrum.sk"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Pridať security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 1.2 Custom OpenAPI components
```python
# app/openapi_config.py
from fastapi.openapi.utils import get_openapi

def get_custom_openapi():
    """Vytvoriť custom OpenAPI schému"""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "API Centrum Backend",
            "description": """
# API Centrum Backend Documentation

Backend API pre správu domén a SSL certifikátov.

## Autentifikácia

API podporuje dva typy autentifikácie:

1. **JWT Token** (Bearer token)
   - Header: `Authorization: Bearer <token>`
   - Používa sa pre užívateľov

2. **API Key**
   - Header: `X-API-Key: <api_key>`
   - Používa sa pre programový prístup

## Rate Limiting

- Free tier: 1000 requestov/hod
- Premium tier: 10000 requestov/hod
- Enterprise tier: 100000 requestov/hod

## Chybové stavy

- `401 Unauthorized` - Neplatný alebo chýbajúci token
- `403 Forbidden` - Nedostatočné oprávnenia
- `429 Too Many Requests` - Prekročený rate limit
- `500 Internal Server Error` - Serverová chyba
""",
            "version": "1.0.0",
            "contact": {
                "name": "API Centrum Support",
                "email": "support@api-centrum.sk",
                "url": "https://api-centrum.sk"
            },
            "license": {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "https://api.api-centrum.sk",
                "description": "Production server"
            },
            {
                "url": "https://staging.api-centrum.sk",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ],
        "tags": [
            {
                "name": "Authentication",
                "description": "Endpoints pre autentifikáciu a autorizáciu"
            },
            {
                "name": "Users",
                "description": "Správa užívateľov a ich účtov"
            },
            {
                "name": "Domains",
                "description": "Správa domén a ich nastavení"
            },
            {
                "name": "SSL",
                "description": "Generovanie a správa SSL certifikátov"
            },
            {
                "name": "Dashboard",
                "description": "Štatistiky a monitorovacie endpointy"
            },
            {
                "name": "Monitoring",
                "description": "Health check a monitorovacie endpointy"
            }
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token pre užívateľov"
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API kľúč pre programový prístup"
                }
            },
            "schemas": {
                # Tu budú definované všetky schémy
            },
            "responses": {
                "UnauthorizedError": {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            },
                            "example": {
                                "error": "Unauthorized",
                                "message": "Invalid or missing authentication token",
                                "code": "UNAUTHORIZED"
                            }
                        }
                    }
                },
                "ForbiddenError": {
                    "description": "Forbidden",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            },
                            "example": {
                                "error": "Forbidden",
                                "message": "Insufficient permissions",
                                "code": "FORBIDDEN"
                            }
                        }
                    }
                },
                "RateLimitError": {
                    "description": "Rate Limit Exceeded",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            },
                            "example": {
                                "error": "Too Many Requests",
                                "message": "Rate limit exceeded. Try again later.",
                                "code": "RATE_LIMIT_EXCEEDED"
                            }
                        }
                    }
                }
            }
        }
    }
```

## 2. Data Models & Schemas

### 2.1 User schemas
```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    full_name: Optional[str] = Field(None, example="John Doe")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="SecurePassword123!")

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, example="John Doe")
    is_active: Optional[bool] = Field(None, example=True)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    account_type: str  # "local" or "neon_auth"
    
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    total_domains: int
    recent_activities: int
    last_login: Optional[datetime]
    account_type: str

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePassword123!")

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., example="CurrentPassword123!")
    new_password: str = Field(..., min_length=8, example="NewSecurePassword123!")

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., example="reset_token_here")
    new_password: str = Field(..., min_length=8, example="NewSecurePassword123!")
```

### 2.2 Domain schemas
```python
# app/schemas/domain.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class DomainBase(BaseModel):
    name: str = Field(..., example="example.com", description="Názov domény")
    description: Optional[str] = Field(None, example="Hlavná doména pre web")

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    description: Optional[str] = Field(None, example="Aktualizovaný popis")

class DomainResponse(DomainBase):
    id: int
    user_id: int
    created_at: datetime
    status: str  # "active", "pending", "suspended"
    dns_records: List[Dict] = []
    
    class Config:
        from_attributes = True

class DomainListResponse(BaseModel):
    domains: List[DomainResponse]
    total: int
    page: int
    size: int

class DomainDetails(BaseModel):
    id: int
    name: str
    description: Optional[str]
    user_id: int
    created_at: datetime
    status: str
    dns_records: List[Dict]
    ssl_status: str  # "none", "pending", "active", "expired"
    last_check: Optional[datetime]

class DomainCheckRequest(BaseModel):
    domain: str = Field(..., example="example.com")

class DomainCheckResponse(BaseModel):
    domain: str
    available: bool
    price: Optional[float]
    currency: Optional[str]
    error: Optional[str]
```

### 2.3 SSL schemas
```python
# app/schemas/ssl.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class SSLCertificateRequest(BaseModel):
    domain: str = Field(..., example="example.com")
    email: EmailStr = Field(..., example="admin@example.com")
    certificate_type: str = Field(default="lets_encrypt", example="lets_encrypt")

class SSLCertificateResponse(BaseModel):
    id: int
    domain: str
    certificate_path: str
    private_key_path: str
    status: str  # "pending", "active", "expired", "error"
    created_at: datetime
    expires_at: Optional[datetime]
    issuer: Optional[str]
    
    class Config:
        from_attributes = True

class SSLStatusResponse(BaseModel):
    domain: str
    exists: bool
    last_modified: Optional[datetime]
    expires_at: Optional[datetime]
    issuer: Optional[str]
    fingerprint: Optional[str]

class SSLRenewRequest(BaseModel):
    domain: str = Field(..., example="example.com")

class SSLRevokeRequest(BaseModel):
    domain: str = Field(..., example="example.com")

class SSLListResponse(BaseModel):
    certificates: List[SSLCertificateResponse]
    total: int
```

### 2.4 Dashboard schemas
```python
# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class SystemHealth(BaseModel):
    websupport_api: str  # "online" or "offline"
    database: str  # "online" or "offline"
    neon_auth_trial: str  # "active" or "inactive"
    timestamp: str

class ActivityLog(BaseModel):
    action: str
    timestamp: datetime
    resource_type: str
    resource_id: Optional[str]
    details: Optional[Dict]

class DashboardStats(BaseModel):
    user_stats: Dict
    system_health: SystemHealth
    timestamp: str

class RecentActivities(BaseModel):
    activities: List[ActivityLog]
    count: int

class UsageMetrics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    top_endpoints: List[Dict]
    error_rates: Dict

class SecurityMetrics(BaseModel):
    total_logins: int
    failed_logins: int
    rate_limit_hits: int
    suspicious_activities: int
    security_alerts: List[Dict]
```

## 3. Endpoint Documentation

### 3.1 Authentication endpoints
```python
# app/auth_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from .schemas import LoginRequest, LoginResponse, RefreshTokenRequest
from .auth import authenticate_user, refresh_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="""
    Prihlási užívateľa a vráti JWT tokeny.
    
    **Rate limit:** 10 pokusov za 15 minút
    """,
    responses={
        200: {
            "description": "Successful login",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "is_active": True,
                            "created_at": "2023-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Unauthorized",
                        "message": "Invalid email or password",
                        "code": "INVALID_CREDENTIALS"
                    }
                }
            }
        },
        429: {
            "description": "Too many login attempts",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Too Many Requests",
                        "message": "Too many login attempts. Please try again later.",
                        "code": "TOO_MANY_ATTEMPTS"
                    }
                }
            }
        }
    }
)
async def login(login_data: LoginRequest):
    """Prihlási užívateľa"""
    return await authenticate_user(login_data.email, login_data.password)

@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token",
    description="Obnoví access token pomocou refresh tokenu"
)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Obnoví access token"""
    return await refresh_access_token(refresh_data.refresh_token)

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Odhlási užívateľa (blacklistuje token)"
)
async def logout(token: str = Depends(HTTPBearer())):
    """Odhlási užívateľa"""
    # Implementácia blacklistingu tokenu
    pass
```

### 3.2 Domain endpoints
```python
# app/domains/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas import DomainCreate, DomainResponse, DomainListResponse
from ..auth import get_current_user
from ..crud import CRUDDomain

router = APIRouter(prefix="/domains", tags=["Domains"])

@router.get(
    "/",
    response_model=DomainListResponse,
    summary="List user domains",
    description="Zoznam všetkých domén užívateľa",
    responses={
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        403: {"$ref": "#/components/responses/ForbiddenError"}
    }
)
async def list_domains(
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zoznam domén užívateľa"""
    domains = CRUDDomain.get_user_domains(
        db, current_user.id, page, size, search, status
    )
    total = CRUDDomain.count_user_domains(db, current_user.id, search, status)
    
    return {
        "domains": domains,
        "total": total,
        "page": page,
        "size": size
    }

@router.post(
    "/",
    response_model=DomainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new domain",
    description="""
    Vytvorí novú doménu.
    
    **Poznámka:** Táto operácia iba zaregistruje doménu v systéme.
    Skutočné vytvorenie domény na Websupport prebieha asynchrónne.
    """,
    responses={
        201: {
            "description": "Domain created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "example.com",
                        "description": "Hlavná doména",
                        "user_id": 1,
                        "created_at": "2023-01-01T00:00:00Z",
                        "status": "pending"
                    }
                }
            }
        },
        400: {
            "description": "Invalid domain name or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Bad Request",
                        "message": "Invalid domain name format",
                        "code": "INVALID_DOMAIN_NAME"
                    }
                }
            }
        }
    }
)
async def create_domain(
    domain_data: DomainCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vytvorí novú doménu"""
    # Validácia domény
    if not validate_domain(domain_data.name):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": "Invalid domain name format",
                "code": "INVALID_DOMAIN_NAME"
            }
        )
    
    return CRUDDomain.create(db, domain_data, current_user.id)

@router.get(
    "/{domain_id}",
    response_model=DomainDetails,
    summary="Get domain details",
    description="Získanie detailov o konkrétnej doméne"
)
async def get_domain_details(
    domain_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Získanie detailov o doméne"""
    domain = CRUDDomain.get_by_id_and_user(db, domain_id, current_user.id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    return domain

@router.put(
    "/{domain_id}",
    response_model=DomainResponse,
    summary="Update domain",
    description="Aktualizuje popis domény"
)
async def update_domain(
    domain_id: int,
    domain_data: DomainUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualizuje doménu"""
    domain = CRUDDomain.get_by_id_and_user(db, domain_id, current_user.id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    return CRUDDomain.update(db, domain, domain_data)

@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete domain",
    description="""
    Zmaže doménu zo systému.
    
    **Poznámka:** Táto operácia iba odstráni doménu z API Centrum.
    Skutočné zmazanie z Websupport prebieha asynchrónne.
    """
)
async def delete_domain(
    domain_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zmaže doménu"""
    domain = CRUDDomain.get_by_id_and_user(db, domain_id, current_user.id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    CRUDDomain.delete(db, domain)
```

### 3.3 SSL endpoints
```python
# app/ssl/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import SSLCertificateRequest, SSLCertificateResponse
from ..auth import get_current_user
from ..ssl.services import SSLService

router = APIRouter(prefix="/ssl", tags=["SSL"])

@router.post(
    "/generate",
    response_model=SSLCertificateResponse,
    summary="Generate SSL certificate",
    description="""
    Vygeneruje SSL certifikát pre doménu pomocou Let's Encrypt.
    
    **Poznámka:** Táto operácia môže trvať niekoľko minút.
    """
)
async def generate_ssl_certificate(
    ssl_data: SSLCertificateRequest,
    current_user = Depends(get_current_user)
):
    """Vygeneruje SSL certifikát"""
    try:
        result = await SSLService.generate_ssl_certificate(
            ssl_data.domain, 
            ssl_data.email
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SSL certificate: {str(e)}"
        )

@router.get(
    "/{domain}",
    response_model=SSLStatusResponse,
    summary="Get SSL certificate status",
    description="Získanie stavu SSL certifikátu pre doménu"
)
async def get_ssl_status(
    domain: str,
    current_user = Depends(get_current_user)
):
    """Získanie stavu SSL certifikátu"""
    try:
        status = await SSLService.get_certificate_info(domain)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get SSL status: {str(e)}"
        )

@router.post(
    "/renew/{domain}",
    response_model=SSLCertificateResponse,
    summary="Renew SSL certificate",
    description="Obnoví SSL certifikát pre doménu"
)
async def renew_ssl_certificate(
    domain: str,
    current_user = Depends(get_current_user)
):
    """Obnoví SSL certifikát"""
    try:
        result = await SSLService.renew_certificate(domain)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to renew SSL certificate: {str(e)}"
        )

@router.delete(
    "/revoke/{domain}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke SSL certificate",
    description="Odvolá SSL certifikát pre doménu"
)
async def revoke_ssl_certificate(
    domain: str,
    current_user = Depends(get_current_user)
):
    """Odvolá SSL certifikát"""
    try:
        await SSLService.revoke_certificate(domain)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to revoke SSL certificate: {str(e)}"
        )
```

### 3.4 Dashboard endpoints
```python
# app/dashboard/routes.py
from fastapi import APIRouter, Depends
from ..schemas import DashboardStats, SystemHealth, RecentActivities
from ..auth import get_current_user
from ..dashboard import DashboardStats as DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get dashboard statistics",
    description="Získanie štatistík pre užívateľa"
)
async def get_dashboard_stats(
    current_user = Depends(get_current_user)
):
    """Získanie štatistík pre dashboard"""
    stats = DashboardService.get_user_stats(current_user.id)
    health = DashboardService.get_system_health()
    
    return {
        "user_stats": stats,
        "system_health": health,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get(
    "/activities",
    response_model=RecentActivities,
    summary="Get recent activities",
    description="Získanie posledných aktivít užívateľa"
)
async def get_recent_activities(
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    """Získanie posledných aktivít"""
    activities = DashboardService.get_recent_activities(current_user.id, limit)
    
    return {
        "activities": activities,
        "count": len(activities)
    }

@router.get(
    "/health",
    response_model=SystemHealth,
    summary="System health check",
    description="Kontrola stavu systému a externých služieb"
)
async def get_system_health():
    """Kontrola stavu systému"""
    return DashboardService.get_system_health()
```

## 4. Error Handling

### 4.1 Custom error responses
```python
# app/errors.py
from fastapi import HTTPException
from typing import Optional, Dict, Any

class APIError(HTTPException):
    """Base API error class"""
    
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": error,
                "message": message,
                "code": code,
                "details": details or {}
            }
        )

class ValidationError(APIError):
    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(
            status_code=400,
            error="Validation Error",
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )

class NotFoundError(APIError):
    def __init__(self, resource: str, resource_id: str = None):
        message = f"{resource} not found"
        details = {"resource": resource, "resource_id": resource_id} if resource_id else {"resource": resource}
        super().__init__(
            status_code=404,
            error="Not Found",
            message=message,
            code="NOT_FOUND",
            details=details
        )

class ConflictError(APIError):
    def __init__(self, message: str, resource: str = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            status_code=409,
            error="Conflict",
            message=message,
            code="CONFLICT",
            details=details
        )

class RateLimitError(APIError):
    def __init__(self, retry_after: int = None):
        message = "Rate limit exceeded"
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            status_code=429,
            error="Too Many Requests",
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            details=details
        )
```

### 4.2 Error handling middleware
```python
# app/middleware.py
from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .errors import APIError

async def error_handler_middleware(request: Request, call_next):
    """Global error handler middleware"""
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as e:
        return Response(
            status_code=400,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "code": "VALIDATION_ERROR",
                "details": e.errors()
            },
            media_type="application/json"
        )
    except StarletteHTTPException as e:
        # Preprocess known HTTP exceptions
        if e.status_code == 401:
            return Response(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid or missing authentication token",
                    "code": "UNAUTHORIZED"
                },
                media_type="application/json"
            )
        elif e.status_code == 403:
            return Response(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": "Insufficient permissions",
                    "code": "FORBIDDEN"
                },
                media_type="application/json"
            )
        else:
            return Response(
                status_code=e.status_code,
                content={
                    "error": "HTTP Error",
                    "message": e.detail,
                    "code": "HTTP_ERROR"
                },
                media_type="application/json"
            )
    except Exception as e:
        # Log the error
        import logging
        logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        return Response(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            },
            media_type="application/json"
        )
```

## 5. Examples & Usage

### 5.1 API usage examples
```python
# examples/api_usage.py
"""
Príklady použitia API Centrum Backend
"""

import requests
import json

BASE_URL = "https://api.api-centrum.sk"

# 1. Prihlásenie
def login(email: str, password: str):
    """Prihlásenie užívateľa"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Login failed: {response.json()}")
        return None

# 2. Vytvorenie domény
def create_domain(token: str, domain_name: str, description: str):
    """Vytvorenie novej domény"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/domains", json={
        "name": domain_name,
        "description": description
    }, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Domain creation failed: {response.json()}")
        return None

# 3. Generovanie SSL certifikátu
def generate_ssl(token: str, domain: str, email: str):
    """Generovanie SSL certifikátu"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/ssl/generate", json={
        "domain": domain,
        "email": email
    }, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"SSL generation failed: {response.json()}")
        return None

# 4. Získanie štatistík
def get_dashboard_stats(token: str):
    """Získanie štatistík"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get stats: {response.json()}")
        return None

# Príklad použitia
if __name__ == "__main__":
    # Prihlásenie
    auth_data = login("user@example.com", "password123")
    if auth_data:
        token = auth_data["access_token"]
        
        # Vytvorenie domény
        domain = create_domain(token, "example.com", "Test domain")
        if domain:
            print(f"Domain created: {domain['name']}")
            
            # Generovanie SSL
            ssl_cert = generate_ssl(token, domain["name"], "admin@example.com")
            if ssl_cert:
                print(f"SSL generated: {ssl_cert['status']}")
        
        # Získanie štatistík
        stats = get_dashboard_stats(token)
        if stats:
            print(f"User stats: {stats['user_stats']}")
```

### 5.2 cURL examples
```bash
# Prihlásenie
curl -X POST "https://api.api-centrum.sk/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Vytvorenie domény
curl -X POST "https://api.api-centrum.sk/api/domains" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example.com",
    "description": "Test domain"
  }'

# Získanie domén
curl -X GET "https://api.api-centrum.sk/api/domains" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Generovanie SSL certifikátu
curl -X POST "https://api.api-centrum.sk/api/ssl/generate" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "email": "admin@example.com"
  }'

# Získanie štatistík
curl -X GET "https://api.api-centrum.sk/api/dashboard/stats" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## 6. Testing Documentation

### 6.1 API testing examples
```python
# tests/test_api_documentation.py
"""
Testy pre overenie API dokumentácie a endpointov
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Testy pre API endpointov"""
    
    def test_openapi_schema(self):
        """Test OpenAPI schémy"""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert "components" in schema
    
    def test_api_docs_available(self):
        """Test dostupnosti API dokumentácie"""
        response = client.get("/api/docs")
        assert response.status_code == 200
        assert "Swagger UI" in response.text
    
    def test_redoc_available(self):
        """Test dostupnosti ReDoc dokumentácie"""
        response = client.get("/api/redoc")
        assert response.status_code == 200
        assert "ReDoc" in response.text
    
    def test_health_endpoint(self):
        """Test health check endpointu"""
        response = client.get("/api/dashboard/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "websupport_api" in data
        assert "database" in data
        assert "neon_auth_trial" in data
        assert "timestamp" in data

class TestAuthentication:
    """Testy pre autentifikáciu"""
    
    def test_login_endpoint_documentation(self):
        """Test dokumentácie login endpointu"""
        schema = client.get("/api/openapi.json").json()
        
        login_path = schema["paths"]["/api/auth/login"]
        assert "post" in login_path
        assert "summary" in login_path["post"]
        assert "description" in login_path["post"]
        assert "requestBody" in login_path["post"]
        assert "responses" in login_path["post"]
    
    def test_protected_endpoints(self):
        """Test chránených endpointov"""
        # Bez autentifikácie by mal vrátiť 401
        response = client.get("/api/domains")
        assert response.status_code == 401
        
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 401

class TestErrorResponses:
    """Testy pre error responses"""
    
    def test_404_response_format(self):
        """Test formátu 404 chyby"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "code" in data
    
    def test_validation_error_format(self):
        """Test formátu validation chyby"""
        response = client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "123"  # Príliš krátke
        })
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data

class TestRateLimiting:
    """Testy pre rate limiting"""
    
    def test_rate_limit_headers(self):
        """Test rate limit hlavičiek"""
        # Vykonajte viacero rýchlych requestov
        for i in range(5):
            response = client.get("/api/dashboard/health")
            assert response.status_code == 200
            
            # Overiť existenciu rate limit hlavičiek
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers
```

## 7. Implementation Steps

### 7.1 Week 1: Basic OpenAPI Setup
- [ ] Nastaviť základný OpenAPI config
- [ ] Pridať custom OpenAPI schému
- [ ] Nastaviť security schemes
- [ ] Pridať basic tags a servers

### 7.2 Week 2: Data Models
- [ ] Vytvoriť všetky Pydantic schémy
- [ ] Definovať relationships
- [ ] Pridať validation rules
- [ ] Vytvoriť example values

### 7.3 Week 3: Endpoint Documentation
- [ ] Dokumentovať authentication endpoints
- [ ] Dokumentovať domain endpoints
- [ ] Dokumentovať SSL endpoints
- [ ] Dokumentovať dashboard endpoints

### 7.4 Week 4: Error Handling
- [ ] Vytvoriť custom error classes
- [ ] Nastaviť error handling middleware
- [ ] Definovať error responses
- [ ] Pridať error examples

### 7.5 Week 5: Examples & Testing
- [ ] Vytvoriť API usage examples
- [ ] Pridať cURL examples
- [ ] Vytvoriť testy pre dokumentáciu
- [ ] Overiť interaktívnu dokumentáciu

### 7.6 Week 6: Polish & Deployment
- [ ] Overiť všetky endpointy
- [ ] Testovať v rôznych prostredia
- [ ] Optimalizovať dokumentáciu
- [ ] Pridať deployment guide

## 8. Best Practices

### 8.1 Documentation best practices
- **Consistent formatting**: Používať rovnaký formát pre všetky endpointy
- **Clear descriptions**: Každý endpoint by mal mať jasný popis
- **Examples**: Vždy poskytnúť príklady request/response
- **Error documentation**: Dokumentovať všetky možné error stavy
- **Versioning**: Plánovať API versioning pre budúce zmeny

### 8.2 API design best practices
- **RESTful conventions**: Dodržiavať REST princípy
- **Consistent naming**: Používať konzistentné pomenovanie
- **Proper HTTP codes**: Používať správne HTTP status kódy
- **Pagination**: Implementovať pagination pre zoznamy
- **Filtering**: Podpora pre filterovanie a vyhľadávanie

### 8.3 Security best practices
- **Authentication**: Vždy overovať autentifikáciu
- **Authorization**: Kontrolovať oprávnenia
- **Input validation**: Validovať všetky vstupy
- **Rate limiting**: Ochrana proti nadmernému používaniu
- **Error handling**: Neprezrádzať citlivé informácie v chybách

Tento blueprint poskytuje komplexný návod na vytvorenie profesionálnej API dokumentácie pre API Centrum Backend systém.