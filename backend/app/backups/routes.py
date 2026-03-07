# backend/app/backups/routes.py

from fastapi import APIRouter, Depends, HTTPException
from ..auth_neon import get_current_user_or_neon
from ..models import User
from .service import BackupService

router = APIRouter(tags=["Backups"])

@router.post("/backups/create")
async def create_backup(current_user: User = Depends(get_current_user_or_neon)):
    result = BackupService.create_backup()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/backups")
async def list_backups(current_user: User = Depends(get_current_user_or_neon)):
    return BackupService.list_backups()

@router.delete("/backups/{filename}")
async def delete_backup(filename: str, current_user: User = Depends(get_current_user_or_neon)):
    result = BackupService.delete_backup(filename)
    if result["status"] == "error":
        raise HTTPException(status_code=result.get("status_code", 404), detail=result["message"])
    return result
