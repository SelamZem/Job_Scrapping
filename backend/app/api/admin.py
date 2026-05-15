from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict
from datetime import datetime
import time
from app.services.scraper_monitor import scraper_monitor
from app.api.auth_new import require_admin
from app.models.user import User
from app.models.settings import SiteSetting
from app.database import SessionLocal, get_db
from app.models.job import Job
from app.services import TagService
from sqlalchemy.orm import Session

router = APIRouter(tags=["admin"])


def _do_scrape():
    """Synchronous scrape — runs in a thread via BackgroundTasks."""
    from app.scrapers import (
        RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper,
        RSSRemoteOKScraper, LandingJobsScraper, LinkedInScraper,
        GitHubJobsScraper, StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper,
    )
    scrapers = [
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
    db = SessionLocal()
    try:
        tag_service = TagService(db)
        jobs_saved = 0
        for source_name, scraper in scrapers:
            try:
                jobs_data = scraper.scrape_jobs("", "", 1) or []
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
                    jobs_saved += len(new_jobs)
                    print(f"[Manual] {source_name}: +{len(new_jobs)} new jobs")
            except Exception as e:
                print(f"[Manual] {source_name} error: {e}")
        print(f"[Manual] Done — {jobs_saved} new jobs added")
    finally:
        db.close()


@router.get("/health")
async def get_scraper_health(current_user: User = Depends(require_admin)) -> Dict:
    """Get scraper health status — admin only."""
    return scraper_monitor.get_health_summary()


@router.get("/settings")
async def get_settings(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Get all site settings — admin only."""
    settings = db.query(SiteSetting).all()
    return {s.key: s.value for s in settings}


@router.post("/settings/{key}")
async def update_setting(
    key: str,
    value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a site setting — admin only."""
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = SiteSetting(key=key, value=value)
        db.add(setting)
    db.commit()
    return {"key": key, "value": value}


@router.get("/settings/public/{key}")
async def get_public_setting(key: str, db: Session = Depends(get_db)):
    """Get a public setting — no auth required."""
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    return {"key": key, "value": setting.value if setting else None}


@router.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
):
    """Manually trigger a full scrape — admin only."""
    background_tasks.add_task(_do_scrape)
    return {"message": "Scrape started. New jobs will appear shortly."}


@router.post("/scrapers/test")
async def test_scrapers(current_user: User = Depends(require_admin)) -> Dict:
    """Test all scrapers and return results — admin only."""
    from app.scrapers import (
        RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper,
        RSSRemoteOKScraper, LandingJobsScraper, GitHubJobsScraper,
        StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper
    )
    scrapers = [
        ("Remotive",             RemotiveAPIScraper()),
        ("Arbeitnow",            ArbeitnowAPIScraper()),
        ("We Work Remotely RSS", RSSWeWorkRemotelyScraper()),
        ("RemoteOK RSS",         RSSRemoteOKScraper()),
        ("Landing.jobs",         LandingJobsScraper()),
        ("GitHub Jobs",          GitHubJobsScraper()),
        ("Stack Overflow",       StackOverflowScraper()),
        ("Authentic Jobs",       AuthenticJobsScraper()),
        ("EuroJobs",             EuroJobsScraper()),
    ]
    results = []
    for name, scraper in scrapers:
        start_time = time.time()
        try:
            jobs = scraper.scrape_jobs("software", "remote", max_pages=1)
            duration = round(time.time() - start_time, 2)
            scraper_monitor.record_run(name=name, success=len(jobs) > 0, jobs_found=len(jobs), duration=duration)
            results.append({"name": name, "status": "success" if jobs else "warning", "jobs_found": len(jobs), "duration": duration, "error": None})
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            scraper_monitor.record_run(name=name, success=False, jobs_found=0, error_message=str(e), duration=duration)
            results.append({"name": name, "status": "error", "jobs_found": 0, "duration": duration, "error": str(e)})

    return {
        "tested_at": datetime.utcnow().isoformat(),
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
    }
