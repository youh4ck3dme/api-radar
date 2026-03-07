# Monitoring & Logging Blueprint

## Prehľad
Tento blueprint definuje komplexný monitoring a logging systém pre API Centrum Backend systém.

## Ciele
- Implementovať struktúrované logovanie
- Nastaviť metriky a monitoring (Prometheus/Grafana)
- Vytvoriť health check endpointy
- Nastaviť alerting systém
- Zabezpečiť log agregáciu a analýzu

## 1. Structured Logging

### 1.1 Logging configuration
```python
# app/logging_config.py
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class JSONFormatter(logging.Formatter):
    """JSON formatter pre struktúrované logovanie"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Pridať extra polia ak existujú
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Pridať exception info ak existuje
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pre logovanie HTTP requestov"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Logovanie requestu
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "content_length": request.headers.get("Content-Length"),
            "content_type": request.headers.get("Content-Type")
        }
        
        logger = logging.getLogger("api.requests")
        logger.info("HTTP Request", extra_fields=request_info)
        
        # Vykonanie requestu
        response = await call_next(request)
        
        # Výpočet trvania
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Logovanie response
        response_info = {
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "content_length": response.headers.get("Content-Length")
        }
        
        logger.info("HTTP Response", extra_fields=response_info)
        
        return response

def setup_logging():
    """Nastavenie loggingu"""
    
    # Základné nastavenie
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Vytvorenie loggerov
    loggers = [
        "api",
        "api.requests", 
        "api.auth",
        "api.domains",
        "api.ssl",
        "api.dashboard",
        "api.security",
        "api.errors"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        
        # Vytvorenie handlerov
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        
        # File handler pre produkčné prostredie
        if not logger_name.endswith(".requests"):  # Requesty idú iba do konzoly
            file_handler = logging.FileHandler(f"logs/{logger_name}.log")
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)
        
        logger.addHandler(console_handler)
        logger.propagate = False

# Globálny logger
logger = logging.getLogger("api")

def log_security_event(event_type: str, details: Dict[str, Any], 
                      user_id: Optional[int] = None, 
                      ip_address: Optional[str] = None):
    """Logovanie bezpečnostných udalostí"""
    security_logger = logging.getLogger("api.security")
    
    extra_fields = {
        "event_type": event_type,
        "details": details
    }
    
    if user_id:
        extra_fields["user_id"] = user_id
    if ip_address:
        extra_fields["ip_address"] = ip_address
    
    security_logger.warning("Security Event", extra_fields=extra_fields)

def log_api_error(error_type: str, error_message: str, 
                 endpoint: Optional[str] = None,
                 user_id: Optional[int] = None):
    """Logovanie API chýb"""
    error_logger = logging.getLogger("api.errors")
    
    extra_fields = {
        "error_type": error_type,
        "error_message": error_message
    }
    
    if endpoint:
        extra_fields["endpoint"] = endpoint
    if user_id:
        extra_fields["user_id"] = user_id
    
    error_logger.error("API Error", extra_fields=extra_fields)
```

### 1.2 Application logging
```python
# app/logger.py
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class AppLogger:
    """Aplikačný logger pre rôzne typy logov"""
    
    def __init__(self):
        self.api_logger = logging.getLogger("api")
        self.auth_logger = logging.getLogger("api.auth")
        self.domain_logger = logging.getLogger("api.domains")
        self.ssl_logger = logging.getLogger("api.ssl")
        self.dashboard_logger = logging.getLogger("api.dashboard")
        self.security_logger = logging.getLogger("api.security")
        self.error_logger = logging.getLogger("api.errors")
    
    def log_domain_operation(self, operation: str, domain: str, 
                           user_id: int, success: bool, details: Dict = None):
        """Logovanie operácií s doménami"""
        extra_fields = {
            "operation": operation,
            "domain": domain,
            "user_id": user_id,
            "success": success,
            "details": details or {}
        }
        
        if success:
            self.domain_logger.info(f"Domain {operation} successful", extra_fields=extra_fields)
        else:
            self.domain_logger.error(f"Domain {operation} failed", extra_fields=extra_fields)
    
    def log_ssl_operation(self, operation: str, domain: str,
                         success: bool, details: Dict = None):
        """Logovanie SSL operácií"""
        extra_fields = {
            "operation": operation,
            "domain": domain,
            "success": success,
            "details": details or {}
        }
        
        if success:
            self.ssl_logger.info(f"SSL {operation} successful", extra_fields=extra_fields)
        else:
            self.ssl_logger.error(f"SSL {operation} failed", extra_fields=extra_fields)
    
    def log_auth_attempt(self, email: str, success: bool, 
                        ip_address: str, details: Dict = None):
        """Logovanie pokusov o prihlásenie"""
        extra_fields = {
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        if success:
            self.auth_logger.info("Authentication successful", extra_fields=extra_fields)
        else:
            self.auth_logger.warning("Authentication failed", extra_fields=extra_fields)
    
    def log_dashboard_access(self, user_id: int, endpoint: str, 
                           success: bool, details: Dict = None):
        """Logovanie prístupu k dashboardu"""
        extra_fields = {
            "user_id": user_id,
            "endpoint": endpoint,
            "success": success,
            "details": details or {}
        }
        
        if success:
            self.dashboard_logger.info("Dashboard access", extra_fields=extra_fields)
        else:
            self.dashboard_logger.warning("Dashboard access failed", extra_fields=extra_fields)

# Globálny logger
app_logger = AppLogger()
```

