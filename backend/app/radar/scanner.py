# backend/app/radar/scanner.py

import time
import os
import sys
from sqlalchemy.orm import Session
from .models import ObservedEndpoint, DocumentedEndpoint
from ..db import SessionLocal
import re

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
