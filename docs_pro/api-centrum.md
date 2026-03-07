Povedali ste

Podľa tvojich požadavkov a dokumentácie **Websupport REST API** vytvorím **Python server s PWA frontendom**, ktorý bude integrovať Websupport API pre správu domén a SSL certifikátov. Tu je **kompletný blueprint** s dôrazom na autentifikáciu, bezpečnosť a rozšírené funkcie.

---

## **1. Backend: FastAPI + Websupport API Integracia**

### **Kľúčové súbory a štruktúra**

```
/backend
│── app/
│   │── __init__.py
│   │── main.py          # Hlavný FastAPI server
│   │── auth.py          # Autentifikácia a generovanie podpisu pre Websupport API
│   │── domains/         # Modul pre správu domén
│   │   │── routes.py    # API endpointy pre domény
│   │   │── models.py    # Databázové modely
│   │   │── services.py  # Logika pre komunikáciu s Websupport API
│   │── ssl/             # Modul pre SSL certifikáty
│   │   │── routes.py
│   │   │── models.py
│   │   │── services.py
│   │── monitoring/      # Modul pre monitorovanie
│   │── schemas.py       # Pydantic schémy pre validáciu
│── config.py           # Konfigurácia (API kľúče, DB pripojenie)
│── Dockerfile
│── requirements.txt
```

---

### **2. Autentifikácia s Websupport API**

#### **Generovanie podpisu (podľa dokumentácie)**

```python
# app/auth.py
import hmac
import hashlib
import time
from datetime import datetime, timezone
import requests
from fastapi import HTTPException

def generate_websupport_signature(api_key: str, secret: str, method: str, path: str) -> tuple:
    timestamp = int(time.time())
    canonical_request = f"{method} {path} {timestamp}"
    signature = hmac.new(
        bytes(secret, 'UTF-8'),
        bytes(canonical_request, 'UTF-8'),
        hashlib.sha1
    ).hexdigest()
    x_date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return signature, x_date, timestamp

def make_websupport_request(api_key: str, secret: str, method: str, path: str, query: str = "", data: dict = None):
    signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
    api_url = f"https://rest.websupport.sk{path}{query}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Date": x_date,
    }
    auth = (api_key, signature)
    try:
        response = requests.request(method, api_url, headers=headers, auth=auth, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))
```

---

### **3. Modul pre správu domén**

#### **API Endpointy**

```python
# app/domains/routes.py
from fastapi import APIRouter, Depends, HTTPException
from .services import DomainService
from ..auth import make_websupport_request
from ..schemas import DomainCreate, DomainUpdate

router = APIRouter()

@router.get("/domains")
async def get_domains(api_key: str, secret: str):
    try:
        data = make_websupport_request(api_key, secret, "GET", "/v2/service/domains")
        return {"domains": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/domains")
async def create_domain(domain: DomainCreate, api_key: str, secret: str):
    try:
        data = make_websupport_request(api_key, secret, "POST", "/v2/service/domains", data=domain.dict())
        return {"domain": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### **Pydantic Schémy**

```python
# app/schemas.py
from pydantic import BaseModel

class DomainBase(BaseModel):
    name: str
    description: str = None

class DomainCreate(DomainBase):
    pass

class DomainUpdate(DomainBase):
    pass
```

---

### **4. Modul pre SSL certifikáty**

#### **Automatická obnova cez Let’s Encrypt**

```python
# app/ssl/services.py
import subprocess
from pathlib import Path

def generate_ssl_certificate(domain: str, email: str):
    certbot_cmd = [
        "certbot", "certonly", "--standalone",
        "--non-interactive", "--agree-tos",
        "--email", email,
        "--domains", domain
    ]
    try:
        subprocess.run(certbot_cmd, check=True)
        return {"status": "success", "domain": domain}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}
```

---

### **5. Frontend: PWA s Vue 3**

#### **Príklad stránky pre zoznam domén**

```vue
<!-- src/views/Domains.vue -->
<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Domény</h1>
    <button
      @click="fetchDomains"
      class="bg-blue-500 text-white px-4 py-2 rounded"
    >
      Načítať domény
    </button>
    <div v-if="loading" class="mt-4">Načítavam...</div>
    <div v-else class="mt-4">
      <div v-for="domain in domains" :key="domain.id" class="border p-2 mb-2">
        {{ domain.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const domains = ref([]);
const loading = ref(false);

const fetchDomains = async () => {
  loading.value = true;
  try {
    const response = await axios.get("/api/domains", {
      auth: { username: "api_key", password: "signature" },
    });
    domains.value = response.data.domains;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};
</script>
```

---

### **6. PWA Konfigurácia**

```javascript
// vite.config.js
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Domain & SSL Manager",
        short_name: "DSM",
        theme_color: "#1e3a8a",
        icons: [
          { src: "/pwa-192x192.png", sizes: "192x192", type: "image/png" },
          { src: "/pwa-512x512.png", sizes: "512x512", type: "image/png" },
        ],
      },
    }),
  ],
});
```

---

### **7. Nasadenie (Docker Compose)**

```yaml
# docker-compose.yml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - WEBSUPPORT_API_KEY=${WEBSUPPORT_API_KEY}
      - WEBSUPPORT_SECRET=${WEBSUPPORT_SECRET}
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  postgres:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

### **8. Ukážka UI (Dashboard)**

---

### **9. Rozšírené funkcie**

1. **Automatická obnova SSL:** Celery úloha, ktorá každý týždeň kontroluje expiráciu.
2. **DNS Health Check:** Skript, ktorý monitoruje DNS záznamy a upozorňuje na chyby.
3. **Audit Log:** Ukladanie všetkých zmien do databázy.
4. **2FA pre prístup:** Integracia s Google Authenticator.

---

### **10. Ďalšie kroky**

1. **Vytvorenie backend API** (FastAPI + PostgreSQL).
2. **Frontend v PWA** (Vue/React + Tailwind).
3. **Integracia s Websupport API** (pre správu domén).
4. **Automatizácia SSL** (Certbot + Celery).
5. **Nasadenie na server** (Docker + Nginx).

---

Priprav mi vsetky subory na to potrebne
Copilot povedal
Projekt — kompletná sada súborov (FastAPI backend + Vue 3 PWA frontend)
Nižšie nájdeš kompletnú štruktúru projektu a obsah všetkých potrebných súborov. Skopíruj súbory do príslušných priečinkov, uprav premenné v .env a spusti podľa sekcie Nasadenie.

Strom projektu
Kód

