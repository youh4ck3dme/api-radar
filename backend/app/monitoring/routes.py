# backend/app/monitoring/routes.py

from fastapi import APIRouter, Depends
from .tasks import check_ssl_expiry, dns_health_check
from ..auth_neon import get_current_user_or_neon
from ..models import User

router = APIRouter(tags=["Monitoring"])

@router.get("/monitoring/ssl/{domain}")
async def get_ssl_status(domain: str, current_user: User = Depends(get_current_user_or_neon)):
    return check_ssl_expiry(domain)

@router.get("/monitoring/dns/{domain}")
async def get_dns_status(domain: str, current_user: User = Depends(get_current_user_or_neon)):
    return dns_health_check(domain)

@router.get("/monitoring/health-report")
async def get_health_report(current_user: User = Depends(get_current_user_or_neon)):
    # Tu by sme v reálnej aplikácii prešli cez všetky domény v DB
    # Pre demo účely vrátime statický zoznam alebo prázdny
    return {"status": "monitoring active", "checks": ["ssl", "dns"]}
