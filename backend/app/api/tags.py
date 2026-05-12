from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job import Tag
from app.config import cache_response, IS_PRODUCTION
from pydantic import BaseModel

router = APIRouter()

class TagResponse(BaseModel):
    id: int
    name: str
    category: str

@router.get("/", response_model=List[TagResponse])
@cache_response(ttl=600)  # 10 minutes cache for tags
async def get_tags(db: Session = Depends(get_db), category: Optional[str] = None):
    # Use database directly in production cache handles caching

    # Query database
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    tags = query.all()

    result = [
        {"id": tag.id, "name": tag.name, "category": tag.category}
        for tag in tags
    ]

    # Cache removed - no longer storing results

    return [TagResponse(**tag) for tag in result]

@router.get("/categories")
async def get_tag_categories(db: Session = Depends(get_db)):
    # Cache removed - always query database

    # Query database
    categories = db.query(Tag.category).distinct().all()
    result = [cat[0] for cat in categories]

    # Cache removed - no longer storing results

    return {"categories": result}
