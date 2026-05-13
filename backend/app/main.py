import os
import asyncio
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


async def background_scrape():
    """Run startup scraping in the background so the server starts instantly."""
    # Small delay to let the server fully start first
    await asyncio.sleep(5)

    db = SessionLocal()
    try:
        job_count = db.query(Job).count()
        print(f"[Background] Database has {job_count} jobs. Starting background scrape...")

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
            ('EuroJobs', EuroJobsScraper()),
        ]
        tag_service = TagService(db)
        jobs_saved = 0

        for source_name, scraper in api_scrapers:
            try:
                # Run blocking scraper in a thread so we don't block the event loop
                jobs_data = await asyncio.to_thread(
                    scraper.scrape_jobs, "", "", 1
                )
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
                    print(f"[Background] Saved {len(jobs_data)} jobs from {source_name}")
            except Exception as e:
                print(f"[Background] Error with {source_name} scraper: {e}")
                continue

        print(f"[Background] Scrape complete — {jobs_saved} new jobs added")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Server starts immediately, scraping happens in the background
    asyncio.create_task(background_scrape())
    print("✅ Server ready. Background scrape started.")
    yield
    # Shutdown — nothing to clean up


app = FastAPI(title="Care Jobs API", version="1.0.0", lifespan=lifespan)

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
async def health_check():
    return {"status": "healthy"}
