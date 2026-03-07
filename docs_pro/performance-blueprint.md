# Performance Blueprint

## Prehľad
Tento blueprint definuje stratégie a techniky pre optimalizáciu výkonu API Centrum Backend systému vrátane caching, load balancing, database optimization a monitoringu.

## Ciele
- Optimalizovať response times API endpointov
- Implementovať efektívne caching stratégie
- Nastaviť load balancing a horizontal scaling
- Optimalizovať databázové operácie
- Zabezpečiť monitoring a profiling výkonu
- Pripraviť systém na vysoké zaťaženie

## 1. Performance Analysis

### 1.1 Current performance bottlenecks
```python
# app/performance/analysis.py
"""
Performance analysis and bottleneck identification
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager
import psutil
import sqlalchemy
from sqlalchemy import text
from app.db import SessionLocal, engine

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: float
    context: Dict[str, Any] = None

@dataclass
class Bottleneck:
    type: str  # database, network, cpu, memory, io
    severity: str  # low, medium, high, critical
    description: str
    location: str
    impact: str
    suggestions: List[str]

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = []
        self.bottlenecks = []
    
    @contextmanager
    def measure_time(self, operation_name: str, context: Dict = None):
        """Context manager for timing operations"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            metric = PerformanceMetric(
                name=operation_name,
                value=duration,
                unit="seconds",
                timestamp=time.time(),
                context=context or {}
            )
            self.metrics.append(metric)
    
    async def analyze_database_performance(self) -> List[Bottleneck]:
        """Analyze database performance bottlenecks"""
        bottlenecks = []
        
        # Check for slow queries
        slow_queries = await self._find_slow_queries()
        for query in slow_queries:
            bottlenecks.append(Bottleneck(
                type="database",
                severity="high" if query['duration'] > 1.0 else "medium",
                description=f"Slow query detected: {query['query'][:100]}...",
                location="database",
                impact=f"Query took {query['duration']:.2f}s",
                suggestions=[
                    "Add appropriate indexes",
                    "Optimize query structure",
                    "Consider query caching"
                ]
            ))
        
        # Check connection pool usage
        pool_stats = await self._check_connection_pool()
        if pool_stats['usage'] > 80:
            bottlenecks.append(Bottleneck(
                type="database",
                severity="medium",
                description=f"High database connection pool usage: {pool_stats['usage']}%",
                location="database",
                impact="Potential connection exhaustion",
                suggestions=[
                    "Increase connection pool size",
                    "Optimize connection usage",
                    "Implement connection pooling"
                ]
            ))
        
        # Check for N+1 queries
        n_plus_one_issues = await self._detect_n_plus_one()
        for issue in n_plus_one_issues:
            bottlenecks.append(Bottleneck(
                type="database",
                severity="high",
                description=f"N+1 query issue in {issue['location']}",
                location="application",
                impact="Multiple unnecessary queries",
                suggestions=[
                    "Use selectinload or joinedload",
                    "Implement eager loading",
                    "Batch database operations"
                ]
            ))
        
        return bottlenecks
    
    async def analyze_memory_usage(self) -> List[Bottleneck]:
        """Analyze memory usage bottlenecks"""
        bottlenecks = []
        
        # Get current memory usage
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Check for memory leaks
        if memory_info.rss > 1024 * 1024 * 512:  # 512MB
            bottlenecks.append(Bottleneck(
                type="memory",
                severity="high",
                description=f"High memory usage detected: {memory_info.rss / 1024 / 1024:.2f}MB",
                location="application",
                impact="Potential memory leak",
                suggestions=[
                    "Check for circular references",
                    "Implement proper cleanup",
                    "Use memory profiling tools"
                ]
            ))
        
        # Check for large objects in memory
        large_objects = await self._find_large_objects()
        for obj in large_objects:
            bottlenecks.append(Bottleneck(
                type="memory",
                severity="medium",
                description=f"Large object in memory: {obj['type']} ({obj['size']} bytes)",
                location="application",
                impact="Memory pressure",
                suggestions=[
                    "Use streaming for large data",
                    "Implement pagination",
                    "Clear unused objects"
                ]
            ))
        
        return bottlenecks
    
    async def analyze_api_performance(self) -> List[Bottleneck]:
        """Analyze API endpoint performance"""
        bottlenecks = []
        
        # Analyze endpoint response times
        endpoint_stats = await self._get_endpoint_stats()
        
        for endpoint, stats in endpoint_stats.items():
            if stats['avg_response_time'] > 1.0:
                bottlenecks.append(Bottleneck(
                    type="api",
                    severity="medium",
                    description=f"Slow endpoint: {endpoint}",
                    location=f"endpoint: {endpoint}",
                    impact=f"Avg response time: {stats['avg_response_time']:.2f}s",
                    suggestions=[
                        "Implement caching",
                        "Optimize database queries",
                        "Add pagination"
                    ]
                ))
            
            if stats['error_rate'] > 0.05:  # 5% error rate
                bottlenecks.append(Bottleneck(
                    type="api",
                    severity="high",
                    description=f"High error rate for endpoint: {endpoint}",
                    location=f"endpoint: {endpoint}",
                    impact=f"Error rate: {stats['error_rate'] * 100:.2f}%",
                    suggestions=[
                        "Improve error handling",
                        "Add input validation",
                        "Implement retry logic"
                    ]
                ))
        
        return bottlenecks
    
    async def _find_slow_queries(self) -> List[Dict]:
        """Find slow database queries"""
        # This would integrate with database query logging
        # For now, return mock data
        return [
            {
                'query': 'SELECT * FROM domains WHERE user_id = ?',
                'duration': 2.5,
                'count': 100
            }
        ]
    
    async def _check_connection_pool(self) -> Dict:
        """Check database connection pool usage"""
        # Get connection pool stats from SQLAlchemy
        pool = engine.pool
        return {
            'total_connections': pool.size(),
            'in_use': pool.checked_in(),
            'available': pool.checked_out(),
            'usage': (pool.checked_out() / pool.size()) * 100 if pool.size() > 0 else 0
        }
    
    async def _detect_n_plus_one(self) -> List[Dict]:
        """Detect N+1 query patterns"""
        # This would require query analysis
        # For now, return mock data
        return [
            {
                'location': 'domain_service.get_domains_with_users()',
                'query_count': 100,
                'suggestion': 'Use selectinload for users'
            }
        ]
    
    async def _find_large_objects(self) -> List[Dict]:
        """Find large objects in memory"""
        # This would require memory profiling
        # For now, return mock data
        return [
            {
                'type': 'list',
                'size': 1024 * 1024 * 100,  # 100MB
                'location': 'cache_service.domains_cache'
            }
        ]
    
    async def _get_endpoint_stats(self) -> Dict:
        """Get endpoint performance statistics"""
        # This would integrate with monitoring/logging
        # For now, return mock data
        return {
            '/api/domains': {
                'avg_response_time': 0.5,
                'error_rate': 0.01,
                'request_count': 1000
            },
            '/api/ssl/generate': {
                'avg_response_time': 2.0,
                'error_rate': 0.05,
                'request_count': 100
            }
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance analysis report"""
        return {
            'timestamp': time.time(),
            'metrics': [vars(metric) for metric in self.metrics],
            'bottlenecks': [vars(bottleneck) for bottleneck in self.bottlenecks],
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Group bottlenecks by type
        bottleneck_types = {}
        for bottleneck in self.bottlenecks:
            if bottleneck.type not in bottleneck_types:
                bottleneck_types[bottleneck.type] = []
            bottleneck_types[bottleneck.type].append(bottleneck)
        
        # Generate recommendations based on bottleneck types
        for btype, bottlenecks in bottleneck_types.items():
            if btype == "database":
                recommendations.append({
                    'priority': 'high',
                    'category': 'database',
                    'title': 'Database Performance Optimization',
                    'description': f'Found {len(bottlenecks)} database performance issues',
                    'actions': [
                        'Implement query optimization',
                        'Add database indexes',
                        'Configure connection pooling',
                        'Enable query caching'
                    ]
                })
            
            elif btype == "memory":
                recommendations.append({
                    'priority': 'medium',
                    'category': 'memory',
                    'title': 'Memory Usage Optimization',
                    'description': f'Found {len(bottlenecks)} memory usage issues',
                    'actions': [
                        'Implement object pooling',
                        'Use streaming for large data',
                        'Add memory monitoring',
                        'Optimize data structures'
                    ]
                })
        
        return recommendations
```

