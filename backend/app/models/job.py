from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Many-to-many relationship table for jobs and tags
job_tags = Table(
    'job_tags',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(String(100), nullable=True)
    url = Column(String(500), nullable=False, unique=True)
    source = Column(String(100), nullable=False)  # e.g., 'linkedin', 'indeed', 'glassdoor'
    posted_date = Column(DateTime, nullable=True)
    scraped_date = Column(DateTime, server_default=func.now())
    
    tags = relationship("Tag", secondary=job_tags, back_populates="jobs")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False)  # e.g., 'skill', 'role', 'industry'
    
    jobs = relationship("Job", secondary=job_tags, back_populates="tags")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True)
    preferred_tags = Column(Text, nullable=True)  # JSON string of tag IDs
    preferred_locations = Column(Text, nullable=True)  # JSON string of locations
    saved_jobs = Column(Text, nullable=True)  # JSON string of job IDs
