# backend/app/ssl/routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..schemas import SSLCertRequest
from .services import SSLService
from ..auth_neon import get_current_user_or_neon
from ..models import User

router = APIRouter()

@router.post("/ssl/generate")
async def generate_ssl_certificate(req: SSLCertRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Generate SSL certificate for domain"""
    try:
        result = SSLService.generate_ssl_certificate(req.domain, req.email)
        
        # Audit log
        new_log = models.AuditLog(user_id=current_user.id, action="generate_ssl", detail=f"Generated SSL for {req.domain}")
        db.add(new_log)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))