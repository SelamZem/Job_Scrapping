from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class FindWorkAPIScraper(BaseScraper):
    """Scrapes jobs from FindWork API (free tier available)"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # FindWork API endpoint - public endpoint without auth for demo
            url = "https://findwork.dev/api/jobs/"
            
            print(f"Fetching jobs from FindWork API for: {search_query}")
            
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
            
            if 'results' in data:
                job_list = data['results']
                print(f"Found {len(job_list)} jobs from FindWork API")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('role', 'Unknown'),
                            'company': job_data.get('company_name', 'Unknown Company'),
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
            print(f"Error fetching from FindWork API: {e}")
        
        print(f"Total jobs from FindWork API: {len(jobs)}")
        return jobs
