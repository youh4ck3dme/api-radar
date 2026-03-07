from fastapi.testclient import TestClient
from app.main import app

def check_health():
    client = TestClient(app)
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

if __name__ == "__main__":
    check_health()
