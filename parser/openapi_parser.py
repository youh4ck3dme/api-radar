import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api_radar.db")

def import_openapi(file_path):
    """
    Parses a basic OpenAPI JSON file and populates the documented_endpoints table.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        spec = json.load(f)

    paths = spec.get('paths', {})
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documented_endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            endpoint TEXT,
            UNIQUE(method, endpoint)
        )
    ''')
    
    # Optional: Clear existing documentation if you want a fresh sync
    # cursor.execute("DELETE FROM documented_endpoints")

    count = 0
    for path, methods in paths.items():
        for method in methods.keys():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO documented_endpoints (method, endpoint)
                        VALUES (?, ?)
                    ''', (method.upper(), path))
                    count += 1
                except Exception as e:
                    print(f"Error inserting {method} {path}: {e}")

    conn.commit()
    conn.close()
    print(f"Successfully imported {count} documented endpoints.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        import_openapi(sys.argv[1])
    else:
        print("Usage: python openapi_parser.py <path_to_openapi.json>")
