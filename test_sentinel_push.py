# test_sentinel_push.py
import os
import json
import sqlite3
from pywebpush import webpush, WebPushException

# Config from .env
VAPID_PRIVATE_KEY = "p6FDBFiKUn1nIDFhfLL9PYux4eOtX6XdwK2BsilJ9ZyAxYXyy_T2LseHjrV-l3cCtgb"
VAPID_PUBLIC_KEY = "BK4S7bHiu9pp_dBJRtvROA6mXTo7e2BPlPbwKroK4ZpIMu_-bvp"
VAPID_MAILTO = "mailto:admin@nexify-studio.tech"

def test_mock_push():
    print("--- Sentinel Push System Manual Test ---")
    
    # 1. Setup Mock DB
    db_path = "backend/test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for subscriptions
    try:
        cursor.execute("SELECT endpoint, p256dh, auth FROM push_subscriptions")
        subs = cursor.fetchall()
    except Exception as e:
        print(f"Error reading subscriptions: {e}")
        return

    if not subs:
        print("❌ No active subscriptions found in DB. Please 'Enable Sentinel' in the UI first.")
        # Create a dummy one for testing the library integration if needed
        print("Creating dummy subscription for library validation...")
        dummy_sub = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/fake-endpoint",
            "keys": {"p256dh": "fake-p256dh", "auth": "fake-auth"}
        }
    else:
        print(f"✅ Found {len(subs)} subscription(s). Sending test alerts...")

    for sub_data in subs:
        endpoint, p256dh, auth = sub_data
        print(f"Targeting: {endpoint[:30]}...")
        
        try:
            webpush(
                subscription_info={
                    "endpoint": endpoint,
                    "keys": {"p256dh": p256dh, "auth": auth}
                },
                data=json.dumps({
                    "title": "🧪 SENTINEL TEST", 
                    "body": "Shadow API discovery engine is active. System Integrity: 100%"
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_MAILTO}
            )
            print("🚀 Push sent successfully (to service worker)!")
        except WebPushException as ex:
            print(f"⚠️ Push attempt resulted in status {ex.response.status_code if ex.response else 'N/A'}")
            print(f"Details: {ex}")

    conn.close()

if __name__ == "__main__":
    test_mock_push()