## 2. Prometheus Metrics

### 2.1 Metrics configuration
```python
# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Optional
import time
from fastapi import Request

class Metrics:
    """Prometheus metrics pre API Centrum"""
    
    # Počítadlá pre rôzne typy requestov
    requests_total = Counter(
        'api_requests_total',
        'Total number of API requests',
        ['method', 'endpoint', 'status_code']
    )
    
    # Histogram pre dobu trvania requestov
    request_duration = Histogram(
        'api_request_duration_seconds',
        'Request duration in seconds',
        ['method', 'endpoint'],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    )
    
    # Gauge pre aktívne connectiony
    active_connections = Gauge(
        'api_active_connections',
        'Number of active connections'
    )
    
    # Počítadlá pre autentifikáciu
    auth_attempts = Counter(
        'auth_attempts_total',
        'Total number of authentication attempts',
        ['success', 'method']
    )
    
    # Počítadlá pre domény
    domain_operations = Counter(
        'domain_operations_total',
        'Total number of domain operations',
        ['operation', 'success']
    )
    
    # Počítadlá pre SSL
    ssl_operations = Counter(
        'ssl_operations_total',
        'Total number of SSL operations',
        ['operation', 'success']
    )
    
    # Počítadlá pre chyby
    errors_total = Counter(
        'api_errors_total',
        'Total number of API errors',
        ['error_type', 'endpoint']
    )
    
    # Summary pre response veľkosti
    response_size = Summary(
        'api_response_size_bytes',
        'Response size in bytes',
        ['endpoint']
    )
    
    # Gauge pre systémové metriky
    system_health = Gauge(
        'system_health_status',
        'System health status (1=healthy, 0=unhealthy)',
        ['component']
    )
    
    # Gauge pre počet užívateľov
    user_count = Gauge(
        'user_count',
        'Number of users'
    )
    
    # Gauge pre počet domén
    domain_count = Gauge(
        'domain_count',
        'Number of domains'
    )
    
    # Gauge pre SSL certifikáty
    ssl_certificates = Gauge(
        'ssl_certificates_count',
        'Number of SSL certificates',
        ['status']
    )

class MetricsMiddleware:
    """Middleware pre meranie metrík"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        # Zvýšiť počítadlo aktívnych connectionov
        Metrics.active_connections.inc()
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                
                # Zaznamenať metriky
                Metrics.requests_total.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()
                
                duration = time.time() - start_time
                Metrics.request_duration.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
                
                # Znížiť počítadlo aktívnych connectionov
                Metrics.active_connections.dec()
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

def record_auth_metric(success: bool, method: str = "jwt"):
    """Zaznamenať metriku pre autentifikáciu"""
    Metrics.auth_attempts.labels(
        success="success" if success else "failure",
        method=method
    ).inc()

def record_domain_operation(operation: str, success: bool):
    """Zaznamenať metriku pre operáciu s doménou"""
    Metrics.domain_operations.labels(
        operation=operation,
        success="success" if success else "failure"
    ).inc()

def record_ssl_operation(operation: str, success: bool):
    """Zaznamenať metriku pre SSL operáciu"""
    Metrics.ssl_operations.labels(
        operation=operation,
        success="success" if success else "failure"
    ).inc()

def record_error(error_type: str, endpoint: str):
    """Zaznamenať metriku pre chybu"""
    Metrics.errors_total.labels(
        error_type=error_type,
        endpoint=endpoint
    ).inc()
```

