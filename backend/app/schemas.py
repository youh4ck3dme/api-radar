# backend/app/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class DomainBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "example.sk"})
    description: Optional[str] = None


class DomainCreate(DomainBase):
    pass


class DomainUpdate(DomainBase):
    pass


class SSLCertRequest(BaseModel):
    domain: str
    email: EmailStr


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    totp: Optional[str] = None

