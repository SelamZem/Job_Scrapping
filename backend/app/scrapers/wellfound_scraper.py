from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class WellfoundScraper(BaseScraper):
    """Scrapes jobs from Wellfound (formerly AngelList) API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Wellfound API endpoint
            url = "https://api.wellfound.com/v1/jobs"
            
            print(f"Fetching jobs from Wellfound")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            params = {
                'remote': 'true',
                'page': 1
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                job_list = data
                print(f"Found {len(job_list)} jobs from Wellfound")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': job_data.get('company', {}).get('name', 'Unknown Company'),
                            'location': job_data.get('location', 'Remote') or 'Remote',
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
            print(f"Error fetching from Wellfound: {e}")
        
        print(f"Total jobs from Wellfound: {len(jobs)}")
        return jobs