### 2.2 Metrics endpoints
```python
# app/metrics/routes.py
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Tu by mohla byť kontrola pripojenia k databáze, externým API atď.
    return {
        "status": "ready",
        "timestamp": time.time()
    }

@router.get("/live")
async def liveness_check():
    """Liveness check endpoint"""
    return {
        "status": "alive",
        "timestamp": time.time()
    }
```

## 3. Health Check System

### 3.1 Health check service
```python
# app/health.py
import asyncio
import aiohttp
import time
from typing import Dict, Any, List
from datetime import datetime
import redis
import sqlalchemy

class HealthCheck:
    """Health check service pre monitorovanie systému"""
    
    def __init__(self):
        self.checks = []
    
    def add_check(self, name: str, check_func):
        """Pridať health check funkciu"""
        self.checks.append({
            "name": name,
            "function": check_func,
            "last_result": None,
            "last_check": None
        })
    
    async def run_checks(self) -> Dict[str, Any]:
        """Spustiť všetky health checks"""
        results = {}
        
        for check in self.checks:
            try:
                start_time = time.time()
                result = await check["function"]()
                duration = time.time() - start_time
                
                check["last_result"] = result
                check["last_check"] = datetime.utcnow()
                
                results[check["name"]] = {
                    "status": "healthy" if result["healthy"] else "unhealthy",
                    "message": result.get("message", ""),
                    "duration": duration,
                    "details": result.get("details", {})
                }
                
            except Exception as e:
                results[check["name"]] = {
                    "status": "error",
                    "message": str(e),
                    "duration": 0,
                    "details": {}
                }
        
        return results
    
    def get_overall_status(self, results: Dict[str, Any]) -> str:
        """Získať celkový status systému"""
        statuses = [result["status"] for result in results.values()]
        
        if "error" in statuses:
            return "error"
        elif "unhealthy" in statuses:
            return "unhealthy"
        else:
            return "healthy"

# Konkrétne health check funkcie
async def check_database():
    """Kontrola pripojenia k databáze"""
    try:
        # Testovacie pripojenie k databáze
        from app.db import engine
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        
        return {
            "healthy": True,
            "message": "Database connection OK",
            "details": {"type": "PostgreSQL"}
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Database connection failed: {str(e)}",
            "details": {}
        }

async def check_websupport_api():
    """Kontrola Websupport API"""
    try:
        from app.websupport import WebsupportService
        service = WebsupportService()
        
        # Testovacie volanie
        domains = await service.list_domains()
        
        return {
            "healthy": True,
            "message": f"Websupport API OK, {len(domains)} domains found",
            "details": {"domains_count": len(domains)}
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Websupport API failed: {str(e)}",
            "details": {}
        }

async def check_neon_auth():
    """Kontrola Neon Auth trial"""
    try:
        from app.neon_auth import NeonAuthService
        service = NeonAuthService()
        
        # Testovacie volanie
        result = await service.check_trial_status()
        
        return {
            "healthy": result["active"],
            "message": f"Neon Auth trial {'active' if result['active'] else 'inactive'}",
            "details": result
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Neon Auth check failed: {str(e)}",
            "details": {}
        }

async def check_redis():
    """Kontrola Redis pripojenia"""
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        
        return {
            "healthy": True,
            "message": "Redis connection OK",
            "details": {"host": "localhost", "port": 6379}
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Redis connection failed: {str(e)}",
            "details": {}
        }

async def check_ssl_certificates():
    """Kontrola SSL certifikátov"""
    try:
        from app.ssl.services import SSLService
        service = SSLService()
        
        # Získanie SSL certifikátov
        certificates = await service.list_certificates()
        
        return {
            "healthy": True,
            "message": f"SSL certificates OK, {len(certificates)} certificates found",
            "details": {"certificates_count": len(certificates)}
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"SSL certificates check failed: {str(e)}",
            "details": {}
        }

# Inicializácia health check service
health_check = HealthCheck()
health_check.add_check("database", check_database)
health_check.add_check("websupport_api", check_websupport_api)
health_check.add_check("neon_auth", check_neon_auth)
health_check.add_check("redis", check_redis)
health_check.add_check("ssl_certificates", check_ssl_certificates)
```

