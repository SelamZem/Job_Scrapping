from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class GitHubJobsScraper(BaseScraper):
    """Scrapes jobs from GitHub Jobs API via third-party aggregator"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Using a third-party GitHub Jobs API (since official was deprecated)
            url = "https://jobs.github.com/positions.json"
            
            print(f"Fetching jobs from GitHub Jobs API")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            params = {}
            if search_query:
                params['description'] = search_query
            if location:
                params['location'] = location
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            job_list = response.json()
            
            if job_list:
                print(f"Found {len(job_list)} jobs from GitHub Jobs API")
                
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
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from GitHub Jobs API: {e}")
        
        print(f"Total jobs from GitHub Jobs API: {len(jobs)}")
        return jobs
