# backend/scripts/create_admin.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db import SessionLocal, engine, Base
from app import crud, models, auth


def create_admin(email: str, password: str):
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        existing = crud.CRUDUser.get_by_email(db, email)
        if existing:
            print("Admin už existuje.")
            return
        user = crud.CRUDUser.create(db, email, password)
        user.is_superuser = True
        db.add(user)
        db.commit()
        print("Admin vytvorený:", email)
    finally:
        db.close()


if __name__ == "__main__":
    create_admin("admin@example.com", "ChangeMe123!")

