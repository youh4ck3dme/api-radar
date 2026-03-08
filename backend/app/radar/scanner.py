# backend/app/radar/scanner.py

import time
import os
import sys
from sqlalchemy.orm import Session
from .models import ObservedEndpoint, DocumentedEndpoint
from ..db import SessionLocal
import re
import json
from pywebpush import webpush, WebPushException
from .models import ObservedEndpoint, DocumentedEndpoint, PushSubscription

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_MAILTO = os.getenv("VAPID_MAILTO", "mailto:admin@example.com")

def send_push_notification(db: Session, title, message):
    subs = db.query(PushSubscription).all()
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                },
                data=json.dumps({"title": title, "body": message}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_MAILTO}
            )
        except WebPushException as ex:
            print(f"Push failed: {ex}")
            if ex.response and ex.response.status_code == 410:
                db.delete(sub)
                db.commit()

def parse_nginx_log_line(line):
    match = re.search(r'"([A-Z]+)\s+([^\s?]+)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def update_endpoint(method, endpoint):
    db: Session = SessionLocal()
    try:
        # Check if documented
        is_documented = db.query(DocumentedEndpoint).filter(
            DocumentedEndpoint.method == method,
            DocumentedEndpoint.endpoint == endpoint
        ).first() is not None
        
        is_shadow = not is_documented
        
        obs = db.query(ObservedEndpoint).filter(
            ObservedEndpoint.method == method,
            ObservedEndpoint.endpoint == endpoint
        ).first()
        
        if obs:
            obs.count += 1
            obs.is_shadow = is_shadow
        else:
            obs = ObservedEndpoint(
                method=method,
                endpoint=endpoint,
                count=1,
                is_shadow=is_shadow
            )
            db.add(obs)
            # Sentinel Alert: New Shadow Detected
            if is_shadow:
                send_push_notification(
                    db, 
                    "⚠️ NEW SHADOW API", 
                    f"Detected: {method} {endpoint}"
                )
        
        db.commit()
        print(f"Discovered: {method} {endpoint} [{'SHADOW' if is_shadow else 'KNOWN'}]")
    except Exception as e:
        print(f"Error updating endpoint: {e}")
        db.rollback()
    finally:
        db.close()

def run_scanner_background(log_file_path):
    print(f"Radar Pro Scanner starting on {log_file_path}...")
    if not os.path.exists(log_file_path):
        return
        
    with open(log_file_path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            
            method, endpoint = parse_nginx_log_line(line)
            if method and endpoint:
                update_endpoint(method, endpoint)
