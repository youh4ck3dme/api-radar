# backend/app/radar/routes.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..db import get_db
from .models import ObservedEndpoint, DocumentedEndpoint, PushSubscription
from .scanner import run_scanner_background
import os
from pydantic import BaseModel

class SubscriptionInfo(BaseModel):
    endpoint: str
    keys: dict

router = APIRouter()

@router.get("/radar/vapid-key")
def get_vapid_key():
    return {"publicKey": os.getenv("VAPID_PUBLIC_KEY")}

@router.post("/radar/subscribe")
def subscribe_notifications(sub: SubscriptionInfo, db: Session = Depends(get_db)):
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == sub.endpoint).first()
    if not existing:
        new_sub = PushSubscription(
            endpoint=sub.endpoint,
            p256dh=sub.keys.get("p256dh"),
            auth=sub.keys.get("auth")
        )
        db.add(new_sub)
        db.commit()
    return {"status": "Subscribed"}

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
