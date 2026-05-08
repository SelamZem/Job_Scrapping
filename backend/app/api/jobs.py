from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job import Job
from app.scrapers import RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper, RSSRemoteOKScraper, LandingJobsScraper, GitHubJobsScraper, StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper
from app.services import TagService
from pydantic import BaseModel, Field

router = APIRouter()

class JobSearchRequest(BaseModel):
    query: str
    location: str = ""

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    url: str
    source: str
    tags: List[str] = Field(default_factory=list)

@router.get("/")
async def get_jobs(db: Session = Depends(get_db), skip: int = 0, limit: int = 12):
    # Get total count for pagination
    total_count = db.query(Job).count()

    # Get paginated jobs, sorted by scraped_date (most recent first)
    jobs = db.query(Job).order_by(Job.scraped_date.desc()).offset(skip).limit(limit).all()

    return {
        "total": total_count,
        "jobs": [
            JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                description=job.description,
                salary=job.salary,
                url=job.url,
                source=job.source,
                tags=[tag.name for tag in job.tags]
            )
            for job in jobs
        ]
    }

@router.post("/scrape")
async def scrape_jobs(request: JobSearchRequest, db: Session = Depends(get_db)):
    # Try multiple job APIs and RSS feeds for real data
    api_scrapers = [
        ('Remotive', RemotiveAPIScraper()),
        ('Arbeitnow', ArbeitnowAPIScraper()),
        ('We Work Remotely RSS', RSSWeWorkRemotelyScraper()),
        ('RemoteOK RSS', RSSRemoteOKScraper()),
        ('Landing.jobs', LandingJobsScraper()),
        ('GitHub Jobs', GitHubJobsScraper()),
        ('Stack Overflow', StackOverflowScraper()),
        ('Authentic Jobs', AuthenticJobsScraper()),
        ('EuroJobs', EuroJobsScraper())
    ]
    
    tag_service = TagService(db)
    saved_jobs = []
    jobs_from_real_scrapers = 0
    sources_used = []
    
    for source_name, scraper in api_scrapers:
        print(f"\n=== Scraping from {source_name} ===")
        try:
            jobs_data = scraper.scrape_jobs(request.query, request.location, max_pages=1)
            
            if jobs_data:
                sources_used.append(source_name)
                
                for job_data in jobs_data:
                    job_data['source'] = source_name.lower().replace(' ', '_')
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
                    
                    saved_jobs.append(job)
                    jobs_from_real_scrapers += 1
                    print(f"  Saved: {job.title} at {job.company}")
            
        except Exception as e:
            print(f"Error with {source_name} scraper: {e}")
            continue
    
    if sources_used:
        source_type = f"{', '.join(sources_used)} (real APIs)"
    else:
        source_type = "no sources available"
    
    return {"message": f"Scraped and saved {len(saved_jobs)} jobs from {source_type}", "count": len(saved_jobs)}

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        salary=job.salary,
        url=job.url,
        source=job.source,
        tags=[tag.name for tag in job.tags]
    )