## 2. Caching Strategies

### 2.1 Redis caching service
```python
# app/caching/services.py
import json
import pickle
import hashlib
from typing import Any, Optional, Union, List, Dict, TypeVar, Callable
from datetime import datetime, timedelta
import redis.asyncio as redis
from functools import wraps
from app.core.config import settings

T = TypeVar('T')

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=False  # For binary data
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return None
            
            # Try JSON first, then pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            # Try JSON first, then pickle
            try:
                data = json.dumps(value).encode('utf-8')
            except (TypeError, ValueError):
                data = pickle.dumps(value)
            
            await self.redis_client.setex(key, ttl, data)
            return True
        
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        try:
            await self.redis_client.expire(key, ttl)
            return True
        except Exception as e:
            print(f"Cache expire error: {e}")
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        result[key] = pickle.loads(value)
            
            return result
        except Exception as e:
            print(f"Cache get_many error: {e}")
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set multiple values in cache"""
        try:
            pipe = self.redis_client.pipeline()
            
            for key, value in data.items():
                try:
                    data_bytes = json.dumps(value).encode('utf-8')
                except (TypeError, ValueError):
                    data_bytes = pickle.dumps(value)
                
                pipe.setex(key, ttl, data_bytes)
            
            await pipe.execute()
            return True
        
        except Exception as e:
            print(f"Cache set_many error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache keys matching pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            print(f"Cache clear_pattern error: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self.redis_client.info()
            return {
                'memory_usage': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info),
                'total_keys': sum(info.get(f'db{i}', {}).get('keys', 0) for i in range(16))
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100

# Cache decorators
def cache_result(ttl: int = 3600, key_prefix: str = "api"):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Try to get from cache
            cache_service = CacheService()
            cached_result = await cache_service.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Decorator to invalidate cache on function execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            cache_service = CacheService()
            await cache_service.clear_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator

def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
    """Generate cache key from function and arguments"""
    # Create a unique key based on function name and arguments
    key_data = {
        'func': f"{func.__module__}.{func.__name__}",
        'args': args,
        'kwargs': kwargs
    }
    
    # Create hash of the key data
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"{prefix}:{key_hash}"
```

