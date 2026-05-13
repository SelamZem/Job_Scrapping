import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.api import jobs, recommendations, tags, auth_new as auth, admin, health, bookmarks
from app.database import engine, Base, SessionLocal
from app.models.user import User  # ensures table is created
from app.models.job import Job
from app.scrapers import (
    RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper,
    RSSRemoteOKScraper, LandingJobsScraper, LinkedInScraper,
    GitHubJobsScraper, StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper,
)
from app.services import TagService
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

# How often to auto-scrape (hours). Override via env var SCRAPE_INTERVAL_HOURS.
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))

SCRAPERS = [
    ('Remotive',            RemotiveAPIScraper()),
    ('Arbeitnow',           ArbeitnowAPIScraper()),
    ('We Work Remotely RSS',RSSWeWorkRemotelyScraper()),
    ('RemoteOK RSS',        RSSRemoteOKScraper()),
    ('Landing.jobs',        LandingJobsScraper()),
    ('LinkedIn',            LinkedInScraper()),
    ('GitHub Jobs',         GitHubJobsScraper()),
    ('Stack Overflow',      StackOverflowScraper()),
    ('Authentic Jobs',      AuthenticJobsScraper()),
    ('EuroJobs',            EuroJobsScraper()),
]


async def run_scrape(label: str = "Scheduled"):
    """Scrape all sources and persist new jobs. Safe to call concurrently."""
    db = SessionLocal()
    try:
        job_count = db.query(Job).count()
        print(f"[{label}] DB has {job_count} jobs. Scraping all sources...")
        tag_service = TagService(db)
        jobs_saved = 0

        for source_name, scraper in SCRAPERS:
            try:
                jobs_data = await asyncio.to_thread(scraper.scrape_jobs, "", "", 1)
                if not jobs_data:
                    continue
                for job_data in jobs_data:
                    job_data['source'] = source_name.lower().replace(' ', '_')
                    if db.query(Job).filter(Job.url == job_data['url']).first():
                        continue
                    job = Job(**job_data)
                    db.add(job)
                    db.commit()
                    db.refresh(job)
                    job.tags = tag_service.extract_tags_from_job(job)
                    db.commit()
                    jobs_saved += 1
                print(f"[{label}] {source_name}: saved {len(jobs_data)} jobs")
            except Exception as e:
                print(f"[{label}] {source_name} error: {e}")
                continue

        print(f"[{label}] Done — {jobs_saved} new jobs added")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Run initial scrape in background (non-blocking)
    asyncio.create_task(run_scrape("Startup"))

    # 2. Start the recurring scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scrape,
        trigger=IntervalTrigger(hours=SCRAPE_INTERVAL_HOURS),
        kwargs={"label": "Scheduled"},
        id="periodic_scrape",
        replace_existing=True,
    )
    scheduler.start()
    print(f"✅ Server ready. Scraping every {SCRAPE_INTERVAL_HOURS}h.")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    print("🛑 Scheduler stopped.")


app = FastAPI(title="Care Jobs API", version="1.0.0", lifespan=lifespan)

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]
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

app.include_router(jobs.router,            prefix="/api/jobs",            tags=["jobs"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(tags.router,            prefix="/api/tags",            tags=["tags"])
app.include_router(auth.router,            prefix="/api/auth",            tags=["auth"])
app.include_router(admin.router,           prefix="/api/admin",           tags=["admin"])
app.include_router(health.router,          prefix="/health",              tags=["health"])
app.include_router(bookmarks.router,       prefix="/api/bookmarks",       tags=["bookmarks"])


@app.get("/")
async def root():
    return {"message": "Care Jobs API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
