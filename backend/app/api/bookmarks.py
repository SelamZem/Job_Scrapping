from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.api.auth_new import get_current_user

router = APIRouter()


@router.get("/", response_model=List[int])
async def get_bookmarks(current_user: User = Depends(get_current_user)):
    """Return the list of saved job IDs for the current user."""
    return current_user.get_saved_jobs()


@router.post("/{job_id}", status_code=status.HTTP_200_OK)
async def add_bookmark(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a job to the current user's saved jobs."""
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    saved = current_user.get_saved_jobs()
    if job_id not in saved:
        saved.append(job_id)
        current_user.set_saved_jobs(saved)
        db.commit()

    return {"saved_jobs": saved}


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
async def remove_bookmark(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a job from the current user's saved jobs."""
    saved = current_user.get_saved_jobs()
    if job_id in saved:
        saved.remove(job_id)
        current_user.set_saved_jobs(saved)
        db.commit()

    return {"saved_jobs": saved}