### 2.2 Domain caching service
```python
# app/caching/domain_cache.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.caching.services import CacheService, cache_result, invalidate_cache
from app.models import Domain
from app.schemas import Domain as DomainSchema

class DomainCacheService:
    def __init__(self):
        self.cache = CacheService()
        self.ttl = 300  # 5 minutes for domains
    
    @cache_result(ttl=300, key_prefix="domain")
    async def get_domain(self, domain_id: int) -> Optional[DomainSchema]:
        """Get domain from cache or database"""
        # This would be implemented in the actual service
        # For now, return None to indicate cache miss
        return None
    
    @cache_result(ttl=600, key_prefix="domain_list")  # 10 minutes for lists
    async def get_user_domains(self, user_id: int, limit: int = 100, offset: int = 0) -> List[DomainSchema]:
        """Get user domains from cache or database"""
        return []
    
    @cache_result(ttl=1800, key_prefix="domain_stats")  # 30 minutes for stats
    async def get_domain_stats(self, user_id: int) -> Dict[str, Any]:
        """Get domain statistics from cache or database"""
        return {
            'total_domains': 0,
            'active_domains': 0,
            'ssl_enabled_domains': 0,
            'expiring_soon': 0
        }
    
    @invalidate_cache("domain:*")
    @invalidate_cache("domain_list:*")
    @invalidate_cache("domain_stats:*")
    async def invalidate_domain_cache(self, domain_id: Optional[int] = None):
        """Invalidate domain-related cache"""
        pass
    
    async def warm_domain_cache(self, user_id: int):
        """Pre-populate domain cache for user"""
        # Get domains and cache them individually
        domains = await self.get_user_domains(user_id)
        
        cache_data = {}
        for domain in domains:
            cache_key = f"domain:{domain.id}"
            cache_data[cache_key] = domain
        
        if cache_data:
            await self.cache.set_many(cache_data, self.ttl)
    
    async def get_cache_health(self) -> Dict[str, Any]:
        """Get domain cache health status"""
        stats = await self.cache.get_cache_stats()
        
        return {
            'service': 'domain_cache',
            'ttl': self.ttl,
            'stats': stats,
            'patterns': [
                'domain:*',
                'domain_list:*',
                'domain_stats:*'
            ]
        }
```

### 2.3 SSL caching service
```python
# app/caching/ssl_cache.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.caching.services import CacheService, cache_result, invalidate_cache
from app.models import SSLCertificate

class SSLCacheService:
    def __init__(self):
        self.cache = CacheService()
        self.ttl = 600  # 10 minutes for SSL data
    
    @cache_result(ttl=600, key_prefix="ssl")
    async def get_ssl_certificate(self, domain_name: str) -> Optional[Dict]:
        """Get SSL certificate from cache or database"""
        return None
    
    @cache_result(ttl=1800, key_prefix="ssl_list")  # 30 minutes for lists
    async def get_user_ssl_certificates(self, user_id: int) -> List[Dict]:
        """Get user SSL certificates from cache or database"""
        return []
    
    @cache_result(ttl=3600, key_prefix="ssl_status")  # 1 hour for status
    async def get_ssl_status(self, domain_name: str) -> Dict[str, Any]:
        """Get SSL status from cache or external API"""
        return {
            'status': 'unknown',
            'expires_at': None,
            'issuer': None,
            'valid': False
        }
    
    @invalidate_cache("ssl:*")
    @invalidate_cache("ssl_list:*")
    @invalidate_cache("ssl_status:*")
    async def invalidate_ssl_cache(self, domain_name: Optional[str] = None):
        """Invalidate SSL-related cache"""
        pass
    
    async def cache_ssl_validation_result(self, domain_name: str, result: Dict[str, Any]):
        """Cache SSL validation result"""
        cache_key = f"ssl_validation:{domain_name}"
        await self.cache.set(cache_key, result, self.ttl * 2)  # Cache validation longer
    
    async def get_ssl_validation_result(self, domain_name: str) -> Optional[Dict]:
        """Get cached SSL validation result"""
        cache_key = f"ssl_validation:{domain_name}"
        return await self.cache.get(cache_key)
    
    async def get_cache_health(self) -> Dict[str, Any]:
        """Get SSL cache health status"""
        stats = await self.cache.get_cache_stats()
        
        return {
            'service': 'ssl_cache',
            'ttl': self.ttl,
            'stats': stats,
            'patterns': [
                'ssl:*',
                'ssl_list:*',
                'ssl_status:*',
                'ssl_validation:*'
            ]
        }
```

