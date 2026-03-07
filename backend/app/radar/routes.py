# backend/app/radar/routes.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..db import get_db
from .models import ObservedEndpoint, DocumentedEndpoint
from .scanner import run_scanner_background
import os

router = APIRouter()

@router.get("/radar/endpoints")
def get_discovered_endpoints(db: Session = Depends(get_db)):
    return db.query(ObservedEndpoint).order_by(ObservedEndpoint.is_shadow.desc(), ObservedEndpoint.count.desc()).all()

@router.post("/radar/start")
def start_radar(background_tasks: BackgroundTasks, log_path: str = "/var/log/nginx/access.log"):
    if not os.path.exists(log_path):
        # Fallback for dev if needed
        log_path = os.path.join(os.getcwd(), "scanner", "access.log")
        if not os.path.exists(log_path):
             with open(log_path, "w") as f: f.write("")

    background_tasks.add_task(run_scanner_background, log_path)
    return {"status": "Radar scanner started in background", "log_path": log_path}
