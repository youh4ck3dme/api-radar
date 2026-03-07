# backend/app/crud.py

from sqlalchemy.orm import Session
from . import models, auth
from typing import Optional


class CRUDUser:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def create(db: Session, email: str, password: str, role: Optional[models.Role] = None) -> models.User:
        hashed = auth.hash_password(password)
        user = models.User(email=email, hashed_password=hashed, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def enable_2fa(db: Session, user: models.User, secret: str):
        user.totp_secret = secret
        user.two_factor_enabled = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def disable_2fa(db: Session, user: models.User):
        user.totp_secret = None
        user.two_factor_enabled = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


class CRUDRole:
    @staticmethod
    def get_by_name(db: Session, name: str):
        return db.query(models.Role).filter(models.Role.name == name).first()

    @staticmethod
    def create(db: Session, name: str):
        role = models.Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

