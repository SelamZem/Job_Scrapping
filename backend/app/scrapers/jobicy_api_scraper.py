from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class JobicyAPIScraper(BaseScraper):
    """Scrapes jobs from Jobicy API (free, no auth required)"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Jobicy API endpoint - free, no auth
            url = "https://jobicy.com/api/v2/remote-jobs"
            
            print(f"Fetching jobs from Jobicy API for: {search_query}")
            
            params = {}
            if search_query:
                params['tag'] = search_query.lower()
            if location:
                params['geo'] = location
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'jobs' in data:
                job_list = data['jobs']
                print(f"Found {len(job_list)} jobs from Jobicy API")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('jobDescription', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('jobTitle', 'Unknown'),
                            'company': job_data.get('companyName', 'Unknown Company'),
                            'location': job_data.get('jobGeo', 'Remote') or 'Remote',
                            'description': description,
                            'url': job_data.get('url', '#'),
                            'salary': job_data.get('annualSalary', None) or job_data.get('jobSalary', None)
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from Jobicy API: {e}")
        
        print(f"Total jobs from Jobicy API: {len(jobs)}")
        return jobs
