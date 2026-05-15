from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, desc, or_
from typing import List, Optional
from app.database import get_db
from app.models.job import Job, Tag, job_tags
from app.scrapers import RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper, RSSRemoteOKScraper, LandingJobsScraper, GitHubJobsScraper, StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper
from app.services import TagService
from app.services.scraper_monitor import scraper_monitor
import time
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
async def get_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 12,
    search: Optional[str] = None,
    location: Optional[str] = None,
    tag: Optional[List[str]] = Query(default=None)
):
    # Performance timing
    import time
    start_time = time.time()
    
    # Use database directly in production cache handles caching

    # Build base query with eager loading to avoid N+1 problem
    query = db.query(Job).options(selectinload(Job.tags))

    # Search title and company using full-text search (uses GIN index, fast)
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
            )
        )

    # Location filter
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    # Apply tag filter — OR logic: jobs that have ANY of the selected tags
    active_tags = [t.strip() for t in (tag or []) if t and t.strip()]
    if active_tags:
        query = query.filter(
            Job.id.in_(
                db.query(Job.id).join(Job.tags).filter(Tag.name.in_(active_tags))
            )
        )

    # Get total count for pagination
    total_count = query.count()

    # Get paginated jobs with eager loaded tags
    jobs = query.order_by(
        desc(func.coalesce(Job.posted_date, Job.scraped_date))
    ).offset(skip).limit(limit).all()

    result = {
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
                tags=[tag.name for tag in job.tags]  # Now uses eager loaded tags
            )
            for job in jobs
        ]
    }

    # Cache removed - no longer storing results

    # Log performance timing
    end_time = time.time()
    duration = (end_time - start_time) * 1000  # Convert to milliseconds
    print(f"🚀 Jobs API took {duration:.2f}ms - returned {len(result['jobs'])} jobs, total: {result['total']}")

    return result

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
        start_time = time.time()
        try:
            jobs_data = scraper.scrape_jobs(request.query, request.location, max_pages=1)
            duration = time.time() - start_time
            
            # Record in scraper monitor
            scraper_monitor.record_run(
                name=source_name,
                success=len(jobs_data) > 0,
                jobs_found=len(jobs_data),
                duration=round(duration, 2)
            )
            
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
            duration = time.time() - start_time
            # Record failure in scraper monitor
            scraper_monitor.record_run(
                name=source_name,
                success=False,
                jobs_found=0,
                error_message=str(e)[:200],
                duration=round(duration, 2)
            )
            print(f"Error with {source_name} scraper: {e}")
            continue
    
    if sources_used:
        source_type = f"{', '.join(sources_used)} (real APIs)"
    else:
        source_type = "no sources available"

    # Cache removed - no longer invalidating cache

    return {"message": f"Scraped and saved {len(saved_jobs)} jobs from {source_type}", "count": len(saved_jobs)}

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    # Use eager loading to avoid N+1 query
    job = db.query(Job).options(selectinload(Job.tags)).filter(Job.id == job_id).first()
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
        tags=[tag.name for tag in job.tags]  # Uses eager loaded tags
    )
