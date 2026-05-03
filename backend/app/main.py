from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import jobs, recommendations, tags, auth_new as auth
from app.database import engine, Base
from app.models.user import User  # Import User model to create table

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Care Jobs API", version="1.0.0")

import os

# CORS origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

# Add production frontend URL if available
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Care Jobs API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
