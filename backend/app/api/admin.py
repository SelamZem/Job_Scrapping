from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict
from datetime import datetime
import asyncio
import time
from app.services.scraper_monitor import scraper_monitor
from app.api.auth_new import require_admin
from app.models.user import User

router = APIRouter(tags=["admin"])


@router.get("/health")
async def get_scraper_health(current_user: User = Depends(require_admin)) -> Dict:
    """Get scraper health status — admin only."""
    return scraper_monitor.get_health_summary()


@router.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """Manually trigger a full scrape — admin only. Runs in background."""
    from app.main import run_scrape

    async def _run():
        await run_scrape("Manual")

    background_tasks.add_task(asyncio.ensure_future, _run())
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
