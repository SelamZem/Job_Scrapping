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
from app.models.settings import SiteSetting  # ensures table is created
from app.scrapers import (
    RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper,
    RSSRemoteOKScraper, LandingJobsScraper, LinkedInScraper,
    GitHubJobsScraper, StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper,
)
from app.services import TagService
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
# Delay before first scrape so server is fully ready to serve requests
SCRAPE_STARTUP_DELAY = int(os.getenv("SCRAPE_STARTUP_DELAY", "30"))

SCRAPERS = [
    ('Remotive',             RemotiveAPIScraper()),
    ('Arbeitnow',            ArbeitnowAPIScraper()),
    ('We Work Remotely RSS', RSSWeWorkRemotelyScraper()),
    ('RemoteOK RSS',         RSSRemoteOKScraper()),
    ('Landing.jobs',         LandingJobsScraper()),
    ('LinkedIn',             LinkedInScraper()),
    ('GitHub Jobs',          GitHubJobsScraper()),
    ('Stack Overflow',       StackOverflowScraper()),
    ('Authentic Jobs',       AuthenticJobsScraper()),
    ('EuroJobs',             EuroJobsScraper()),
]


async def run_scrape(label: str = "Scheduled", delay: int = 0):
    """
    Scrape all sources in the background.
    - delay: seconds to wait before starting (lets server handle requests first)
    - max 2 scrapers run concurrently to avoid saturating the thread pool
    """
    if delay:
        await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(2)

    async def scrape_one(source_name, scraper):
        async with semaphore:
            try:
                data = await asyncio.to_thread(scraper.scrape_jobs, "", "", 1)
                return source_name, data or []
            except Exception as e:
                print(f"[{label}] {source_name} error: {e}")
                return source_name, []

    db = SessionLocal()
    try:
        print(f"[{label}] Starting scrape ({len(SCRAPERS)} sources)...")
        tag_service = TagService(db)
        jobs_saved = 0

        # Run all scrapers concurrently (max 2 at a time)
        results = await asyncio.gather(*[scrape_one(n, s) for n, s in SCRAPERS])

        for source_name, jobs_data in results:
            if not jobs_data:
                continue

            # Run DB writes in a thread — never blocks the event loop
            def save_jobs(source_name=source_name, jobs_data=jobs_data):
                new_count = 0
                new_jobs = []
                for job_data in jobs_data:
                    job_data['source'] = source_name.lower().replace(' ', '_')
                    if db.query(Job).filter(Job.url == job_data['url']).first():
                        continue
                    job = Job(**job_data)
                    db.add(job)
                    new_jobs.append(job)
                if new_jobs:
                    db.commit()
                    for job in new_jobs:
                        db.refresh(job)
                        job.tags = tag_service.extract_tags_from_job(job)
                    db.commit()
                    new_count = len(new_jobs)
                    print(f"[{label}] {source_name}: +{new_count} new jobs")
                return new_count

            jobs_saved += await asyncio.to_thread(save_jobs)
            # Yield to event loop between each source
            await asyncio.sleep(0)

        print(f"[{label}] Done — {jobs_saved} new jobs added")
    except Exception as e:
        print(f"[{label}] Scrape failed: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scraping after a delay so the server handles requests first
    asyncio.create_task(run_scrape("Startup", delay=SCRAPE_STARTUP_DELAY))

    # Recurring scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scrape,
        trigger=IntervalTrigger(hours=SCRAPE_INTERVAL_HOURS),
        kwargs={"label": "Scheduled", "delay": 0},
        id="periodic_scrape",
        replace_existing=True,
    )
    scheduler.start()
    print(f"✅ Server ready. Scrape starts in {SCRAPE_STARTUP_DELAY}s, then every {SCRAPE_INTERVAL_HOURS}h.")

    yield

    scheduler.shutdown(wait=False)
    print("🛑 Scheduler stopped.")


app = FastAPI(title="Care Jobs API", version="1.0.0", lifespan=lifespan)

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
