# test_pro_radar.py
import time
import os
import requests
from sqlalchemy.orm import Session
from backend.app.db import SessionLocal, engine, Base
from backend.app.radar.models import ObservedEndpoint, DocumentedEndpoint
from backend.app.radar.scanner import update_endpoint

def setup_test_data():
    db = SessionLocal()
    # Clear existing
    db.query(ObservedEndpoint).delete()
    db.query(DocumentedEndpoint).delete()
    
    # Add documented
    doc1 = DocumentedEndpoint(method="GET", endpoint="/api/users")
    doc2 = DocumentedEndpoint(method="POST", endpoint="/api/login")
    db.add_all([doc1, doc2])
    db.commit()
    db.close()
    print("Test data setup complete.")

def run_simulation():
    print("Simulating API traffic...")
    update_endpoint("GET", "/api/users")
    update_endpoint("POST", "/api/login")
    update_endpoint("GET", "/api/users")
    update_endpoint("GET", "/api/internal/debug") # SHADOW
    update_endpoint("DELETE", "/api/v1/nuke")     # SHADOW

def verify_results():
    db = SessionLocal()
    obs = db.query(ObservedEndpoint).order_by(ObservedEndpoint.count.desc()).all()
    print("\nRadar Pro Discovered Endpoints:")
    for o in obs:
        status = "SHADOW" if o.is_shadow else "DOCUMENTED"
        print(f"{o.method} {o.endpoint} -> {o.count} hits [{status}]")
    db.close()

if __name__ == "__main__":
    setup_test_data()
    run_simulation()
    verify_results()