## 3. Database Optimization

### 3.1 Database connection pooling
```python
# app/db/optimized.py
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import time
import logging
from app.core.config import settings

# Configure optimized database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to keep open
    max_overflow=30,  # Number of connections to allow beyond pool_size
    pool_timeout=30,  # Timeout for getting a connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before use
    echo=False,  # Set to True for SQL logging
    connect_args={
        "connect_timeout": 10,
        "application_name": "api_centrum_backend"
    }
)

# Create optimized session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Keep objects valid after commit
)

# Connection monitoring
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for performance (if using SQLite)"""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=memory")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time"""
    total = time.time() - context._query_start_time
    
    if total > 1.0:  # Log queries taking more than 1 second
        logging.warning(f"Slow query detected: {total:.2f}s - {statement[:100]}...")

@contextmanager
def get_db_session() -> Session:
    """Get database session with proper cleanup"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

class DatabaseOptimizer:
    """Database optimization utilities"""
    
    @staticmethod
    def optimize_query(query):
        """Apply query optimizations"""
        # Add query hints and optimizations
        return query.execution_options(
            compiled_cache=None,  # Disable query compilation cache for complex queries
            stream_results=True  # Enable streaming for large result sets
        )
    
    @staticmethod
    def batch_insert(session: Session, model_class, data_list: List[Dict], batch_size: int = 1000):
        """Optimized batch insert"""
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            session.bulk_insert_mappings(model_class, batch)
            session.flush()
        
        session.commit()
    
    @staticmethod
    def batch_update(session: Session, model_class, updates: List[Dict], batch_size: int = 1000):
        """Optimized batch update"""
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            session.bulk_update_mappings(model_class, batch)
            session.flush()
        
        session.commit()
    
    @staticmethod
    async def get_connection_stats():
        """Get database connection statistics"""
        pool = engine.pool
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checked_in(),
            'checked_out': pool.checked_out(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid(),
            'total_connections': pool.size() + pool.overflow(),
            'utilization': (pool.checked_out() / pool.size()) * 100 if pool.size() > 0 else 0
        }
```

### 3.2 Database indexes and queries
```python
# app/db/indexes.py
"""
Database indexes for optimal performance
"""

from sqlalchemy import Index, text
from app.models import Domain, SSLCertificate, User, AuditLog

# Domain indexes
DOMAIN_USER_INDEX = Index('idx_domain_user_id', Domain.user_id)
DOMAIN_NAME_INDEX = Index('idx_domain_name', Domain.name)
DOMAIN_STATUS_INDEX = Index('idx_domain_status', Domain.status)
DOMAIN_CREATED_AT_INDEX = Index('idx_domain_created_at', Domain.created_at)

# SSL Certificate indexes
SSL_DOMAIN_INDEX = Index('idx_ssl_domain_name', SSLCertificate.domain_name)
SSL_USER_INDEX = Index('idx_ssl_user_id', SSLCertificate.user_id)
SSL_EXPIRES_AT_INDEX = Index('idx_ssl_expires_at', SSLCertificate.expires_at)
SSL_STATUS_INDEX = Index('idx_ssl_status', SSLCertificate.status)

# User indexes
USER_EMAIL_INDEX = Index('idx_user_email', User.email, unique=True)
USER_CREATED_AT_INDEX = Index('idx_user_created_at', User.created_at)

# Audit log indexes
AUDIT_USER_INDEX = Index('idx_audit_user_id', AuditLog.user_id)
AUDIT_ACTION_INDEX = Index('idx_audit_action', AuditLog.action)
AUDIT_RESOURCE_TYPE_INDEX = Index('idx_audit_resource_type', AuditLog.resource_type)
AUDIT_CREATED_AT_INDEX = Index('idx_audit_created_at', AuditLog.created_at)

# Composite indexes for common queries
DOMAIN_USER_STATUS_INDEX = Index('idx_domain_user_status', Domain.user_id, Domain.status)
SSL_DOMAIN_EXPIRES_INDEX = Index('idx_ssl_domain_expires', SSLCertificate.domain_name, SSLCertificate.expires_at)
AUDIT_USER_ACTION_INDEX = Index('idx_audit_user_action', AuditLog.user_id, AuditLog.action)

# Full-text search index for domains (if supported)
DOMAIN_SEARCH_INDEX = Index(
    'idx_domain_search',
    text('to_tsvector(\'english\', name || \' \' || COALESCE(description, \'\'))'),
    postgresql_using='gin'
)

def create_indexes(engine):
    """Create all performance indexes"""
    indexes = [
        DOMAIN_USER_INDEX,
        DOMAIN_NAME_INDEX,
        DOMAIN_STATUS_INDEX,
        DOMAIN_CREATED_AT_INDEX,
        SSL_DOMAIN_INDEX,
        SSL_USER_INDEX,
        SSL_EXPIRES_AT_INDEX,
        SSL_STATUS_INDEX,
        USER_EMAIL_INDEX,
        USER_CREATED_AT_INDEX,
        AUDIT_USER_INDEX,
        AUDIT_ACTION_INDEX,
        AUDIT_RESOURCE_TYPE_INDEX,
        AUDIT_CREATED_AT_INDEX,
        DOMAIN_USER_STATUS_INDEX,
        SSL_DOMAIN_EXPIRES_INDEX,
        AUDIT_USER_ACTION_INDEX
    ]
    
    for index in indexes:
        try:
            index.create(engine, checkfirst=True)
            print(f"Created index: {index.name}")
        except Exception as e:
            print(f"Failed to create index {index.name}: {e}")

def drop_indexes(engine):
    """Drop all performance indexes"""
    indexes = [
        DOMAIN_USER_INDEX,
        DOMAIN_NAME_INDEX,
        DOMAIN_STATUS_INDEX,
        DOMAIN_CREATED_AT_INDEX,
        SSL_DOMAIN_INDEX,
        SSL_USER_INDEX,
        SSL_EXPIRES_AT_INDEX,
        SSL_STATUS_INDEX,
        USER_EMAIL_INDEX,
        USER_CREATED_AT_INDEX,
        AUDIT_USER_INDEX,
        AUDIT_ACTION_INDEX,
        AUDIT_RESOURCE_TYPE_INDEX,
        AUDIT_CREATED_AT_INDEX,
        DOMAIN_USER_STATUS_INDEX,
        SSL_DOMAIN_EXPIRES_INDEX,
        AUDIT_USER_ACTION_INDEX
    ]
    
    for index in indexes:
        try:
            index.drop(engine, checkfirst=True)
            print(f"Dropped index: {index.name}")
        except Exception as e:
            print(f"Failed to drop index {index.name}: {e}")
```

