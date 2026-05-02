from typing import List
from app.models.job import Job, Tag
from sqlalchemy.orm import Session

class TagService:
    def __init__(self, db: Session):
        self.db = db
    
    def extract_tags_from_job(self, job: Job) -> List[Tag]:
        """Extract tags from job title and description"""
        tags = []
        text = f"{job.title} {job.description}".lower()
        
        # Common tech skills
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'sql', 'mongodb', 'typescript', 'go', 'rust', 'swift',
            'machine learning', 'ai', 'data science', 'devops', 'cloud', 'linux',
            'git', 'agile', 'scrum', 'api', 'rest', 'graphql', 'microservices'
        ]
        
        # Common job roles
        job_roles = [
            'developer', 'engineer', 'manager', 'analyst', 'designer', 'architect',
            'consultant', 'specialist', 'director', 'lead', 'senior', 'junior'
        ]
        
        # Common industries
        industries = [
            'fintech', 'healthcare', 'ecommerce', 'saas', 'education', 'gaming',
            'finance', 'banking', 'insurance', 'retail', 'manufacturing'
        ]
        
        for skill in tech_skills:
            if skill in text:
                tag = self._get_or_create_tag(skill, 'skill')
                tags.append(tag)
        
        for role in job_roles:
            if role in text:
                tag = self._get_or_create_tag(role, 'role')
                tags.append(tag)
        
        for industry in industries:
            if industry in text:
                tag = self._get_or_create_tag(industry, 'industry')
                tags.append(tag)
        
        return tags
    
    def _get_or_create_tag(self, name: str, category: str) -> Tag:
        tag = self.db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name, category=category)
            self.db.add(tag)
            self.db.commit()
            self.db.refresh(tag)
        return tag
    
    def get_all_tags(self) -> List[Tag]:
        return self.db.query(Tag).all()
    
    def get_tags_by_category(self, category: str) -> List[Tag]:
        return self.db.query(Tag).filter(Tag.category == category).all()
