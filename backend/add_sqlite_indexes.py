#!/usr/bin/env python3
"""
Add SQLite-compatible performance indexes
"""

from sqlalchemy import text
from app.database import engine

def add_sqlite_indexes():
    """Add SQLite-compatible indexes to improve query performance"""
    
    indexes = [
        # Index for title search
        "CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)",
        
        # Index for company search
        "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)",
        
        # Index for location search
        "CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)",
        
        # Composite index for date ordering (most important for pagination)
        "CREATE INDEX IF NOT EXISTS idx_jobs_date_order ON jobs(coalesce(posted_date, scraped_date) DESC)",
        
        # Index for posted_date
        "CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC)",
        
        # Index for scraped_date
        "CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date ON jobs(scraped_date DESC)",
        
        # Index for source
        "CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)",
        
        # Indexes for job_tags table
        "CREATE INDEX IF NOT EXISTS idx_job_tags_tag_id ON job_tags(tag_id)",
        "CREATE INDEX IF NOT EXISTS idx_job_tags_job_id ON job_tags(job_id)",
        
        # Indexes for tags table
        "CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category)",
        "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)",
        "CREATE INDEX IF NOT EXISTS idx_tags_name_category ON tags(name, category)",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                print(f"✅ Created: {index_sql}")
            except Exception as e:
                print(f"⚠️ Failed: {e}")
    
    print("🚀 SQLite performance indexes added!")

if __name__ == "__main__":
    add_sqlite_indexes()
