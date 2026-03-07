import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    # Basic check that Prometheus metrics are present
    assert b"process_cpu_seconds_total" in response.content or b"http_requests_total" in response.content

def test_ssl_monitoring_endpoint():
    # Using example.com which should have a valid SSL certificate
    response = client.get("/api/monitoring/ssl/example.com")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "expiry_date" in json_data
    assert "days_remaining" in json_data

def test_dns_monitoring_endpoint():
    response = client.get("/api/monitoring/dns/example.com")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "ip" in json_data
