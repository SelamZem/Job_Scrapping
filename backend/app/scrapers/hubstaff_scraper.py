from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class HubstaffScraper(BaseScraper):
    """Scrapes jobs from Hubstaff Talent API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Hubstaff Talent API
            url = "https://talent.hubstaff.com/api/jobs"
            
            print(f"Fetching jobs from Hubstaff Talent")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            params = {
                'page': 1,
                'per_page': 50
            }
            
            if search_query:
                params['search'] = search_query
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                job_list = data
                print(f"Found {len(job_list)} jobs from Hubstaff Talent")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': job_data.get('client', {}).get('name', 'Unknown Company'),
                            'location': 'Remote',
                            'description': description,
                            'url': f"https://talent.hubstaff.com/jobs/{job_data.get('id', '')}",
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            elif isinstance(data, dict) and 'jobs' in data:
                job_list = data['jobs']
                print(f"Found {len(job_list)} jobs from Hubstaff Talent")
                
                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': job_data.get('client', {}).get('name', 'Unknown Company'),
                            'location': 'Remote',
                            'description': description,
                            'url': f"https://talent.hubstaff.com/jobs/{job_data.get('id', '')}",
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from Hubstaff Talent: {e}")
        
        print(f"Total jobs from Hubstaff Talent: {len(jobs)}")
        return jobs