### 3.2 Health check endpoints
```python
# app/health/routes.py
from fastapi import APIRouter
from ..health import health_check

router = APIRouter()

@router.get("/health")
async def health_status():
    """Detailed health status"""
    results = await health_check.run_checks()
    overall_status = health_check.get_overall_status(results)
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": results
    }

@router.get("/health/simple")
async def simple_health():
    """Simple health check"""
    results = await health_check.run_checks()
    overall_status = health_check.get_overall_status(results)
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check - pre Kubernetes"""
    results = await health_check.run_checks()
    
    # Readiness check zlyhá ak je nejaký kritický komponent down
    critical_checks = ["database", "websupport_api"]
    
    for check_name in critical_checks:
        if check_name in results and results[check_name]["status"] != "healthy":
            return {"status": "not ready", "reason": f"{check_name} is down"}
    
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    """Liveness check - pre Kubernetes"""
    return {"status": "alive"}
```

## 4. Alerting System

### 4.1 Alert manager configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@api-centrum.sk'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://localhost:8000/api/alerts/webhook'

- name: 'critical-alerts'
  email_configs:
  - to: 'admin@api-centrum.sk'
    subject: '[CRITICAL] API Centrum Alert'
    body: |
      Alert: {{ .GroupLabels.alertname }}
      Severity: {{ .CommonLabels.severity }}
      Description: {{ .CommonAnnotations.description }}
      Time: {{ .CommonLabels.time }}

- name: 'warning-alerts'
  email_configs:
  - to: 'team@api-centrum.sk'
    subject: '[WARNING] API Centrum Alert'
    body: |
      Alert: {{ .GroupLabels.alertname }}
      Severity: {{ .CommonLabels.severity }}
      Description: {{ .CommonAnnotations.description }}
      Time: {{ .CommonLabels.time }}