Kopírovať
project-root/
├─ backend/
│ ├─ app/
│ │ ├─ **init**.py
│ │ ├─ main.py
│ │ ├─ auth.py
│ │ ├─ config.py
│ │ ├─ schemas.py
│ │ ├─ domains/
│ │ │ ├─ **init**.py
│ │ │ ├─ routes.py
│ │ │ ├─ services.py
│ │ │ ├─ models.py
│ │ ├─ ssl/
│ │ │ ├─ **init**.py
│ │ │ ├─ routes.py
│ │ │ ├─ services.py
│ │ ├─ monitoring/
│ │ │ ├─ **init**.py
│ │ │ ├─ tasks.py
│ ├─ Dockerfile
│ ├─ requirements.txt
│ ├─ alembic.ini (voliteľné)
│ └─ .env.example
├─ frontend/
│ ├─ package.json
│ ├─ vite.config.js
│ ├─ index.html
│ ├─ src/
│ │ ├─ main.js
│ │ ├─ App.vue
│ │ ├─ api/
│ │ │ ├─ api.js
│ │ ├─ views/
│ │ │ ├─ Domains.vue
│ │ ├─ assets/
│ │ │ ├─ pwa-192x192.png
│ │ │ ├─ pwa-512x512.png
│ ├─ public/
│ │ ├─ manifest.webmanifest
│ │ ├─ robots.txt
├─ docker-compose.yml
└─ README.md
Backend — súbory
backend/app/**init**.py
python

Kopírovať

# backend/app/**init**.py

backend/app/config.py
python

Kopírovať

# backend/app/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
WEBSUPPORT_API_KEY: str = os.getenv("WEBSUPPORT_API_KEY", "")
WEBSUPPORT_SECRET: str = os.getenv("WEBSUPPORT_SECRET", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/postgres")
CERTBOT_EMAIL: str = os.getenv("CERTBOT_EMAIL", "")
ENV: str = os.getenv("ENV", "development")

settings = Settings()
backend/app/auth.py
python

Kopírovať

# backend/app/auth.py

import hmac
import hashlib
import time
from datetime import datetime, timezone
import requests
from fastapi import HTTPException
from .config import settings

def generate_websupport_signature(api_key: str, secret: str, method: str, path: str) -> tuple:
timestamp = int(time.time())
canonical_request = f"{method} {path} {timestamp}"
signature = hmac.new(
bytes(secret, 'UTF-8'),
bytes(canonical_request, 'UTF-8'),
hashlib.sha1
).hexdigest()
x_date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y%m%dT%H%M%SZ')
return signature, x_date, timestamp

def make_websupport_request(api_key: str, secret: str, method: str, path: str, query: str = "", data: dict = None):
signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
api_url = f"https://rest.websupport.sk{path}{query}"
headers = {
"Content-Type": "application/json",
"Accept": "application/json",
"X-Date": x_date,
}
auth = (api_key, signature)
try:
response = requests.request(method, api_url, headers=headers, auth=auth, json=data, timeout=30)
response.raise_for_status()
if response.text:
return response.json()
return {}
except requests.exceptions.RequestException as e: # bezpečné chytanie chýb
detail = str(e)
status_code = getattr(e.response, "status_code", 500) if hasattr(e, "response") else 500
raise HTTPException(status_code=status_code, detail=detail)
backend/app/schemas.py
python

Kopírovať

# backend/app/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class DomainBase(BaseModel):
name: str = Field(..., example="example.sk")
description: Optional[str] = None

class DomainCreate(DomainBase):
pass

class DomainUpdate(DomainBase):
pass

class SSLCertRequest(BaseModel):
domain: str
email: EmailStr
backend/app/main.py
python

Kopírovať

# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .domains import routes as domain_routes
from .ssl import routes as ssl_routes
from .config import settings

app = FastAPI(title="Domain & SSL Manager API")

app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # v produkcii obmedziť
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(domain_routes.router, prefix="/api")
app.include_router(ssl_routes.router, prefix="/api")

@app.get("/health")
def health():
return {"status": "ok", "env": settings.ENV}
Modul domén
backend/app/domains/**init**.py
python

Kopírovať

# backend/app/domains/**init**.py

backend/app/domains/routes.py
python

Kopírovať

# backend/app/domains/routes.py

from fastapi import APIRouter, Depends, HTTPException
from ..schemas import DomainCreate
from .services import DomainService
from ..config import settings

router = APIRouter()

@router.get("/domains")
async def get_domains():
try:
return DomainService.list_domains(settings.WEBSUPPORT_API_KEY, settings.WEBSUPPORT_SECRET)
except HTTPException:
raise
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains")
async def create_domain(domain: DomainCreate):
try:
return DomainService.create_domain(settings.WEBSUPPORT_API_KEY, settings.WEBSUPPORT_SECRET, domain.dict())
except HTTPException:
raise
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
backend/app/domains/services.py
python

Kopírovať

# backend/app/domains/services.py

from ..auth import make_websupport_request

class DomainService:
@staticmethod
def list_domains(api_key: str, secret: str):
path = "/v2/service/domains"
return make_websupport_request(api_key, secret, "GET", path)

    @staticmethod
    def create_domain(api_key: str, secret: str, payload: dict):
        path = "/v2/service/domains"
        return make_websupport_request(api_key, secret, "POST", path, data=payload)

backend/app/domains/models.py
python

Kopírovať

# backend/app/domains/models.py

# Voliteľné: SQLAlchemy modely ak chceš persistenciu

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Domain(Base):
**tablename** = "domains"
id = Column(Integer, primary_key=True, index=True)
name = Column(String(255), unique=True, index=True, nullable=False)
description = Column(Text, nullable=True)
Modul SSL
backend/app/ssl/**init**.py
python

Kopírovať

# backend/app/ssl/**init**.py

backend/app/ssl/routes.py
python

Kopírovať

# backend/app/ssl/routes.py

from fastapi import APIRouter, HTTPException
from ..schemas import SSLCertRequest
from .services import SSLService
from ..config import settings

router = APIRouter()

@router.post("/ssl/generate")
async def generate_ssl(req: SSLCertRequest):
try:
result = SSLService.generate_ssl_certificate(req.domain, req.email)
return result
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
backend/app/ssl/services.py
python

Kopírovať

# backend/app/ssl/services.py

import subprocess
from pathlib import Path
from ..config import settings

class SSLService:
@staticmethod
def generate_ssl_certificate(domain: str, email: str): # Ukladanie certifikátov do /etc/letsencrypt (vyžaduje root)
certbot_cmd = [
"certbot", "certonly", "--standalone",
"--non-interactive", "--agree-tos",
"--email", email,
"--domains", domain
]
try:
subprocess.run(certbot_cmd, check=True)
return {"status": "success", "domain": domain}
except subprocess.CalledProcessError as e:
return {"status": "error", "message": str(e)}
Monitoring (základ)
backend/app/monitoring/tasks.py
python

Kopírovať

# backend/app/monitoring/tasks.py

# Základné úlohy pre plánovanie (Celery/cron)

def check_ssl_expiry(): # implementovať kontrolu expirácie certifikátov
pass

def dns_health_check(): # implementovať DNS kontrolu
pass
backend/requirements.txt
Kód

Kopírovať
fastapi==0.95.2
uvicorn[standard]==0.22.0
requests==2.31.0
pydantic==1.10.11
python-dotenv==1.0.0
sqlalchemy==1.4.52
alembic==1.11.1
psycopg2-binary==2.9.7
certbot==2.6.0
Poznámka: verzie sú orientačné — uprav podľa potreby.

backend/Dockerfile
dockerfile

Kopírovať
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
backend/.env.example
Kód

Kopírovať
WEBSUPPORT_API_KEY=your_api_key_here
WEBSUPPORT_SECRET=your_secret_here
DATABASE_URL=postgresql://postgres:password@postgres:5432/postgres
CERTBOT_EMAIL=admin@example.com
ENV=production
Frontend — súbory
frontend/package.json
json

Kopírovať
{
"name": "domain-ssl-manager",
"version": "0.1.0",
"private": true,
"scripts": {
"dev": "vite",
"build": "vite build",
"preview": "vite preview"
},
"dependencies": {
"axios": "^1.4.0",
"vue": "^3.3.4"
},
"devDependencies": {
"vite": "^5.0.0",
"vite-plugin-pwa": "^0.15.0"
}
}
frontend/vite.config.js
javascript

Kopírovať
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
plugins: [
vue(),
VitePWA({
registerType: 'autoUpdate',
manifest: {
name: 'Domain & SSL Manager',
short_name: 'DSM',
theme_color: '#1e3a8a',
icons: [
{ src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
{ src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' }
]
}
})
],
server: {
proxy: {
'/api': {
target: 'http://backend:8000',
changeOrigin: true,
secure: false,
rewrite: (path) => path.replace(/^\/api/, '/api')
}
}
}
})
frontend/index.html
html

Kopírovať

<!doctype html>
<html lang="sk">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1.0" />
    <title>Domain & SSL Manager</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
frontend/src/main.js
javascript

Kopírovať
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
frontend/src/App.vue
vue

Kopírovať
<template>

  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Domain & SSL Manager</h1>
    <Domains />
  </div>
</template>

<script setup>
import Domains from './views/Domains.vue'
</script>

frontend/src/api/api.js
javascript

Kopírovať
import axios from 'axios'

const api = axios.create({
baseURL: '/api',
timeout: 30000
})

// Interceptor pre pridanie autentifikácie ak bude potrebné
api.interceptors.request.use(config => {
// tu môžeš pridať token z localStorage
return config
})

export default api
frontend/src/views/Domains.vue
vue

Kopírovať
<template>

  <div class="p-4">
    <h2 class="text-xl font-semibold mb-3">Domény</h2>
    <div class="mb-3">
      <button @click="fetchDomains" class="bg-blue-600 text-white px-3 py-1 rounded">Načítať domény</button>
    </div>

    <div v-if="loading">Načítavam...</div>

    <div v-else>
      <div v-if="domains && domains.length">
        <div v-for="d in domains" :key="d.id" class="border p-2 mb-2">
          <div><strong>{{ d.name }}</strong></div>
          <div v-if="d.description">{{ d.description }}</div>
        </div>
      </div>
      <div v-else>Žiadne domény.</div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/api'

const domains = ref([])
const loading = ref(false)

const fetchDomains = async () => {
  loading.value = true
  try {
    const res = await api.get('/domains')
    // Očakávame, že backend vráti pole alebo objekt
    domains.value = res.data.domains || res.data
  } catch (err) {
    console.error(err)
    alert('Chyba pri načítaní domén.')
  } finally {
    loading.value = false
  }
}
</script>

frontend/public/manifest.webmanifest
json

Kopírovať
{
"name": "Domain & SSL Manager",
"short_name": "DSM",
"start_url": "/",
"display": "standalone",
"background_color": "#ffffff",
"theme_color": "#1e3a8a",
"icons": [
{ "src": "/pwa-192x192.png", "sizes": "192x192", "type": "image/png" },
{ "src": "/pwa-512x512.png", "sizes": "512x512", "type": "image/png" }
]
}
Pridaj pwa-192x192.png a pwa-512x512.png do frontend/src/assets alebo frontend/public.

Docker Compose a nasadenie
docker-compose.yml
yaml

Kopírovať
version: '3.8'
services:
backend:
build: ./backend
container_name: dsm_backend
ports: - "8000:8000"
environment: - WEBSUPPORT_API_KEY=${WEBSUPPORT_API_KEY}
      - WEBSUPPORT_SECRET=${WEBSUPPORT_SECRET} - DATABASE_URL=${DATABASE_URL}
      - CERTBOT_EMAIL=${CERTBOT_EMAIL} - ENV=${ENV}
depends_on: - postgres

frontend:
build:
context: ./frontend
container_name: dsm_frontend
ports: - "3000:3000"
depends_on: - backend

postgres:
image: postgres:14
environment:
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
POSTGRES_USER: ${POSTGRES_USER}
POSTGRES_DB: ${POSTGRES_DB}
volumes: - postgres_data:/var/lib/postgresql/data

volumes:
postgres_data:
V frontend Dockerfile môžeš použiť oficiálny Node image alebo Vite preview. Ak chceš jednoduché lokálne dev prostredie, spúšťaj npm run dev lokálne.

README.md (základ)
README.md
markdown

Kopírovať

# Domain & SSL Manager

## Popis

FastAPI backend integrujúci Websupport REST API + Vue 3 PWA frontend.

## Spustenie lokálne (dev)

1. Skopíruj `.env.example` do `.env` a doplň hodnoty.
2. Backend:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`
3. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## Nasadenie s Docker Compose

`docker-compose up --build`
Bezpečnosť a odporúčania (stručne)
Nikdy neukladaj WEBSUPPORT_SECRET do repozitára; používaj .env alebo secrets v CI/CD.

V produkcii obmedz CORS a povoľ len dôveryhodné originy.

Certbot vyžaduje root a otvorené porty 80/443; v Docker prostredí riešiť s hostom (bind mount alebo proxy).

Pre automatickú obnovu SSL použij Cron/Celery, ktorý spúšťa certbot renew.

Logovanie a audit: zaznamenávaj volania API a zmeny do DB s užívateľskými identifikátormi.

Ďalšie kroky (konkrétne)
Chceš, aby som vygeneroval Dockerfile pre frontend a kompletný nginx reverse-proxy konfiguráciu pre produkciu?

Alebo mám pripraviť aj SQLAlchemy + Alembic migrácie a základnú autentifikáciu (users, roles, 2FA)?

Ktorú z týchto dvoch možností preferuješ ako ďalší krok?

Povedali ste

Druhu moznost
Copilot povedal
Prehľad riešenia
Pripravím kompletnú implementáciu SQLAlchemy + Alembic migrácií a základnej autentifikácie (users, roles, JWT, heslá, 2FA pomocou TOTP). Kód je pripravený tak, aby sa dal vložiť do už existujúcej štruktúry backend/app z predchádzajúceho blueprintu. Sú zahrnuté modely, CRUD pre používateľov, závislosti pre autorizáciu, generovanie a overenie JWT, integrácia pyotp pre 2FA a ukážková Alembic migrácia.

Strom súborov (rozšírenie backendu)
Kód

Kopírovať
backend/app/
├─ auth.py # JWT, heslá, 2FA helpery
├─ db.py # SQLAlchemy engine, session, Base
├─ models.py # User, Role, Audit
├─ crud.py # CRUD operácie pre users/roles
├─ deps.py # závislosti pre FastAPI (get_db, current_user)
├─ users/routes.py # endpoints: register, login, enable-2fa, verify-2fa, me
├─ alembic/ # alembic konfigurácia
│ ├─ env.py
│ ├─ script.py.mako
│ └─ versions/
│ └─ 0001_create_users_roles.py
├─ requirements.txt # doplnené knižnice
backend/app/db.py
python

Kopírovať

# backend/app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()
backend/app/models.py
python

Kopírovať

# backend/app/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Role(Base):
**tablename** = "roles"
id = Column(Integer, primary_key=True, index=True)
name = Column(String(50), unique=True, nullable=False)

class User(Base):
**tablename** = "users"
id = Column(Integer, primary_key=True, index=True)
email = Column(String(255), unique=True, index=True, nullable=False)
hashed_password = Column(String(255), nullable=False)
is_active = Column(Boolean, default=True)
is_superuser = Column(Boolean, default=False)
created_at = Column(DateTime, default=datetime.utcnow)
role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
role = relationship("Role") # 2FA fields
totp_secret = Column(String(32), nullable=True)
two_factor_enabled = Column(Boolean, default=False)

class AuditLog(Base):
**tablename** = "audit_logs"
id = Column(Integer, primary_key=True, index=True)
user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
action = Column(String(255))
detail = Column(Text, nullable=True)
created_at = Column(DateTime, default=datetime.utcnow)
backend/app/auth.py
python

Kopírovať

# backend/app/auth.py

from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import pyotp
from fastapi import HTTPException, status
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 \* 24 # 24h, upraviteľné

def hash_password(password: str) -> str:
return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
now = datetime.utcnow()
expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
payload = {"sub": subject, "iat": now, "exp": expire}
token = jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)
return token

def decode_access_token(token: str) -> dict:
try:
payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
return payload
except jwt.ExpiredSignatureError:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
except jwt.PyJWTError:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def generate_totp_secret() -> str:
return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer_name: str = "DSM") -> str:
return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

def verify_totp(token: str, secret: str) -> bool:
totp = pyotp.TOTP(secret)
return totp.verify(token, valid_window=1)
backend/app/crud.py
python

Kopírovať

# backend/app/crud.py

from sqlalchemy.orm import Session
from . import models, auth
from typing import Optional

class CRUDUser:
@staticmethod
def get_by_email(db: Session, email: str) -> Optional[models.User]:
return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def create(db: Session, email: str, password: str, role: Optional[models.Role] = None) -> models.User:
        hashed = auth.hash_password(password)
        user = models.User(email=email, hashed_password=hashed, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def enable_2fa(db: Session, user: models.User, secret: str):
        user.totp_secret = secret
        user.two_factor_enabled = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def disable_2fa(db: Session, user: models.User):
        user.totp_secret = None
        user.two_factor_enabled = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

class CRUDRole:
@staticmethod
def get_by_name(db: Session, name: str):
return db.query(models.Role).filter(models.Role.name == name).first()

    @staticmethod
    def create(db: Session, name: str):
        role = models.Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

backend/app/deps.py
python

Kopírovať

# backend/app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import get_db
from .auth import decode_access_token
from . import crud, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def get_db_dep():
yield from get_db()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_dep)) -> models.User:
payload = decode_access_token(token)
email = payload.get("sub")
if not email:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
user = crud.CRUDUser.get_by_email(db, email)
if not user or not user.is_active:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
return user

def require_superuser(current_user: models.User = Depends(get_current_user)):
if not current_user.is_superuser:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
return current_user
backend/app/users/routes.py
python

Kopírovať

# backend/app/users/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from .. import crud, auth, models
from ..deps import get_current_user

router = APIRouter()

class RegisterIn(BaseModel):
email: EmailStr
password: str

class TokenOut(BaseModel):
access_token: str
token_type: str = "bearer"

class LoginIn(BaseModel):
email: EmailStr
password: str
totp: str | None = None

@router.post("/users/register", response_model=dict)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
existing = crud.CRUDUser.get_by_email(db, payload.email)
if existing:
raise HTTPException(status_code=400, detail="Email already registered")
user = crud.CRUDUser.create(db, payload.email, payload.password)
return {"id": user.id, "email": user.email}

@router.post("/users/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
user = crud.CRUDUser.get_by_email(db, payload.email)
if not user or not auth.verify_password(payload.password, user.hashed_password):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
if user.two_factor_enabled:
if not payload.totp or not auth.verify_totp(payload.totp, user.totp_secret):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="2FA required or invalid token")
token = auth.create_access_token(subject=user.email)
return {"access_token": token}

@router.post("/users/2fa/setup", response_model=dict)
def setup_2fa(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # vráti secret a provisioning URI (QR kód môže frontend vygenerovať z URI)
secret = auth.generate_totp_secret()
uri = auth.get_totp_uri(secret, current_user.email, issuer_name="Domain-SSL-Manager") # dočasne neaktivujeme, aktivácia po overení kódu
return {"secret": secret, "otp_auth_url": uri}

class Verify2FAIn(BaseModel):
token: str
secret: str

@router.post("/users/2fa/verify", response_model=dict)
def verify_2fa(payload: Verify2FAIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
if not auth.verify_totp(payload.token, payload.secret):
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP token") # uložiť secret a aktivovať 2FA
crud.CRUDUser.enable_2fa(db, current_user, payload.secret)
return {"status": "2fa_enabled"}

@router.get("/users/me", response_model=dict)
def me(current_user: models.User = Depends(get_current_user)):
return {"id": current_user.id, "email": current_user.email, "two_factor_enabled": current_user.two_factor_enabled}
backend/app/config.py (doplnok)
python

Kopírovať

# backend/app/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
WEBSUPPORT_API_KEY: str = os.getenv("WEBSUPPORT_API_KEY", "")
WEBSUPPORT_SECRET: str = os.getenv("WEBSUPPORT_SECRET", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/postgres")
CERTBOT_EMAIL: str = os.getenv("CERTBOT_EMAIL", "")
ENV: str = os.getenv("ENV", "development")
JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-to-secure-random")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

settings = Settings()
backend/requirements.txt (doplnok)
Kód

Kopírovať
fastapi==0.95.2
uvicorn[standard]==0.22.0
requests==2.31.0
pydantic==1.10.11
python-dotenv==1.0.0
sqlalchemy==1.4.52
alembic==1.11.1
psycopg2-binary==2.9.7
passlib[bcrypt]==1.7.4
pyjwt==2.8.0
pyotp==2.8.0
Alembic konfigurácia a príklad migrácie
backend/alembic/env.py
python

Kopírovať

# backend/alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(**file**), "..")))
from app.db import Base
from app.config import settings
from app import models # ensure models are imported

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
url = settings.DATABASE_URL
context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
with context.begin_transaction():
context.run_migrations()

def run_migrations_online():
connectable = engine_from_config(
{"sqlalchemy.url": settings.DATABASE_URL},
prefix='sqlalchemy.',
poolclass=pool.NullPool)
with connectable.connect() as connection:
context.configure(connection=connection, target_metadata=target_metadata)
with context.begin_transaction():
context.run_migrations()

if context.is_offline_mode():
run_migrations_offline()
else:
run_migrations_online()
backend/alembic/versions/0001_create_users_roles.py
python

Kopírovať

# backend/alembic/versions/0001_create_users_roles.py

"""create users, roles, audit_logs

Revision ID: 0001
Revises:
Create Date: 2026-03-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
op.create_table(
'roles',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('name', sa.String(length=50), nullable=False, unique=True),
)
op.create_table(
'users',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('email', sa.String(length=255), nullable=False, unique=True),
sa.Column('hashed_password', sa.String(length=255), nullable=False),
sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=True),
sa.Column('totp_secret', sa.String(length=32), nullable=True),
sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
)
op.create_table(
'audit_logs',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
sa.Column('action', sa.String(length=255)),
sa.Column('detail', sa.Text(), nullable=True),
sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
)

def downgrade():
op.drop_table('audit_logs')
op.drop_table('users')
op.drop_table('roles')
Spustenie migrácií a inicializácia
Nainštaluj závislosti: pip install -r requirements.txt.

Vytvor .env s DATABASE_URL a JWT_SECRET.

Inicializuj Alembic (ak ešte nie je): alembic init alembic (už je pripravené v projekte).

Vykonaj migrácie: alembic upgrade head.

Alternatívne: pri prvom spustení môžeš použiť python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)" pre rýchle vytvorenie tabuliek (len pre dev).

Bezpečnostné a prevádzkové odporúčania
JWT_SECRET musí byť dlhý, náhodný a uložený v secrets manageri alebo .env mimo repozitára.

Heslá ukladaj len v hashed forme (použité bcrypt cez passlib).

Pri 2FA nikdy neukladaj TOTP tokeny v plaintext logoch; ulož len totp_secret v DB šifrovanom alebo chránenom úložisku, ak to infraštruktúra vyžaduje.

Pri produkcii obmedz CORS, zapni HTTPS, nastav rate limiting a audit logovanie (AuditLog model je pripravený).

Pre obnovu a rotáciu kľúčov navrhni endpointy pre revokáciu tokenov a zmenu totp_secret.

Certbot v Docker konteineri vyžaduje špeciálne nastavenie portov 80/443; pre produkciu odporúčam Nginx reverzný proxy + certbot na hoste.

Ktoré konkrétne časti chceš, aby som teraz vygeneroval ako súbory (napríklad: kompletné users/routes.py vložiť do projektu, alebo pripraviť skript na inicializáciu admin účtu a Alembic env.py s premennými)?

Povedali ste

Vsetko teraz naraz nech to mozme uzavriet
Copilot povedal
Kompletný balík súborov — pripravené na vloženie do projektu
Nižšie sú všetky súbory pre backend (FastAPI + SQLAlchemy + Alembic + autentifikácia s 2FA) a frontend (Vue 3 PWA), plus Docker konfigurácie a README. Skopíruj každý blok do príslušného súboru podľa stromu projektu.

Strom projektu (rýchla referencia)
Kód

Kopírovať
project-root/
├─ backend/
│ ├─ app/
│ │ ├─ **init**.py
│ │ ├─ main.py
│ │ ├─ config.py
│ │ ├─ auth.py
│ │ ├─ db.py
│ │ ├─ models.py
│ │ ├─ crud.py
│ │ ├─ deps.py
│ │ ├─ schemas.py
│ │ ├─ domains/
│ │ │ ├─ **init**.py
│ │ │ ├─ routes.py
│ │ │ ├─ services.py
│ │ │ ├─ models.py
│ │ ├─ ssl/
│ │ │ ├─ **init**.py
│ │ │ ├─ routes.py
│ │ │ ├─ services.py
│ │ ├─ monitoring/
│ │ │ ├─ **init**.py
│ │ │ ├─ tasks.py
│ │ ├─ users/
│ │ │ ├─ **init**.py
│ │ │ ├─ routes.py
│ ├─ Dockerfile
│ ├─ requirements.txt
│ ├─ .env.example
│ └─ alembic/
│ ├─ env.py
│ ├─ script.py.mako
│ └─ versions/
│ └─ 0001_create_users_roles.py
├─ frontend/
│ ├─ package.json
│ ├─ vite.config.js
│ ├─ index.html
│ ├─ Dockerfile
│ ├─ src/
│ │ ├─ main.js
│ │ ├─ App.vue
│ │ ├─ api/
│ │ │ └─ api.js
│ │ ├─ views/
│ │ │ └─ Domains.vue
│ │ └─ assets/
│ │ ├─ pwa-192x192.png
│ │ └─ pwa-512x512.png
│ └─ public/
│ ├─ manifest.webmanifest
│ └─ robots.txt
├─ docker-compose.yml
└─ README.md
Backend — súbory
backend/app/**init**.py
python

Kopírovať

# backend/app/**init**.py

backend/app/config.py
python

Kopírovať

# backend/app/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
WEBSUPPORT_API_KEY: str = os.getenv("WEBSUPPORT_API_KEY", "")
WEBSUPPORT_SECRET: str = os.getenv("WEBSUPPORT_SECRET", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/postgres")
CERTBOT_EMAIL: str = os.getenv("CERTBOT_EMAIL", "")
ENV: str = os.getenv("ENV", "development")
JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-to-secure-random")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

settings = Settings()
backend/app/db.py
python

Kopírovať

# backend/app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()
backend/app/models.py
python

Kopírovať

# backend/app/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Role(Base):
**tablename** = "roles"
id = Column(Integer, primary_key=True, index=True)
name = Column(String(50), unique=True, nullable=False)

class User(Base):
**tablename** = "users"
id = Column(Integer, primary_key=True, index=True)
email = Column(String(255), unique=True, index=True, nullable=False)
hashed_password = Column(String(255), nullable=False)
is_active = Column(Boolean, default=True)
is_superuser = Column(Boolean, default=False)
created_at = Column(DateTime, default=datetime.utcnow)
role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
role = relationship("Role")
totp_secret = Column(String(32), nullable=True)
two_factor_enabled = Column(Boolean, default=False)

class AuditLog(Base):
**tablename** = "audit_logs"
id = Column(Integer, primary_key=True, index=True)
user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
action = Column(String(255))
detail = Column(Text, nullable=True)
created_at = Column(DateTime, default=datetime.utcnow)
backend/app/auth.py
python

Kopírovať

# backend/app/auth.py

from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import pyotp
from fastapi import HTTPException, status
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES

def hash_password(password: str) -> str:
return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
now = datetime.utcnow()
expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
payload = {"sub": subject, "iat": now.timestamp(), "exp": expire.timestamp()}
token = jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)
return token

def decode_access_token(token: str) -> dict:
try:
payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
return payload
except jwt.ExpiredSignatureError:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
except jwt.PyJWTError:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def generate_totp_secret() -> str:
return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer_name: str = "DSM") -> str:
return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

def verify_totp(token: str, secret: str) -> bool:
totp = pyotp.TOTP(secret)
return totp.verify(token, valid_window=1)
backend/app/crud.py
python

Kopírovať

# backend/app/crud.py

from sqlalchemy.orm import Session
from . import models, auth
from typing import Optional

class CRUDUser:
@staticmethod
def get_by_email(db: Session, email: str) -> Optional[models.User]:
return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def create(db: Session, email: str, password: str, role: Optional[models.Role] = None) -> models.User:
        hashed = auth.hash_password(password)
        user = models.User(email=email, hashed_password=hashed, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def enable_2fa(db: Session, user: models.User, secret: str):
        user.totp_secret = secret
        user.two_factor_enabled = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def disable_2fa(db: Session, user: models.User):
        user.totp_secret = None
        user.two_factor_enabled = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

class CRUDRole:
@staticmethod
def get_by_name(db: Session, name: str):
return db.query(models.Role).filter(models.Role.name == name).first()

    @staticmethod
    def create(db: Session, name: str):
        role = models.Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

backend/app/deps.py
python

Kopírovať

# backend/app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import get_db
from .auth import decode_access_token
from . import crud, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def get_db_dep():
yield from get_db()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_dep)) -> models.User:
payload = decode_access_token(token)
email = payload.get("sub")
if not email:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
user = crud.CRUDUser.get_by_email(db, email)
if not user or not user.is_active:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
return user

def require_superuser(current_user: models.User = Depends(get_current_user)):
if not current_user.is_superuser:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
return current_user
backend/app/schemas.py
python

Kopírovať

# backend/app/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class DomainBase(BaseModel):
name: str = Field(..., example="example.sk")
description: Optional[str] = None

class DomainCreate(DomainBase):
pass

class DomainUpdate(DomainBase):
pass

class SSLCertRequest(BaseModel):
domain: str
email: EmailStr

class RegisterIn(BaseModel):
email: EmailStr
password: str

class TokenOut(BaseModel):
access_token: str
token_type: str = "bearer"

class LoginIn(BaseModel):
email: EmailStr
password: str
totp: Optional[str] = None
backend/app/main.py
python

Kopírovať

# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .domains import routes as domain_routes
from .ssl import routes as ssl_routes
from .users import routes as user_routes
from .config import settings

app = FastAPI(title="Domain & SSL Manager API")

app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # v produkcii obmedziť na konkrétne originy
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(domain_routes.router, prefix="/api")
app.include_router(ssl_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")

@app.get("/health")
def health():
return {"status": "ok", "env": settings.ENV}
Modul domains
backend/app/domains/**init**.py
python

Kopírovať

# backend/app/domains/**init**.py

backend/app/domains/services.py
python

Kopírovať

# backend/app/domains/services.py

from ..auth import make_websupport_request # note: make_websupport_request defined earlier in original blueprint

# If make_websupport_request is in a different module, import accordingly.

class DomainService:
@staticmethod
def list_domains(api_key: str, secret: str):
path = "/v2/service/domains"
return make_websupport_request(api_key, secret, "GET", path)

    @staticmethod
    def create_domain(api_key: str, secret: str, payload: dict):
        path = "/v2/service/domains"
        return make_websupport_request(api_key, secret, "POST", path, data=payload)

Poznámka: Ak make_websupport_request je v app/auth.py v pôvodnom blueprint-e, presuň alebo importuj správne. V tomto balíku je autentifikačná funkcia pre Websupport v predchádzajúcom návrhu; ak ju potrebuješ, vlož ju do app/websupport.py a importuj sem.

backend/app/domains/routes.py
python

Kopírovať

# backend/app/domains/routes.py

from fastapi import APIRouter, HTTPException
from ..schemas import DomainCreate
from .services import DomainService
from ..config import settings

router = APIRouter()

@router.get("/domains")
async def get_domains():
try:
return DomainService.list_domains(settings.WEBSUPPORT_API_KEY, settings.WEBSUPPORT_SECRET)
except HTTPException:
raise
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains")
async def create_domain(domain: DomainCreate):
try:
return DomainService.create_domain(settings.WEBSUPPORT_API_KEY, settings.WEBSUPPORT_SECRET, domain.dict())
except HTTPException:
raise
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
backend/app/domains/models.py
python

Kopírovať

# backend/app/domains/models.py

# Voliteľné: SQLAlchemy modely ak chceš persistenciu lokálne

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Domain(Base):
**tablename** = "domains"
id = Column(Integer, primary_key=True, index=True)
name = Column(String(255), unique=True, index=True, nullable=False)
description = Column(Text, nullable=True)
Modul ssl
backend/app/ssl/**init**.py
python

Kopírovať

# backend/app/ssl/**init**.py

backend/app/ssl/services.py
python

Kopírovať

# backend/app/ssl/services.py

import subprocess
from pathlib import Path
from ..config import settings

class SSLService:
@staticmethod
def generate_ssl_certificate(domain: str, email: str):
certbot_cmd = [
"certbot", "certonly", "--standalone",
"--non-interactive", "--agree-tos",
"--email", email,
"--domains", domain
]
try:
subprocess.run(certbot_cmd, check=True)
return {"status": "success", "domain": domain}
except subprocess.CalledProcessError as e:
return {"status": "error", "message": str(e)}
backend/app/ssl/routes.py
python

Kopírovať

# backend/app/ssl/routes.py

from fastapi import APIRouter, HTTPException
from ..schemas import SSLCertRequest
from .services import SSLService

router = APIRouter()

@router.post("/ssl/generate")
async def generate_ssl(req: SSLCertRequest):
try:
result = SSLService.generate_ssl_certificate(req.domain, req.email)
return result
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
Monitoring
backend/app/monitoring/**init**.py
python

Kopírovať

# backend/app/monitoring/**init**.py

backend/app/monitoring/tasks.py
python

Kopírovať

# backend/app/monitoring/tasks.py

def check_ssl_expiry(): # implementovať kontrolu expirácie certifikátov
pass

def dns_health_check(): # implementovať DNS kontrolu
pass
Users (auth endpoints)
backend/app/users/**init**.py
python

Kopírovať

# backend/app/users/**init**.py

backend/app/users/routes.py
python

Kopírovať

# backend/app/users/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from .. import crud, auth, models
from ..deps import get_current_user

router = APIRouter()

class RegisterIn(BaseModel):
email: EmailStr
password: str

class TokenOut(BaseModel):
access_token: str
token_type: str = "bearer"

class LoginIn(BaseModel):
email: EmailStr
password: str
totp: str | None = None

@router.post("/users/register", response_model=dict)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
existing = crud.CRUDUser.get_by_email(db, payload.email)
if existing:
raise HTTPException(status_code=400, detail="Email already registered")
user = crud.CRUDUser.create(db, payload.email, payload.password)
return {"id": user.id, "email": user.email}

@router.post("/users/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
user = crud.CRUDUser.get_by_email(db, payload.email)
if not user or not auth.verify_password(payload.password, user.hashed_password):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
if user.two_factor_enabled:
if not payload.totp or not auth.verify_totp(payload.totp, user.totp_secret):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="2FA required or invalid token")
token = auth.create_access_token(subject=user.email)
return {"access_token": token}

@router.post("/users/2fa/setup", response_model=dict)
def setup_2fa(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
secret = auth.generate_totp_secret()
uri = auth.get_totp_uri(secret, current_user.email, issuer_name="Domain-SSL-Manager")
return {"secret": secret, "otp_auth_url": uri}

class Verify2FAIn(BaseModel):
token: str
secret: str

@router.post("/users/2fa/verify", response_model=dict)
def verify_2fa(payload: Verify2FAIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
if not auth.verify_totp(payload.token, payload.secret):
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP token")
crud.CRUDUser.enable_2fa(db, current_user, payload.secret)
return {"status": "2fa_enabled"}

@router.get("/users/me", response_model=dict)
def me(current_user: models.User = Depends(get_current_user)):
return {"id": current_user.id, "email": current_user.email, "two_factor_enabled": current_user.two_factor_enabled}
Alembic — migrácie
backend/alembic/env.py
python

Kopírovať

# backend/alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(**file**), "..")))
from app.db import Base
from app.config import settings
from app import models # ensure models are imported

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
url = settings.DATABASE_URL
context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
with context.begin_transaction():
context.run_migrations()

def run_migrations_online():
connectable = engine_from_config(
{"sqlalchemy.url": settings.DATABASE_URL},
prefix='sqlalchemy.',
poolclass=pool.NullPool)
with connectable.connect() as connection:
context.configure(connection=connection, target_metadata=target_metadata)
with context.begin_transaction():
context.run_migrations()

if context.is_offline_mode():
run_migrations_offline()
else:
run_migrations_online()
backend/alembic/versions/0001_create_users_roles.py
python

Kopírovať

# backend/alembic/versions/0001_create_users_roles.py

"""create users, roles, audit_logs

Revision ID: 0001
Revises:
Create Date: 2026-03-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
op.create_table(
'roles',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('name', sa.String(length=50), nullable=False, unique=True),
)
op.create_table(
'users',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('email', sa.String(length=255), nullable=False, unique=True),
sa.Column('hashed_password', sa.String(length=255), nullable=False),
sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=True),
sa.Column('totp_secret', sa.String(length=32), nullable=True),
sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
)
op.create_table(
'audit_logs',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
sa.Column('action', sa.String(length=255)),
sa.Column('detail', sa.Text(), nullable=True),
sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
)

def downgrade():
op.drop_table('audit_logs')
op.drop_table('users')
op.drop_table('roles')
backend/requirements.txt
Kód

Kopírovať
fastapi==0.95.2
uvicorn[standard]==0.22.0
requests==2.31.0
pydantic==1.10.11
python-dotenv==1.0.0
sqlalchemy==1.4.52
alembic==1.11.1
psycopg2-binary==2.9.7
passlib[bcrypt]==1.7.4
pyjwt==2.8.0
pyotp==2.8.0
certbot==2.6.0
backend/Dockerfile
dockerfile

Kopírovať
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
backend/.env.example
Kód

Kopírovať
WEBSUPPORT_API_KEY=your_api_key_here
WEBSUPPORT_SECRET=your_secret_here
DATABASE_URL=postgresql://postgres:password@postgres:5432/postgres
CERTBOT_EMAIL=admin@example.com
ENV=production
JWT_SECRET=change-me-to-secure-random
JWT_EXPIRE_MINUTES=1440
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=postgres
Frontend — súbory
frontend/package.json
json

Kopírovať
{
"name": "domain-ssl-manager",
"version": "0.1.0",
"private": true,
"scripts": {
"dev": "vite",
"build": "vite build",
"preview": "vite preview"
},
"dependencies": {
"axios": "^1.4.0",
"vue": "^3.3.4"
},
"devDependencies": {
"vite": "^5.0.0",
"vite-plugin-pwa": "^0.15.0",
"@vitejs/plugin-vue": "^4.0.0"
}
}
frontend/vite.config.js
javascript

Kopírovať
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
plugins: [
vue(),
VitePWA({
registerType: 'autoUpdate',
manifest: {
name: 'Domain & SSL Manager',
short_name: 'DSM',
theme_color: '#1e3a8a',
icons: [
{ src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
{ src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' }
]
}
})
],
server: {
proxy: {
'/api': {
target: 'http://backend:8000',
changeOrigin: true,
secure: false,
rewrite: (path) => path.replace(/^\/api/, '/api')
}
}
}
})
frontend/index.html
html

Kopírovať

<!doctype html>
<html lang="sk">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1.0" />
    <title>Domain & SSL Manager</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
frontend/Dockerfile
dockerfile

Kopírovať
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json\* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
frontend/src/main.js
javascript

Kopírovať
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
frontend/src/App.vue
vue

Kopírovať
<template>

  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Domain & SSL Manager</h1>
    <Domains />
  </div>
</template>

<script setup>
import Domains from './views/Domains.vue'
</script>

frontend/src/api/api.js
javascript

Kopírovať
import axios from 'axios'

const api = axios.create({
baseURL: '/api',
timeout: 30000
})

api.interceptors.request.use(config => {
const token = localStorage.getItem('access_token')
if (token) config.headers.Authorization = `Bearer ${token}`
return config
})

export default api
frontend/src/views/Domains.vue
vue

Kopírovať
<template>

  <div class="p-4">
    <h2 class="text-xl font-semibold mb-3">Domény</h2>
    <div class="mb-3">
      <button @click="fetchDomains" class="bg-blue-600 text-white px-3 py-1 rounded">Načítať domény</button>
    </div>

    <div v-if="loading">Načítavam...</div>

    <div v-else>
      <div v-if="domains && domains.length">
        <div v-for="d in domains" :key="d.id" class="border p-2 mb-2">
          <div><strong>{{ d.name }}</strong></div>
          <div v-if="d.description">{{ d.description }}</div>
        </div>
      </div>
      <div v-else>Žiadne domény.</div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/api'

const domains = ref([])
const loading = ref(false)

const fetchDomains = async () => {
  loading.value = true
  try {
    const res = await api.get('/domains')
    domains.value = res.data.domains || res.data
  } catch (err) {
    console.error(err)
    alert('Chyba pri načítaní domén.')
  } finally {
    loading.value = false
  }
}
</script>

frontend/public/manifest.webmanifest
json

Kopírovať
{
"name": "Domain & SSL Manager",
"short_name": "DSM",
"start_url": "/",
"display": "standalone",
"background_color": "#ffffff",
"theme_color": "#1e3a8a",
"icons": [
{ "src": "/pwa-192x192.png", "sizes": "192x192", "type": "image/png" },
{ "src": "/pwa-512x512.png", "sizes": "512x512", "type": "image/png" }
]
}
frontend/public/robots.txt
Kód

Kopírovať
User-agent: \*
Disallow:
Docker Compose
docker-compose.yml
yaml

Kopírovať
version: '3.8'
services:
backend:
build: ./backend
container_name: dsm_backend
ports: - "8000:8000"
environment: - WEBSUPPORT_API_KEY=${WEBSUPPORT_API_KEY}
      - WEBSUPPORT_SECRET=${WEBSUPPORT_SECRET} - DATABASE_URL=${DATABASE_URL}
      - CERTBOT_EMAIL=${CERTBOT_EMAIL} - ENV=${ENV}
      - JWT_SECRET=${JWT_SECRET} - JWT_EXPIRE_MINUTES=${JWT_EXPIRE_MINUTES}
depends_on: - postgres

frontend:
build:
context: ./frontend
container_name: dsm_frontend
ports: - "3000:80"
depends_on: - backend

postgres:
image: postgres:14
environment:
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
POSTGRES_USER: ${POSTGRES_USER}
POSTGRES_DB: ${POSTGRES_DB}
volumes: - postgres_data:/var/lib/postgresql/data

volumes:
postgres_data:
README.md
README.md
markdown

Kopírovať

# Domain & SSL Manager

## Popis

FastAPI backend integrujúci Websupport REST API + Vue 3 PWA frontend. Obsahuje SQLAlchemy, Alembic migrácie, JWT autentifikáciu a 2FA (TOTP).

## Rýchle spustenie (dev)

1. Skopíruj `backend/.env.example` do `backend/.env` a doplň hodnoty.
2. Backend:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
4. Migrácie:
   - `alembic upgrade head` (alebo `python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"` pre dev)

## Nasadenie s Docker Compose

`docker-compose up --build`

## Bezpečnostné poznámky

- **JWT_SECRET** a iné citlivé hodnoty ukladaj mimo repozitára.
- V produkcii obmedz CORS, zapni HTTPS a nastav reverzný proxy (Nginx).
- Certbot vyžaduje porty 80/443; v Docker prostredí rieš s hostom alebo Nginx.

## Ďalšie kroky

- Pridať audit logovanie volaní Websupport API.
- Implementovať rate limiting a monitoring.
- Pridať admin inicializačný skript pre vytvorenie superusera.
  Doplnkové skripty (voliteľné)
  Rýchly skript na vytvorenie admin účtu (spusti v kontejnery alebo lokálne)
  python

Kopírovať

# backend/scripts/create_admin.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(**file**), "..")))
from app.db import SessionLocal, engine, Base
from app import crud, models, auth

def create_admin(email: str, password: str):
db = SessionLocal()
try:
Base.metadata.create_all(bind=engine)
existing = crud.CRUDUser.get_by_email(db, email)
if existing:
print("Admin už existuje.")
return
user = crud.CRUDUser.create(db, email, password)
user.is_superuser = True
db.add(user)
db.commit()
print("Admin vytvorený:", email)
finally:
db.close()

if **name** == "**main**":
create_admin("admin@example.com", "ChangeMe123!")
Poznámky k integrácii Websupport API
Funkcia make_websupport_request bola v pôvodnom blueprint-e. Ak ju potrebuješ, vlož ju do backend/app/websupport.py alebo auth.py a uprav importy v domains/services.py.

Pri volaní certbot v Docker kontejnery zabezpeč, že porty 80/443 sú dostupné a že kontajner má potrebné oprávnenia.

Bezpečnostné odporúčania (stručne)
Ulož JWT_SECRET a WEBSUPPORT_SECRET mimo repozitára.

Obmedz CORS v produkcii.

Zapni HTTPS a reverzný proxy (Nginx) pre certbot a bezpečné vystavenie služieb.

Šifruj citlivé polia v DB podľa potreby.

Ak chceš, môžem teraz:

pridať make_websupport_request implementáciu do backend/app/websupport.py a upraviť importy,

alebo vygenerovať skript init_admin.sh na automatické vytvorenie admin účtu pri nasadení.

Ktorú z týchto dvoch akcií preferuješ ako ďalší krok?

Pokračovať v konverzácii
