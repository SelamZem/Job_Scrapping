from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job import Tag
from pydantic import BaseModel

router = APIRouter()

class TagResponse(BaseModel):
    id: int
    name: str
    category: str

@router.get("/", response_model=List[TagResponse])
async def get_tags(db: Session = Depends(get_db), category: Optional[str] = None):
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    tags = query.all()
    
    return [
        TagResponse(id=tag.id, name=tag.name, category=tag.category)
        for tag in tags
    ]

@router.get("/categories")
async def get_tag_categories(db: Session = Depends(get_db)):
    categories = db.query(Tag.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}
