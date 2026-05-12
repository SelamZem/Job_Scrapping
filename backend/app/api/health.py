"""
Health check endpoint for Render monitoring
"""
from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine
from app.config import IS_PRODUCTION
import time
import psutil
import os

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint for Render"""
    start_time = time.time()
    
    # Check database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Check response time
    response_time = (time.time() - start_time) * 1000
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": time.time(),
        "environment": "production" if IS_PRODUCTION else "development",
        "checks": {
            "database": db_status,
            "response_time_ms": round(response_time, 2),
            "cpu_usage_percent": round(cpu_percent, 2),
            "memory_usage_percent": round(memory_percent, 2),
        },
        "version": "1.0.0"
    }
    
    # Return appropriate status code
    status_code = 200 if db_status == "healthy" else 503
    
    return health_data
