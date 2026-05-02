from typing import List, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_job_recommendations(self, user_profile: Dict, jobs: List[Dict], limit: int = 5) -> List[Dict]:
        """Get AI-powered job recommendations based on user profile"""
        if not os.getenv("OPENAI_API_KEY"):
            return self._get_fallback_recommendations(jobs, limit)
        
        try:
            job_summaries = "\n".join([
                f"- {job['title']} at {job['company']} (Tags: {', '.join(job.get('tags', []))})"
                for job in jobs[:20]
            ])
            
            prompt = f"""
            User Profile:
            - Skills: {', '.join(user_profile.get('skills', []))}
            - Preferred Roles: {', '.join(user_profile.get('roles', []))}
            - Preferred Locations: {', '.join(user_profile.get('locations', []))}
            
            Available Jobs:
            {job_summaries}
            
            Recommend the top {limit} jobs that best match this user's profile.
            Return only the job titles and companies, one per line.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a job recommendation assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            recommendations = response.choices[0].message.content.strip().split('\n')
            return self._match_recommendations_to_jobs(recommendations, jobs)
            
        except Exception as e:
            print(f"AI service error: {e}")
            return self._get_fallback_recommendations(jobs, limit)
    
    def _match_recommendations_to_jobs(self, recommendations: List[str], jobs: List[Dict]) -> List[Dict]:
        """Match AI recommendations to actual job objects"""
        matched = []
        for rec in recommendations:
            for job in jobs:
                if job['title'] in rec and job['company'] in rec:
                    matched.append(job)
                    break
        return matched[:5]
    
    def _get_fallback_recommendations(self, jobs: List[Dict], limit: int) -> List[Dict]:
        """Fallback recommendations when AI is unavailable"""
        return jobs[:limit]
    
    def get_career_advice(self, job_title: str) -> str:
        """Get AI-powered career advice for a specific job role"""
        if not os.getenv("OPENAI_API_KEY"):
            return "AI service unavailable. Please configure OPENAI_API_KEY."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a career advisor."},
                    {"role": "user", "content": f"Provide brief career advice for someone pursuing a {job_title} role."}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating advice: {e}"
