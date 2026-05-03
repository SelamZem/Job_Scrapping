from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.models.job import Job
from app.services import AIService
from pydantic import BaseModel

router = APIRouter()

class UserProfile(BaseModel):
    skills: List[str]
    roles: List[str]
    locations: List[str]

class RecommendationRequest(BaseModel):
    user_profile: UserProfile
    limit: int = 5

@router.post("/")
async def get_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs available")
    
    ai_service = AIService()
    user_profile_dict = request.user_profile.dict()
    
    jobs_data = [
        {
            'title': job.title,
            'company': job.company,
            'url': job.url,
            'tags': [tag.name for tag in job.tags]
        }
        for job in jobs
    ]
    
    recommendations = ai_service.get_job_recommendations(user_profile_dict, jobs_data, request.limit)
    
    return {"recommendations": recommendations}

@router.get("/advice/{job_title}")
async def get_career_advice(job_title: str):
    ai_service = AIService()
    advice = ai_service.get_career_advice(job_title)
    return {"advice": advice}
