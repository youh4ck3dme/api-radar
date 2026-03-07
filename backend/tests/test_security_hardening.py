from pathlib import Path

from fastapi.testclient import TestClient

from app.auth import create_access_token
from app.backups.service import BackupService
from app.crud import CRUDUser


def _auth_headers(db_session):
    email = "security@example.com"
    password = "security_password_123"
    user = CRUDUser.get_by_email(db_session, email)
    if not user:
        user = CRUDUser.create(db_session, email, password)
    token = create_access_token(user.email)
    return {"Authorization": f"Bearer {token}"}


def test_sensitive_endpoints_require_auth(client: TestClient):
    checks = [
        ("GET", "/api/backups"),
        ("POST", "/api/backups/create"),
        ("DELETE", "/api/backups/example.db"),
        ("GET", "/api/performance/stats"),
        ("GET", "/api/monitoring/health-report"),
    ]

    for method, path in checks:
        response = client.request(method, path)
        assert response.status_code == 401, f"{method} {path} must require auth"


def test_sensitive_endpoints_work_with_auth(client: TestClient, db_session):
    headers = _auth_headers(db_session)

    assert client.get("/api/backups", headers=headers).status_code == 200
    assert client.get("/api/performance/stats", headers=headers).status_code == 200
    assert client.get("/api/monitoring/health-report", headers=headers).status_code == 200


def test_backup_delete_rejects_path_traversal(client: TestClient, db_session):
    headers = _auth_headers(db_session)
    probe = Path("tmp_traversal_probe.db")
    probe.write_text("probe", encoding="utf-8")

    try:
        response = client.delete(f"/api/backups/..%5C{probe.name}", headers=headers)
        assert response.status_code == 400
        assert "Invalid backup filename" in response.json()["detail"]
        assert probe.exists()
    finally:
        if probe.exists():
            probe.unlink()


def test_backup_delete_allows_valid_filename(client: TestClient, db_session):
    headers = _auth_headers(db_session)
    backup_dir = BackupService.ensure_backup_dir()
    backup_file = backup_dir / "valid_backup.db"
    backup_file.write_text("backup-content", encoding="utf-8")

    response = client.delete("/api/backups/valid_backup.db", headers=headers)

    assert response.status_code == 200
    assert not backup_file.exists()


def test_security_headers_and_csp_are_set(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
    assert "Content-Security-Policy" in response.headers