### 3.3 Query optimization
```python
# app/db/query_optimizer.py
"""
Query optimization utilities and patterns
"""

from sqlalchemy.orm import Query, selectinload, joinedload, subqueryload
from sqlalchemy import and_, or_, func, desc, asc
from typing import Type, List, Optional, Union, Any
from app.db import SessionLocal

class QueryOptimizer:
    """Optimize database queries for better performance"""
    
    @staticmethod
    def optimize_domain_query(query: Query, eager_load: bool = True) -> Query:
        """Optimize domain query with proper eager loading"""
        if eager_load:
            # Use selectinload for one-to-many relationships
            query = query.options(
                selectinload('*')  # Load all relationships efficiently
            )
        
        return query
    
    @staticmethod
    def optimize_ssl_query(query: Query, eager_load: bool = True) -> Query:
        """Optimize SSL certificate query"""
        if eager_load:
            query = query.options(
                selectinload('*')
            )
        
        return query
    
    @staticmethod
    def add_pagination(query: Query, page: int = 1, size: int = 20) -> Query:
        """Add pagination to query"""
        offset = (page - 1) * size
        return query.offset(offset).limit(size)
    
    @staticmethod
    def add_search_filter(query: Query, model_class: Type, search_term: str, 
                         search_fields: List[str]) -> Query:
        """Add search filter to query"""
        if not search_term:
            return query
        
        # Create OR conditions for search fields
        search_conditions = []
        for field in search_fields:
            column = getattr(model_class, field)
            search_conditions.append(column.ilike(f"%{search_term}%"))
        
        return query.filter(or_(*search_conditions))
    
    @staticmethod
    def add_date_range_filter(query: Query, date_column, start_date: Optional[Any] = None,
                            end_date: Optional[Any] = None) -> Query:
        """Add date range filter to query"""
        if start_date:
            query = query.filter(date_column >= start_date)
        if end_date:
            query = query.filter(date_column <= end_date)
        
        return query
    
    @staticmethod
    def add_status_filter(query: Query, status_column, statuses: List[str]) -> Query:
        """Add status filter to query"""
        if statuses:
            query = query.filter(status_column.in_(statuses))
        
        return query
    
    @staticmethod
    def optimize_aggregation_query(query: Query, group_by_fields: List[str]) -> Query:
        """Optimize aggregation queries"""
        # Add proper indexing hints for aggregation
        for field in group_by_fields:
            query = query.add_column(func.count().label(f'count_{field}'))
        
        return query.group_by(*[getattr(query.column_descriptions[0]['type'], field) 
                               for field in group_by_fields])

class BatchProcessor:
    """Process large datasets in batches for better memory usage"""
    
    @staticmethod
    async def process_in_batches(query_func, batch_size: int = 1000, 
                               process_func: Optional[Callable] = None):
        """Process query results in batches"""
        offset = 0
        
        while True:
            # Get batch
            batch_query = query_func().offset(offset).limit(batch_size)
            
            with SessionLocal() as session:
                batch = session.execute(batch_query).fetchall()
                
                if not batch:
                    break
                
                # Process batch
                if process_func:
                    for item in batch:
                        process_func(item)
                
                offset += batch_size
    
    @staticmethod
    def stream_large_result(query: Query, chunk_size: int = 1000):
        """Stream large query results to avoid memory issues"""
        offset = 0
        
        while True:
            chunk = query.offset(offset).limit(chunk_size).all()
            
            if not chunk:
                break
            
            yield from chunk
            offset += chunk_size
```

