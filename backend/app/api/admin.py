from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from datetime import datetime
import time
from app.services.scraper_monitor import scraper_monitor
from app.api.auth_new import get_password_hash
from app.models.user import User
from app.database import SessionLocal

router = APIRouter(tags=["admin"])

def require_admin():
    """Lazy import to avoid circular dependency"""
    from app.api.auth_new import require_admin as _require_admin
    return _require_admin

@router.post("/setup-admin")
async def setup_admin():
    """Create default admin user - call once then remove this endpoint"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            return {"message": "Admin already exists", "username": admin.username}

        admin_user = User(
            username="admin",
            email="admin@carejobs.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()

        return {
            "message": "Admin created! Login with: admin / admin123",
            "username": "admin",
            "password": "admin123"
        }
    finally:
        db.close()

@router.get("/health")
async def get_scraper_health(current_user = Depends(require_admin())) -> Dict:
    """Get scraper health status - admin endpoint"""
    return scraper_monitor.get_health_summary()

@router.post("/scrapers/test")
async def test_scrapers(current_user = Depends(require_admin())) -> Dict:
    """Test all scrapers and return results"""
    from app.scrapers import (
        RemotiveAPIScraper, ArbeitnowAPIScraper, RSSWeWorkRemotelyScraper,
        RSSRemoteOKScraper, LandingJobsScraper, EuroJobsScraper
    )
    
    scrapers = [
        ("Remotive", RemotiveAPIScraper()),
        ("Arbeitnow", ArbeitnowAPIScraper()),
        ("We Work Remotely", RSSWeWorkRemotelyScraper()),
        ("RemoteOK", RSSRemoteOKScraper()),
        ("Landing.jobs", LandingJobsScraper()),
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
