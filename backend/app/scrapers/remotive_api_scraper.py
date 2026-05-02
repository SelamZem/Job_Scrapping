from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class RemotiveAPIScraper(BaseScraper):
    """Scrapes jobs from Remotive API (free, no auth required)"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Remotive API endpoint
            url = "https://remotive.com/api/remote-jobs"
            
            # Add search query as category filter
            params = {}
            if search_query:
                params['search'] = search_query.lower()
            
            print(f"Fetching jobs from Remotive API for: {search_query}")
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'jobs' in data:
                job_list = data['jobs']
                print(f"Found {len(job_list)} jobs from Remotive API")
                
                for job_data in job_list:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': job_data.get('company_name', 'Unknown Company'),
                            'location': job_data.get('candidate_required_location', 'Remote') or 'Remote',
                            'description': description,
                            'url': job_data.get('url', '#'),
                            'salary': self._extract_salary(job_data)
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from Remotive API: {e}")
        
        print(f"Total jobs from Remotive API: {len(jobs)}")
        return jobs
    
    def _extract_salary(self, job_data: Dict) -> str:
        """Try to extract salary information"""
        # Remotive doesn't always have salary, check description
        description = job_data.get('description', '').lower()
        salary_keywords = ['salary', '$', 'per year', 'per hour', 'k-', 'annual']
        
        if any(keyword in description for keyword in salary_keywords):
            return "See job description for salary"
        
        return None
