# API Centrum Backend

## Prehľad

Backend systém pre API Centrum - Domain & SSL Manager s integráciou Neon Auth.

### Architektúra

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── db.py              # Database setup
│   ├── models.py          # SQLAlchemy models
│   ├── crud.py            # Database operations
│   ├── auth_local.py      # Local JWT authentication
│   ├── auth_neon.py       # Neon Auth integration
│   ├── auth_composite.py  # Hybrid authentication
│   ├── auth_endpoints.py  # Authentication endpoints
│   ├── websupport.py      # Websupport API integration
│   ├── dashboard.py       # Dashboard statistics
│   ├── domains/           # Domain management
│   ├── ssl/              # SSL certificate management
│   ├── users/            # User management
│   └── monitoring/       # System monitoring
├── requirements.txt       # Python dependencies
├── Dockerfile           # Container configuration
└── alembic/            # Database migrations
```

### Funkcie

#### Autentifikácia
- **Neon Auth Integration**: Trial period authentication
- **Local JWT Auth**: Independent authentication system
- **Hybrid Auth**: Seamless fallback between systems
- **Migration Support**: Move users between auth systems

#### Domény
- Správa domén cez Websupport API
- CRUD operácie (Create, Read, Update, Delete)
- Autentifikované endpointy

#### SSL Certifikáty
- Generovanie SSL certifikátov
- Integrácia s Let's Encrypt
- Certifikátové endpointy

#### Dashboard
- Štatistiky a monitorovanie
- System health checks
- Užívateľské aktivity

### Inštalácia

1. Nainštaluj závislosti:
```bash
pip install -r requirements.txt
```

2. Nastav premenné prostredia:
```bash
cp .env.example .env
# Uprav .env súbory podľa potreby
```

3. Spusti migrácie:
```bash
alembic upgrade head
```

4. Spusti server:
```bash
uvicorn app.main:app --reload
```

### Premenné prostredia

```env
# Websupport API
WEBSUPPORT_API_KEY=your_api_key
WEBSUPPORT_SECRET=your_secret

# Database
DATABASE_URL=postgresql://user:password@host:port/db

# JWT
JWT_SECRET=your_jwt_secret
JWT_EXPIRE_MINUTES=1440

# SSL
CERTBOT_EMAIL=admin@example.com

# Environment
ENV=development
```

### API Endpoints

#### Autentifikácia
- `POST /api/auth/login` - Local login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/status` - Auth system status

#### Domény
- `GET /api/domains` - List domains
- `POST /api/domains` - Create domain
- `GET /api/domains/{id}` - Get domain details
- `DELETE /api/domains/{id}` - Delete domain

#### SSL
- `POST /api/ssl/generate` - Generate SSL certificate

#### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/activities` - Recent activities
- `GET /api/dashboard/health` - System health

### Neon Auth Integration

Systém podporuje trial period Neon Auth s nasledujúcimi výhodami:

1. **Enterprise Authentication**: Google OAuth, SSO
2. **Professional Email**: Authenticated email notifications
3. **User Management**: Professional user lifecycle
4. **Fallback System**: Automatic fallback to local auth

### Migrácia

Systém umožňuje migráciu medzi autentifikačnými systémami:

1. **Neon to Local**: Migrate Neon Auth users to local auth
2. **Status Check**: Monitor auth system availability
3. **Seamless Transition**: No user data loss

### Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

### Monitoring

- System health checks
- API response times
- Database connectivity
- Neon Auth trial status

### Bezpečnosť

- JWT token authentication
- Password hashing (bcrypt)
- HTTPS enforcement in production
- Rate limiting (planned)
- Audit logging

### Vývoj

1. **Code Style**: Follow PEP 8
2. **Testing**: Write tests for new features
3. **Documentation**: Update docs for new endpoints
4. **Migration**: Create Alembic migrations for DB changes

### Licencia

API Centrum Backend - Domain & SSL Manager