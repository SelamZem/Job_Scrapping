from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, desc, or_
from typing import Dict, List
from app.database import get_db
from app.models.job import Job, Tag
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
    max_jobs_to_analyze: int = 100  # Limit jobs for performance

@router.post("/")
async def get_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    # Build query with eager loading to avoid N+1 problem
    query = db.query(Job).options(selectinload(Job.tags))

    # Filter by user skills if provided (database-level filtering for performance)
    if request.user_profile.skills:
        skill_filters = [
            Job.title.ilike(f"%{skill}%") |
            Job.description.ilike(f"%{skill}%")
            for skill in request.user_profile.skills
        ]
        if skill_filters:
            query = query.filter(or_(*skill_filters))

    # Filter by user locations if provided
    if request.user_profile.locations:
        location_filters = [
            Job.location.ilike(f"%{location}%")
            for location in request.user_profile.locations
        ]
        if location_filters:
            query = query.filter(or_(*location_filters))

    # Order by most recent and limit to avoid loading all jobs
    jobs = query.order_by(
        desc(func.coalesce(Job.posted_date, Job.scraped_date))
    ).limit(request.max_jobs_to_analyze).all()

    if not jobs:
        # Fallback: get recent jobs if no matches
        jobs = db.query(Job).options(selectinload(Job.tags)).order_by(
            desc(func.coalesce(Job.posted_date, Job.scraped_date))
        ).limit(request.max_jobs_to_analyze).all()

    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs available")

    ai_service = AIService()
    user_profile_dict = request.user_profile.dict()

    jobs_data = [
        {
            'title': job.title,
            'company': job.company,
            'url': job.url,
            'tags': [tag.name for tag in job.tags]  # Uses eager loaded tags
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
