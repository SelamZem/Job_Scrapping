from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
import json

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    saved_jobs = Column(Text, default="[]")  # JSON list of job IDs
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def get_saved_jobs(self) -> list:
        try:
            return json.loads(self.saved_jobs or "[]")
        except Exception:
            return []

    def set_saved_jobs(self, job_ids: list):
        self.saved_jobs = json.dumps(job_ids)