## 4. Load Balancing & Scaling

### 4.1 Load balancer configuration
```yaml
# nginx/load-balancer.conf
upstream api_backend {
    # Backend servers
    server api1.api-centrum.sk:8000 max_fails=3 fail_timeout=30s;
    server api2.api-centrum.sk:8000 max_fails=3 fail_timeout=30s;
    server api3.api-centrum.sk:8000 max_fails=3 fail_timeout=30s;
    
    # Load balancing method
    least_conn;  # Use least connections algorithm
    
    # Health check
    health_check;
}

upstream ssl_backend {
    server ssl1.api-centrum.sk:8000 max_fails=3 fail_timeout=30s;
    server ssl2.api-centrum.sk:8000 max_fails=3 fail_timeout=30s;
    
    ip_hash;  # Sticky sessions for SSL operations
}

server {
    listen 80;
    server_name api-centrum.sk;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api-centrum.sk;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/api-centrum.sk.crt;
    ssl_certificate_key /etc/ssl/private/api-centrum.sk.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=ssl:10m rate=5r/s;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # SSL specific endpoints
    location /api/ssl/ {
        limit_req zone=ssl burst=10 nodelay;
        
        proxy_pass http://ssl_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Longer timeouts for SSL operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://api_backend;
    }
    
    # Monitoring endpoint
    location /metrics {
        access_log off;
        proxy_pass http://api_backend;
    }
}
```

### 4.2 Horizontal scaling service
```python
# app/scaling/services.py
"""
Horizontal scaling and load distribution services
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import psutil
import socket

class ServerStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    UNKNOWN = "unknown"

@dataclass
class ServerInfo:
    host: str
    port: int
    status: ServerStatus
    load: float  # CPU load percentage
    memory: float  # Memory usage percentage
    response_time: float  # Average response time
    active_connections: int
    last_check: float

class LoadBalancer:
    """Load balancer for distributing requests across multiple servers"""
    
    def __init__(self, servers: List[Dict[str, Any]]):
        self.servers = {
            f"{server['host']}:{server['port']}": ServerInfo(
                host=server['host'],
                port=server['port'],
                status=ServerStatus.UNKNOWN,
                load=0.0,
                memory=0.0,
                response_time=0.0,
                active_connections=0,
                last_check=0.0
            )
            for server in servers
        }
        self.current_server_index = 0
        self.health_check_interval = 30  # seconds
    
    async def get_healthy_server(self) -> Optional[ServerInfo]:
        """Get the best available server using least connections algorithm"""
        healthy_servers = [
            server for server in self.servers.values()
            if server.status == ServerStatus.HEALTHY
        ]
        
        if not healthy_servers:
            return None
        
        # Sort by active connections (least connections algorithm)
        healthy_servers.sort(key=lambda s: s.active_connections)
        return healthy_servers[0]
    
    async def get_server_round_robin(self) -> Optional[ServerInfo]:
        """Get server using round robin algorithm"""
        healthy_servers = [
            server for server in self.servers.values()
            if server.status == ServerStatus.HEALTHY
        ]
        
        if not healthy_servers:
            return None
        
        # Round robin selection
        server = healthy_servers[self.current_server_index % len(healthy_servers)]
        self.current_server_index += 1
        return server
    
    async def health_check(self):
        """Perform health check on all servers"""
        async with aiohttp.ClientSession() as session:
            for server_key, server in self.servers.items():
                try:
                    start_time = time.time()
                    
                    # Health check request
                    async with session.get(
                        f"http://{server.host}:{server.port}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            server.status = ServerStatus.HEALTHY
                            server.response_time = response_time
                            server.last_check = time.time()
                        else:
                            server.status = ServerStatus.UNHEALTHY
                    
                    # Get server metrics
                    async with session.get(
                        f"http://{server.host}:{server.port}/metrics",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as metrics_response:
                        if metrics_response.status == 200:
                            metrics = await metrics_response.json()
                            server.load = metrics.get('cpu_load', 0.0)
                            server.memory = metrics.get('memory_usage', 0.0)
                            server.active_connections = metrics.get('active_connections', 0)
                
                except Exception as e:
                    server.status = ServerStatus.UNHEALTHY
                    print(f"Health check failed for {server_key}: {e}")
    
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        while True:
            await self.health_check()
            await asyncio.sleep(self.health_check_interval)
    
    def get_load_distribution(self) -> Dict[str, Any]:
        """Get current load distribution"""
        total_connections = sum(server.active_connections for server in self.servers.values())
        
        distribution = {}
        for server_key, server in self.servers.items():
            distribution[server_key] = {
                'status': server.status.value,
                'load': server.load,
                'memory': server.memory,
                'response_time': server.response_time,
                'active_connections': server.active_connections,
                'connection_percentage': (server.active_connections / total_connections * 100) if total_connections > 0 else 0
            }
        
        return distribution

class AutoScaler:
    """Automatic scaling based on load metrics"""
    
    def __init__(self, min_instances: int = 2, max_instances: int = 10, 
                 scale_up_threshold: float = 70.0, scale_down_threshold: float = 30.0):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        
        self.current_instances = min_instances
        self.scaling_cooldown = 300  # 5 minutes
        self.last_scale_time = 0
    
    async def check_scaling_requirements(self, load_metrics: Dict[str, Any]) -> Optional[str]:
        """Check if scaling is required"""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_scale_time < self.scaling_cooldown:
            return None
        
        # Calculate average load
        total_load = sum(server['load'] for server in load_metrics.values())
        avg_load = total_load / len(load_metrics) if load_metrics else 0
        
        # Determine scaling action
        if avg_load > self.scale_up_threshold and self.current_instances < self.max_instances:
            self.current_instances += 1
            self.last_scale_time = current_time
            return "scale_up"
        
        elif avg_load < self.scale_down_threshold and self.current_instances > self.min_instances:
            self.current_instances -= 1
            self.last_scale_time = current_time
            return "scale_down"
        
        return None
    
    async def scale_instances(self, action: str, orchestrator):
        """Scale instances up or down"""
        if action == "scale_up":
            print(f"Scaling up to {self.current_instances} instances")
            await orchestrator.scale_up(self.current_instances)
        
        elif action == "scale_down":
            print(f"Scaling down to {self.current_instances} instances")
            await orchestrator.scale_down(self.current_instances)

class ServerOrchestrator:
    """Orchestrate server instances"""
    
    def __init__(self):
        self.active_instances = []
    
    async def scale_up(self, target_count: int):
        """Scale up by starting new instances"""
        # This would integrate with container orchestration (Docker Swarm, Kubernetes)
        # For now, just simulate
        print(f"Starting new instances to reach {target_count}")
    
    async def scale_down(self, target_count: int):
        """Scale down by stopping instances"""
        # This would integrate with container orchestration
        print(f"Stopping instances to reach {target_count}")
    
    async def get_instance_metrics(self) -> Dict[str, Any]:
        """Get metrics from all instances"""
        # This would collect metrics from monitoring system
        return {
            'instance_count': len(self.active_instances),
            'total_cpu': psutil.cpu_percent(),
            'total_memory': psutil.virtual_memory().percent,
            'network_io': psutil.net_io_counters()
        }
```

