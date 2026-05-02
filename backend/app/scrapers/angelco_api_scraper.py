from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class AngelCoAPIScraper(BaseScraper):
    """Scrapes jobs from AngelList (Wellfound) API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # AngelList/Wellfound API endpoint
            url = "https://www.angel.co/job_listings.json"
            
            print(f"Fetching jobs from AngelList/Wellfound API")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Origin': 'https://www.angel.co',
                'Referer': 'https://www.angel.co/'
            }
            
            params = {}
            if search_query:
                params['query'] = search_query
            if location:
                params['location'] = location
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data and 'jobs' in data:
                job_list = data['jobs']
                print(f"Found {len(job_list)} jobs from AngelList API")
                
                for job_data in job_list[:50]:
                    try:
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': job_data.get('startup', {}).get('name', 'Unknown Company'),
                            'location': job_data.get('location', 'Remote') or 'Remote',
                            'description': job_data.get('description', 'No description available')[:500] + '...' if len(job_data.get('description', '')) > 500 else job_data.get('description', 'No description available'),
                            'url': f"https://www.angel.co/company/{job_data.get('startup', {}).get('slug', '')}/jobs/{job_data.get('id', '')}",
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from AngelList API: {e}")
        
        print(f"Total jobs from AngelList API: {len(jobs)}")
        return jobs
