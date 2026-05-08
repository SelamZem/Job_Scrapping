from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from datetime import datetime
import time
from app.services.scraper_monitor import scraper_monitor
from app.api.auth_new import require_admin
from app.models.user import User

router = APIRouter(tags=["admin"])

@router.get("/health")
async def get_scraper_health(current_user: User = Depends(require_admin)) -> Dict:
    """Get scraper health status - admin endpoint"""
    return scraper_monitor.get_health_summary()

@router.post("/scrapers/test")
async def test_scrapers(current_user: User = Depends(require_admin)) -> Dict:
    """Test all scrapers and return results"""
    from app.scrapers import (
        RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper,
        RSSRemoteOKScraper, LandingJobsScraper, GitHubJobsScraper,
        StackOverflowScraper, AuthenticJobsScraper, EuroJobsScraper
    )

    scrapers = [
        ("Remotive", RemotiveAPIScraper()),
        ("Arbeitnow", ArbeitnowAPIScraper()),
        ("We Work Remotely RSS", RSSWeWorkRemotelyScraper()),
        ("RemoteOK RSS", RSSRemoteOKScraper()),
        ("Landing.jobs", LandingJobsScraper()),
        ("GitHub Jobs", GitHubJobsScraper()),
        ("Stack Overflow", StackOverflowScraper()),
        ("Authentic Jobs", AuthenticJobsScraper()),
        ("EuroJobs", EuroJobsScraper())
    ]
    
    results = []
    for name, scraper in scrapers:
        start_time = time.time()
        try:
            jobs = scraper.scrape_jobs("software", "remote", max_pages=1)
            end_time = time.time()
            duration = end_time - start_time

            # Record in monitor
            scraper_monitor.record_run(
                name=name,
                success=len(jobs) > 0,
                jobs_found=len(jobs),
                duration=round(duration, 2)
            )

            results.append({
                "name": name,
                "status": "success" if jobs else "warning",
                "jobs_found": len(jobs),
                "duration": round(duration, 2),
                "error": None
            })
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            # Record failure in monitor
            scraper_monitor.record_run(
                name=name,
                success=False,
                jobs_found=0,
                error_message=str(e),
                duration=round(duration, 2)
            )
            
            results.append({
                "name": name,
                "status": "error",
                "jobs_found": 0,
                "duration": round(duration, 2),
                "error": str(e)
            })
    
    return {
        "tested_at": datetime.utcnow().isoformat(),
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error")
    }
