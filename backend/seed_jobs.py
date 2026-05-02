import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.job import Job, Tag
from app.scrapers import IndeedScraper
from app.services import TagService

def seed_jobs():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    scraper = IndeedScraper()
    tag_service = TagService(db)
    
    print("Scraping jobs from Indeed...")
    # Scrape some common tech jobs
    search_queries = [
        ("Software Engineer", "Remote"),
        ("Python Developer", "Remote"),
        ("React Developer", "Remote"),
        ("Data Scientist", "Remote"),
        ("Full Stack Developer", "Remote")
    ]
    
    total_saved = 0
    
    for query, location in search_queries:
        print(f"\nScraping: {query} in {location}")
        try:
            jobs_data = scraper.scrape_jobs(query, location)
            print(f"Found {len(jobs_data)} jobs")
            
            for job_data in jobs_data:
                existing_job = db.query(Job).filter(Job.url == job_data['url']).first()
                if existing_job:
                    continue
                
                job = Job(**job_data)
                db.add(job)
                db.commit()
                db.refresh(job)
                
                tags = tag_service.extract_tags_from_job(job)
                job.tags = tags
                db.commit()
                
                total_saved += 1
                print(f"  Saved: {job.title} at {job.company}")
                
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    print(f"\n✓ Total jobs saved: {total_saved}")
    
    # Show tag statistics
    tags = db.query(Tag).all()
    print(f"✓ Total tags created: {len(tags)}")
    
    db.close()
    print("\nDatabase seeded successfully!")

if __name__ == "__main__":
    seed_jobs()
