from sqlalchemy import Column, String, Boolean
from app.database import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    key = Column(String(100), primary_key=True)
    value = Column(String(500), nullable=False)
