# backend/app/domains/routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..schemas import DomainCreate
from .services import DomainService
from ..auth_neon import get_current_user_or_neon
from ..models import User

router = APIRouter()

@router.get("/domains")
async def get_domains(current_user: User = Depends(get_current_user_or_neon)):
    """Get list of domains from Websupport API"""
    try:
        return DomainService.list_domains()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains")
async def create_domain(domain: DomainCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Create new domain via Websupport API"""
    try:
        res = DomainService.create_domain(domain.model_dump())
        
        # Audit log
        new_log = models.AuditLog(user_id=current_user.id, action="create_domain", detail=f"Created domain {domain.name}")
        db.add(new_log)
        db.commit()
        
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains/{domain_id}")
async def get_domain_details(domain_id: int, current_user: User = Depends(get_current_user_or_neon)):
    """Get domain details from Websupport API"""
    try:
        return DomainService.get_domain_details(domain_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/domains/{domain_id}")
async def delete_domain(domain_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Delete domain via Websupport API"""
    try:
        DomainService.delete_domain(domain_id)
        
        # Audit log
        new_log = models.AuditLog(user_id=current_user.id, action="delete_domain", detail=f"Deleted domain ID {domain_id}")
        db.add(new_log)
        db.commit()
        
        return {"success": True, "message": "Domain deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
