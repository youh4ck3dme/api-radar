# backend/app/radar/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from ..db import Base

class ObservedEndpoint(Base):
    __tablename__ = "observed_endpoints"
    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(512), nullable=False)
    count = Column(Integer, default=1)
    is_shadow = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentedEndpoint(Base):
    __tablename__ = "documented_endpoints"
    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(512), nullable=False)