## 5. Monitoring & Profiling

### 5.1 Performance monitoring
```python
# app/monitoring/performance.py
"""
Performance monitoring and profiling
"""

import time
import asyncio
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import cProfile
import pstats
import io
from contextlib import contextmanager

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict[str, str] = None

@dataclass
class RequestMetric:
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: float
    user_id: Optional[int] = None
    ip_address: Optional[str] = None

class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = deque(maxlen=10000)  # Keep last 10k metrics
        self.request_metrics = deque(maxlen=10000)
        self.cpu_samples = deque(maxlen=100)
        self.memory_samples = deque(maxlen=100)
        self.active_requests = 0
        
        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitoring_thread.start()
    
    def record_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      response_time: float, user_id: Optional[int] = None,
                      ip_address: Optional[str] = None):
        """Record a request metric"""
        request_metric = RequestMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            timestamp=time.time(),
            user_id=user_id,
            ip_address=ip_address
        )
        self.request_metrics.append(request_metric)
    
    @contextmanager
    def measure_operation(self, operation_name: str, tags: Dict[str, str] = None):
        """Context manager to measure operation performance"""
        start_time = time.perf_counter()
        self.active_requests += 1
        
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            self.active_requests -= 1
            
            self.record_metric(
                name=f"operation.{operation_name}",
                value=duration,
                unit="seconds",
                tags=tags
            )
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percentage': memory.percent
        }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage"""
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percentage': disk.percent
        }
    
    def get_network_stats(self) -> Dict[str, float]:
        """Get network statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    
    def _background_monitor(self):
        """Background monitoring thread"""
        while True:
            try:
                # Sample CPU and memory
                cpu_usage = self.get_cpu_usage()
                memory_usage = self.get_memory_usage()
                
                self.cpu_samples.append(cpu_usage)
                self.memory_samples.append(memory_usage['percentage'])
                
                # Record system metrics
                self.record_metric("system.cpu", cpu_usage, "percentage")
                self.record_metric("system.memory", memory_usage['percentage'], "percentage")
                self.record_metric("system.active_requests", self.active_requests, "count")
                
                time.sleep(10)  # Sample every 10 seconds
            
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(10)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        # Calculate request statistics
        recent_requests = [r for r in self.request_metrics 
                          if time.time() - r.timestamp < 300]  # Last 5 minutes
        
        if recent_requests:
            avg_response_time = sum(r.response_time for r in recent_requests) / len(recent_requests)
            error_rate = sum(1 for r in recent_requests if r.status_code >= 400) / len(recent_requests)
            rps = len(recent_requests) / 300  # Requests per second
        else:
            avg_response_time = 0
            error_rate = 0
            rps = 0
        
        # Calculate system statistics
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        avg_memory = sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
        
        return {
            'timestamp': time.time(),
            'system': {
                'cpu_usage': avg_cpu,
                'memory_usage': avg_memory,
                'active_requests': self.active_requests,
                'disk_usage': self.get_disk_usage()
            },
            'requests': {
                'total_requests': len(self.request_metrics),
                'recent_requests': len(recent_requests),
                'avg_response_time': avg_response_time,
                'error_rate': error_rate,
                'requests_per_second': rps
            },
            'top_endpoints': self._get_top_endpoints(recent_requests),
            'status_codes': self._get_status_code_distribution(recent_requests)
        }
    
    def _get_top_endpoints(self, requests: List[RequestMetric]) -> List[Dict]:
        """Get top endpoints by request count"""
        endpoint_counts = defaultdict(int)
        endpoint_times = defaultdict(list)
        
        for req in requests:
            endpoint_counts[req.endpoint] += 1
            endpoint_times[req.endpoint].append(req.response_time)
        
        top_endpoints = []
        for endpoint, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            avg_time = sum(endpoint_times[endpoint]) / len(endpoint_times[endpoint])
            top_endpoints.append({
                'endpoint': endpoint,
                'request_count': count,
                'avg_response_time': avg_time
            })
        
        return top_endpoints
    
    def _get_status_code_distribution(self, requests: List[RequestMetric]) -> Dict[str, int]:
        """Get status code distribution"""
        status_counts = defaultdict(int)
        for req in requests:
            status_counts[str(req.status_code)] += 1
        return dict(status_counts)

class Profiler:
    """Performance profiler for detailed analysis"""
    
    def __init__(self):
        self.profiles = {}
    
    @contextmanager
    def profile_function(self, function_name: str):
        """Profile a function execution"""
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            yield
        finally:
            profiler.disable()
            
            # Save profile stats
            stats_stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
            
            self.profiles[function_name] = stats_stream.getvalue()
    
    def get_profile(self, function_name: str) -> Optional[str]:
        """Get profile for a function"""
        return self.profiles.get(function_name)
    
    def get_all_profiles(self) -> Dict[str, str]:
        """Get all profiles"""
        return self.profiles
    
    def clear_profiles(self):
        """Clear all profiles"""
        self.profiles.clear()
```