```

### 4.2 Prometheus rules
```yaml
# prometheus-rules.yml
groups:
- name: api-centrum.rules
  rules:
  - alert: HighErrorRate
    expr: rate(api_errors_total[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"

  - alert: DatabaseDown
    expr: up{job="database"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database is down"
      description: "Database has been down for more than 1 minute"

  - alert: WebsupportAPIError
    expr: rate(api_errors_total{error_type="websupport_api"}[5m]) > 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Websupport API errors detected"
      description: "Websupport API is returning errors"

  - alert: SSLCertificateExpiring
    expr: ssl_certificates_expires_in_days < 30
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "SSL certificate expiring soon"
      description: "SSL certificate for {{ $labels.domain }} expires in {{ $value }} days"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is above 80%"

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is above 80%"
```

### 4.3 Alert webhook handler
```python
# app/alerts/routes.py
from fastapi import APIRouter, Request, HTTPException
import logging
import json

router = APIRouter()

@router.post("/alerts/webhook")
async def alert_webhook(request: Request):
    """Webhook pre prijímanie alertov z AlertManager"""
    try:
        data = await request.json()
        
        # Logovanie alertu
        logger = logging.getLogger("api.alerts")
        
        for alert in data.get("alerts", []):
            alert_info = {
                "alertname": alert.get("labels", {}).get("alertname"),
                "severity": alert.get("labels", {}).get("severity"),
                "status": alert.get("status"),
                "starts_at": alert.get("startsAt"),
                "ends_at": alert.get("endsAt"),
                "description": alert.get("annotations", {}).get("description"),
                "summary": alert.get("annotations", {}).get("summary")
            }
            
            logger.warning("Alert received", extra_fields=alert_info)
            
            # Tu by sa mohli odoslať notifikácie (email, Slack, atď.)
            await send_alert_notification(alert_info)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Alert webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def send_alert_notification(alert_info: Dict):
    """Odoslanie notifikácie o alarte"""
    # Implementácia odosielania notifikácií
    # Email, Slack, SMS, atď.
    pass
```

## 5. Log Aggregation

### 5.1 ELK Stack configuration
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logs:/var/log/api-centrum:ro
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.8.0
    user: root
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./logs:/var/log/api-centrum:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - logstash

volumes:
  elasticsearch_data:
```

### 5.2 Logstash configuration
```yaml
# logstash/config/logstash.yml
http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.hosts: [ "http://elasticsearch:9200" ]
```

```ruby
# logstash/pipeline/logstash.conf
input {
  beats {
    port => 5044
  }
  
  file {
    path => "/var/log/api-centrum/*.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [logger] {
    mutate {
      add_field => { "service" => "%{logger}" }
    }
  }
  
  if [level] {
    mutate {
      add_field => { "log_level" => "%{level}" }
    }
  }
  
  if [extra_fields] {
    ruby {
      code => "
        event.to_hash.each do |k,v|
          if k.start_with?('extra_fields.')
            new_key = k.split('.', 2)[1]
            event.set(new_key, v)
          end
        end
      "
    }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "api-centrum-logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
```

### 5.3 Filebeat configuration
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/api-centrum/*.log
  json.keys_under_root: true
  json.add_error_key: true

- type: docker
  enabled: true
  containers.ids:
    - "*"

output.logstash:
  hosts: ["logstash:5044"]

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded
```

## 6. Grafana Dashboards

### 6.1 Dashboard configuration
```json
{
  "dashboard": {
    "id": null,
    "title": "API Centrum Monitoring",
    "tags": ["api", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_errors_total[5m])",
            "legendFormat": "{{error_type}}"
          }
        ],
        "yAxes": [
          {
            "label": "Errors/sec"
          }
        ]
      },
      {
        "id": 4,
        "title": "System Health",
        "type": "stat",
        "targets": [
          {
            "expr": "system_health_status",
            "legendFormat": "{{component}}"
          }
        ]
      },
      {
        "id": 5,
        "title": "Active Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "api_active_connections",
            "legendFormat": "Active connections"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
```

## 7. Implementation Steps

### 7.1 Week 1: Basic Logging
- [ ] Nastaviť structured logging
- [ ] Vytvoriť JSON formatter
- [ ] Pridať request logging middleware
- [ ] Nastaviť logovanie pre rôzne komponenty

### 7.2 Week 2: Prometheus Metrics
- [ ] Nastaviť Prometheus client
- [ ] Vytvoriť custom metrics
- [ ] Pridať metrics middleware
- [ ] Vytvoriť metrics endpoints

### 7.3 Week 3: Health Checks
- [ ] Implementovať health check service
- [ ] Vytvoriť konkrétne health check funkcie
- [ ] Pridať health check endpoints
- [ ] Nastaviť readiness a liveness checks

### 7.4 Week 4: Alerting
- [ ] Nastaviť AlertManager
- [ ] Vytvoriť Prometheus rules
- [ ] Implementovať alert webhook
- [ ] Nastaviť notifikácie

### 7.5 Week 5: Log Aggregation
- [ ] Nastaviť ELK stack
- [ ] Konfigurovať Logstash
- [ ] Nastaviť Filebeat
- [ ] Vytvoriť Kibana dashboards

### 7.6 Week 6: Grafana & Polish
- [ ] Nastaviť Grafana
- [ ] Vytvoriť monitoring dashboards
- [ ] Konfigurovať notifikácie
- [ ] Testovanie a optimalizácia

## 8. Best Practices

### 8.1 Logging best practices
- **Structured logging**: Používať JSON formát pre logy
- **Consistent fields**: Používať konzistentné názvy polí
- **Log levels**: Správne používať log úrovne (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Context**: Pridávať kontext do logov (user_id, request_id, atď.)
- **Performance**: Neprekážať výkonu aplikácie logovaním

### 8.2 Monitoring best practices
- **Right metrics**: Meriať len relevantné metriky
- **Alert fatigue**: Vyhnúť sa príliš častým falošným alertom
- **Dashboards**: Vytvárať prehľadné a užitočné dashboards
- **Trends**: Sledovať trendy a dlhodobé zmeny
- **Automation**: Automatizovať reakcie na bežné problémy

### 8.3 Alerting best practices
- **Escalation**: Nastaviť vhodné eskalácie
- **On-call**: Mať jasný on-call proces
- **Runbooks**: Mať dokumentované postupy pre riešenie problémov
- **Testing**: Pravidelne testovať alerting systém
- **Review**: Pravidelne reviewovať a optimalizovať alerty

Tento blueprint poskytuje komplexný návod na implementáciu robustného monitoring a logging systému pre API Centrum Backend systém.