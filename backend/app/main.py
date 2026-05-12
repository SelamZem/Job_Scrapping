from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import jobs, recommendations, tags, auth_new as auth, admin, health
from app.database import engine, Base, SessionLocal
from app.models.user import User  # Import User model to create table
from app.models.job import Job
from app.scrapers import RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper, RSSRemoteOKScraper, LandingJobsScraper, LinkedInScraper, GitHubJobsScraper, StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper
from app.services import TagService
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-scrape jobs from all sources
    db = SessionLocal()
    try:
        job_count = db.query(Job).count()
        print(f"Database has {job_count} jobs. Scraping for more jobs...")

        api_scrapers = [
            ('Remotive', RemotiveAPIScraper()),
            ('Arbeitnow', ArbeitnowAPIScraper()),
            ('We Work Remotely RSS', RSSWeWorkRemotelyScraper()),
            ('RemoteOK RSS', RSSRemoteOKScraper()),
            ('Landing.jobs', LandingJobsScraper()),
            ('LinkedIn', LinkedInScraper()),
            ('GitHub Jobs', GitHubJobsScraper()),
            ('Stack Overflow', StackOverflowScraper()),
            ('Authentic Jobs', AuthenticJobsScraper()),
            ('EuroJobs', EuroJobsScraper())
        ]
        tag_service = TagService(db)
        jobs_saved = 0

        for source_name, scraper in api_scrapers:
            try:
                # Scrape without filtering to get all available jobs
                jobs_data = scraper.scrape_jobs("", "", max_pages=1)
                if jobs_data:
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
                        jobs_saved += 1
                    print(f"Saved {len(jobs_data)} jobs from {source_name}")
            except Exception as e:
                print(f"Error with {source_name} scraper: {e}")
                continue

        print(f"Auto-scraped {jobs_saved} new jobs from real APIs on startup")
    finally:
        db.close()
    yield
    # Shutdown
    pass

app = FastAPI(title="Care Jobs API", version="1.0.0", lifespan=lifespan)

import os

# CORS origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

# Add production frontend URL if available
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {"message": "Care Jobs API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
