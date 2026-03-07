# backend/app/backups/service.py

import re
import shutil
from datetime import datetime
from pathlib import Path
from ..config import settings

class BackupService:
    BACKUP_DIR = Path("backups")
    BACKUP_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+\.db$")

    @classmethod
    def ensure_backup_dir(cls) -> Path:
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        return cls.BACKUP_DIR.resolve()

    @classmethod
    def _validate_backup_filename(cls, filename: str) -> bool:
        if not filename:
            return False
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        return bool(cls.BACKUP_FILENAME_PATTERN.fullmatch(filename))

    @classmethod
    def _resolve_backup_path(cls, filename: str) -> Path | None:
        backup_dir = cls.ensure_backup_dir()
        candidate = (backup_dir / filename).resolve()
        try:
            candidate.relative_to(backup_dir)
        except ValueError:
            return None
        return candidate
            
    @classmethod
    def create_backup(cls):
        backup_dir = cls.ensure_backup_dir()
        
        # Get DB path from settings
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite:///"):
            db_path = Path(db_url.replace("sqlite:///", "")).resolve()
        else:
            db_path = Path("test.db").resolve()  # Fallback
            
        if not db_path.exists():
            return {"status": "error", "message": f"Database file not found at {db_path}"}
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.db"
        backup_path = backup_dir / backup_file
        
        try:
            shutil.copy2(db_path, backup_path)
            return {
                "status": "success", 
                "filename": backup_file, 
                "size": backup_path.stat().st_size,
                "timestamp": timestamp
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    @classmethod
    def list_backups(cls):
        backup_dir = cls.ensure_backup_dir()
        backups = []
        for path in backup_dir.iterdir():
            if path.is_file() and cls._validate_backup_filename(path.name):
                backups.append({
                    "filename": path.name,
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                })
        return sorted(backups, key=lambda x: x['modified'], reverse=True)

    @classmethod
    def delete_backup(cls, filename: str):
        if not cls._validate_backup_filename(filename):
            return {
                "status": "error",
                "message": "Invalid backup filename",
                "status_code": 400,
            }

        path = cls._resolve_backup_path(filename)
        if path is None:
            return {
                "status": "error",
                "message": "Invalid backup filename",
                "status_code": 400,
            }

        if path.exists() and path.is_file():
            path.unlink()
            return {"status": "success", "message": f"Backup {filename} deleted"}
        return {"status": "error", "message": "Backup not found", "status_code": 404}
