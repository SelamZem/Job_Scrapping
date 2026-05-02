from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class AuthenticJobsScraper(BaseScraper):
    """Scrapes jobs from AuthenticJobs API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # AuthenticJobs API endpoint
            url = "https://authenticjobs.com/api/jobs.json"
            
            print(f"Fetching jobs from AuthenticJobs API for: {search_query}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {}
            if search_query:
                params['search'] = search_query
            if location:
                params['location'] = location
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'listings' in data and 'listing' in data['listings']:
                job_list = data['listings']['listing']
                if not isinstance(job_list, list):
                    job_list = [job_list]
                print(f"Found {len(job_list)} jobs from AuthenticJobs API")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        company_name = 'Unknown Company'
                        if 'company' in job_data and job_data['company']:
                            company_name = job_data['company'].get('name', 'Unknown Company')
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': company_name,
                            'location': 'Remote',
                            'description': description,
                            'url': job_data.get('url', '#'),
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from AuthenticJobs API: {e}")
        
        print(f"Total jobs from AuthenticJobs API: {len(jobs)}")
        return jobs
