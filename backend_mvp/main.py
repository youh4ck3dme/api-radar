from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(title="API Radar Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api_radar.db")

@app.get("/endpoints")
def get_endpoints():
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT method, endpoint, count, is_shadow FROM endpoints ORDER BY is_shadow DESC, count DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [{"method": r[0], "endpoint": r[1], "count": r[2], "is_shadow": bool(r[3])} for r in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
