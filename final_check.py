# final_check.py
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db import SessionLocal
from app.radar.models import ObservedEndpoint, PushSubscription

def check():
    db = SessionLocal()
    obs = db.query(ObservedEndpoint).filter(ObservedEndpoint.endpoint == '/api/shadow/test').first()
    subs_count = db.query(PushSubscription).count()
    
    print("\n--- SENTINEL SUITE VERIFICATION ---")
    if obs:
        print(f"Shadow Endpoint Detection: SUCCESS (Found {obs.method} {obs.endpoint})")
        print(f"Shadow Flag: {'CORRECT' if obs.is_shadow else 'FAILED'}")
    else:
        print("Shadow Endpoint Detection: FAILED (No record found)")
        
    print(f"Subscription Storage: {'SUCCESS' if subs_count > 0 else 'EMPTY'} (Count: {subs_count})")
    print("--- END CHECK ---\n")
    db.close()

if __name__ == "__main__":
    check()