## 6. Implementation Steps

### 6.1 Week 1: Performance Analysis
- [ ] Implement performance analyzer
- [ ] Set up monitoring and profiling
- [ ] Identify current bottlenecks
- [ ] Create performance baseline

### 6.2 Week 2: Caching Implementation
- [ ] Set up Redis caching service
- [ ] Implement domain caching
- [ ] Implement SSL caching
- [ ] Add cache invalidation strategies

### 6.3 Week 3: Database Optimization
- [ ] Configure optimized database connections
- [ ] Create performance indexes
- [ ] Implement query optimization
- [ ] Set up batch processing

### 6.4 Week 4: Load Balancing
- [ ] Configure nginx load balancer
- [ ] Implement load balancer service
- [ ] Set up health monitoring
- [ ] Configure auto-scaling

### 6.5 Week 5: Monitoring & Alerting
- [ ] Implement performance monitoring
- [ ] Set up alerting for performance issues
- [ ] Create performance dashboards
- [ ] Configure log aggregation

### 6.6 Week 6: Optimization & Testing
- [ ] Load testing and stress testing
- [ ] Performance tuning based on results
- [ ] Optimize identified bottlenecks
- [ ] Document performance improvements

## 7. Best Practices

### 7.1 Caching best practices
- **Cache invalidation**: Implement proper cache invalidation strategies
- **Cache warming**: Pre-populate cache with frequently accessed data
- **Cache layers**: Use multiple cache layers (L1, L2, CDN)
- **Cache monitoring**: Monitor cache hit rates and performance
- **Graceful degradation**: Handle cache failures gracefully

### 7.2 Database optimization best practices
- **Proper indexing**: Create indexes for frequently queried columns
- **Query optimization**: Optimize slow queries and avoid N+1 problems
- **Connection pooling**: Use connection pooling for better performance
- **Batch operations**: Use batch operations for bulk data processing
- **Database monitoring**: Monitor database performance and resource usage

### 7.3 Load balancing best practices
- **Health checks**: Implement proper health checks for backend servers
- **Load distribution**: Use appropriate load balancing algorithms
- **Session persistence**: Handle session persistence when needed
- **Failover**: Implement automatic failover mechanisms
- **Monitoring**: Monitor load balancer performance and health

### 7.4 Performance monitoring best practices
- **Key metrics**: Monitor key performance indicators (KPIs)
- **Alerting**: Set up alerts for performance degradation
- **Trending**: Track performance trends over time
- **Profiling**: Use profiling tools for detailed analysis
- **Capacity planning**: Use monitoring data for capacity planning

Tento blueprint poskytuje komplexný návod na optimalizáciu výkonu API Centrum Backend systému.