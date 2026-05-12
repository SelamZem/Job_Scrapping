#!/usr/bin/env python3
"""
Add performance indexes to improve job loading speed
"""

from sqlalchemy import text
from app.database import engine

def add_performance_indexes():
    """Add indexes to improve query performance"""
    
    indexes = [
        # Composite index for title search (most common search field)
        "CREATE INDEX IF NOT EXISTS idx_jobs_title_gin ON jobs USING gin(to_tsvector('english', title))",
        
        # Composite index for company search
        "CREATE INDEX IF NOT EXISTS idx_jobs_company_gin ON jobs USING gin(to_tsvector('english', company))",
        
        # Composite index for location search
        "CREATE INDEX IF NOT EXISTS idx_jobs_location_gin ON jobs USING gin(to_tsvector('english', location))",
        
        # Composite index for search across multiple fields
        "CREATE INDEX IF NOT EXISTS idx_jobs_search_gin ON jobs USING gin(to_tsvector('english', title || ' ' || company || ' ' || description))",
        
        # Index for ordering by dates
        "CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC NULLS LAST)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date ON jobs(scraped_date DESC NULLS LAST)",
        
        # Composite index for date ordering
        "CREATE INDEX IF NOT EXISTS idx_jobs_date_order ON jobs(coalesce(posted_date, scraped_date) DESC)",
        
        # Index for tag names in job_tags table
        "CREATE INDEX IF NOT EXISTS idx_job_tags_tag_id ON job_tags(tag_id)",
        "CREATE INDEX IF NOT EXISTS idx_job_tags_job_id ON job_tags(job_id)",
        
        # Index for tag categories
        "CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category)",
        "CREATE INDEX IF NOT EXISTS idx_tags_name_category ON tags(name, category)",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                print(f"✅ Created index: {index_sql[:50]}...")
            except Exception as e:
                print(f"⚠️ Index creation failed: {e}")
    
    print("🚀 Performance indexes added successfully!")

if __name__ == "__main__":
    add_performance_indexes()
