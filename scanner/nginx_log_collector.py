import sqlite3
import os
import sys
import time

# Add the parent directory to sys.path to import the parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser.api_parser import parse_nginx_log_line

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api_radar.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            endpoint TEXT,
            count INTEGER DEFAULT 0,
            UNIQUE(method, endpoint)
        )
    ''')
    conn.commit()
    conn.close()

def update_endpoint(method, endpoint):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO endpoints (method, endpoint, count)
        VALUES (?, ?, 1)
        ON CONFLICT(method, endpoint) DO UPDATE SET count = count + 1
    ''', (method, endpoint))
    conn.commit()
    conn.close()
    print(f"Updated: {method} {endpoint}")

def collect_logs(log_file_path):
    print(f"Starting log collection from {log_file_path}...")
    init_db()
    
    # Simple tail-like behavior
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as f:
            f.write("") # Create empty file if not exists

    with open(log_file_path, "r") as f:
        # Go to the end of the file
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1) # Sleep briefly to wait for new lines
                continue
            
            method, endpoint = parse_nginx_log_line(line)
            if method and endpoint:
                update_endpoint(method, endpoint)

if __name__ == "__main__":
    # For testing, we can point to a local file
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "access.log")
    collect_logs(log_path)
