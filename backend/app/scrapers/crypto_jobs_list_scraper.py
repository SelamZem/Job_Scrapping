from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class CryptoJobsListScraper(BaseScraper):
    """Scrapes jobs from CryptoJobsList API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # CryptoJobsList API
            url = "https://crypto.jobs/api/jobs"
            
            print(f"Fetching jobs from CryptoJobsList API for: {search_query}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {}
            if search_query:
                params['query'] = search_query
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                job_list = data
                print(f"Found {len(job_list)} jobs from CryptoJobsList API")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': job_data.get('company', 'Unknown Company'),
                            'location': job_data.get('location', 'Remote') or 'Remote',
                            'description': description,
                            'url': job_data.get('url', '#'),
                            'salary': job_data.get('salary', None)
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from CryptoJobsList API: {e}")
        
        print(f"Total jobs from CryptoJobsList API: {len(jobs)}")
        return jobs
