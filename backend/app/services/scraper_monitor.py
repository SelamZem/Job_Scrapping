from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class ScraperStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class ScraperHealth:
    name: str
    status: ScraperStatus
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    avg_jobs_per_run: float = 0.0
    history: List[Dict] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100
    
    @property
    def is_healthy(self) -> bool:
        return self.status == ScraperStatus.HEALTHY
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "success_rate": round(self.success_rate, 1),
            "avg_jobs_per_run": round(self.avg_jobs_per_run, 1),
            "is_healthy": self.is_healthy
        }

class ScraperMonitor:
    """Monitors scraper health and performance"""
    
    def __init__(self):
        self.scrapers: Dict[str, ScraperHealth] = {}
        self.max_history = 10
    
    def register_scraper(self, name: str) -> ScraperHealth:
        if name not in self.scrapers:
            self.scrapers[name] = ScraperHealth(name=name, status=ScraperStatus.UNKNOWN)
        return self.scrapers[name]
    
    def record_run(self, name: str, success: bool, jobs_found: int = 0, error_message: Optional[str] = None, duration: float = 0.0):
        scraper = self.register_scraper(name)
        now = datetime.utcnow()
        scraper.last_run = now
        scraper.total_runs += 1

        if success:
            scraper.successful_runs += 1
            scraper.last_success = now
            scraper.last_error = None
            total_jobs = scraper.avg_jobs_per_run * (scraper.total_runs - 1) + jobs_found
            scraper.avg_jobs_per_run = total_jobs / scraper.total_runs
        else:
            scraper.failed_runs += 1
            scraper.last_error = error_message

        scraper.history.append({
            "timestamp": now.isoformat(),
            "success": success,
            "jobs_found": jobs_found,
            "error": error_message,
            "duration": duration
        })
        
        if len(scraper.history) > self.max_history:
            scraper.history = scraper.history[-self.max_history:]
        
        self._update_status(scraper)
    
    def _update_status(self, scraper: ScraperHealth):
        if scraper.total_runs == 0:
            scraper.status = ScraperStatus.UNKNOWN
            return
        
        recent_runs = scraper.history[-5:] if len(scraper.history) >= 5 else scraper.history
        if not recent_runs:
            scraper.status = ScraperStatus.UNKNOWN
            return
        
        recent_successes = sum(1 for run in recent_runs if run["success"])
        recent_rate = recent_successes / len(recent_runs)
        
        if recent_rate >= 0.8:
            scraper.status = ScraperStatus.HEALTHY
        elif recent_rate >= 0.4:
            scraper.status = ScraperStatus.DEGRADED
        else:
            scraper.status = ScraperStatus.DOWN
    
    def get_health_summary(self) -> Dict:
        if not self.scrapers:
            return {"total_scrapers": 0, "healthy": 0, "degraded": 0, "down": 0, "unknown": 0, "overall_status": "unknown"}
        
        healthy = sum(1 for s in self.scrapers.values() if s.status == ScraperStatus.HEALTHY)
        degraded = sum(1 for s in self.scrapers.values() if s.status == ScraperStatus.DEGRADED)
        down = sum(1 for s in self.scrapers.values() if s.status == ScraperStatus.DOWN)
        unknown = sum(1 for s in self.scrapers.values() if s.status == ScraperStatus.UNKNOWN)
        
        total = len(self.scrapers)
        if down > total / 2:
            overall = "critical"
        elif down > 0 or degraded > total / 2:
            overall = "degraded"
        elif healthy >= total * 0.8:
            overall = "healthy"
        else:
            overall = "warning"
        
        return {
            "total_scrapers": total,
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "unknown": unknown,
            "overall_status": overall,
            "scrapers": [s.to_dict() for s in self.scrapers.values()]
        }

scraper_monitor = ScraperMonitor()
