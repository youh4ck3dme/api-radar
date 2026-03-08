# test_e2e_sentinel.py
import os
import sys
import time
import json
import sqlite3
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db import SessionLocal, engine
from app.radar.models import PushSubscription, ObservedEndpoint, DocumentedEndpoint, Base
from app.radar.scanner import update_endpoint

def setup_test_env():
    print("--- Setting up E2E Sentinel Test Environment ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Ensure no previous mock data for this endpoint exists
    db.query(ObservedEndpoint).filter(ObservedEndpoint.endpoint == "/api/shadow/test").delete()
    db.query(DocumentedEndpoint).filter(DocumentedEndpoint.endpoint == "/api/shadow/test").delete()
    
    # 2. Add a DUMMY Push Subscription if none exists
    # If the user hasn't subscribed yet, we need at least one record to trigger the dispatch logic
    existing_sub = db.query(PushSubscription).first()
    if not existing_sub:
        print("Adding dummy subscription for test purposes...")
        dummy = PushSubscription(
            endpoint="https://fcm.googleapis.com/fcm/send/DUMMY_TOKEN_123",
            p256dh="BM_DUMMY_KEY_BLABLA",
            auth="DUMMY_AUTH_SECRET"
        )
        db.add(dummy)
    
    db.commit()
    db.close()
    print("Test environment ready.")

def simulate_attack():
    print("\n--- Simulating Shadow API Discovery ---")
    # This calls the actual logic that the scanner uses
    # We simulate discovering a NEW shadow endpoint
    method = "GET"
    endpoint = "/api/shadow/test"
    
    print(f"Triggering update_endpoint for: {method} {endpoint}")
    update_endpoint(method, endpoint)
    print("Discovery logic executed.")

def verify_results():
    print("\n--- Verifying Database State ---")
    db = SessionLocal()
    obs = db.query(ObservedEndpoint).filter(ObservedEndpoint.endpoint == "/api/shadow/test").first()
    
    if obs and obs.is_shadow:
        print(f"✅ Success: ObservedEndpoint record created and marked as SHADOW.")
        print(f"   Count: {obs.count}, Last Seen: {obs.last_seen}")
    else:
        print("❌ Failure: Shadow endpoint not found or incorrectly flagged.")
    
    db.close()

if __name__ == "__main__":
    try:
        setup_test_env()
        simulate_attack()
        verify_results()
        print("\nNOTE: Check the console output above for 'Push failed' messages.")
        print("Since we used a DUMMY_TOKEN, a 400/410 error from FCM/WebPush is EXPECTED and confirms the dispatch logic fired.")
    except Exception as e:
        print(f"ERROR during E2E test: {e}")
        import traceback
        traceback.print_exc()
