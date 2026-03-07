import os
import time
import sqlite3
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(PROJECT_ROOT, "scanner", "access.log")
DB_FILE = os.path.join(PROJECT_ROOT, "api_radar.db")

DUMMY_LOGS = [
    '88.212.19.47 - - [08/Mar/2026:00:07:21 +0100] "GET /api/users HTTP/1.1" 200',
    '88.212.19.47 - - [08/Mar/2026:00:07:22 +0100] "POST /api/login HTTP/1.1" 201',
    '88.212.19.47 - - [08/Mar/2026:00:07:23 +0100] "GET /api/users HTTP/1.1" 200',
    '88.212.19.47 - - [08/Mar/2026:00:07:24 +0100] "GET /api/dashboard/stats HTTP/1.1" 200',
]

def run_test():
    # 1. Start the scanner in the background
    print("Starting scanner...")
    scanner_env = os.environ.copy()
    scanner_env["PYTHONPATH"] = PROJECT_ROOT
    process = subprocess.Popen(["python", "scanner/nginx_log_collector.py"], cwd=PROJECT_ROOT, env=scanner_env)
    
    time.sleep(1) # Give it time to initialize
    
    # 2. Append logs
    print("Appending dummy logs...")
    with open(LOG_FILE, "a") as f:
        for log in DUMMY_LOGS:
            f.write(log + "\n")
            f.flush()
            time.sleep(0.5)
            
    time.sleep(1) # Let the scanner process
    
    # 3. Check DB
    print("Checking database...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT method, endpoint, count FROM endpoints")
    rows = cursor.fetchall()
    conn.close()
    
    print("\nDiscovered Endpoints in DB:")
    for method, endpoint, count in rows:
        print(f"{method} {endpoint} -> {count}")
        
    # 4. Cleanup
    process.terminate()
    print("\nTest completed.")

if __name__ == "__main__":
    run_test()
