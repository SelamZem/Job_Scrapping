from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class ArbeitnowAPIScraper(BaseScraper):
    """Scrapes jobs from Arbeitnow API (free, no auth required)"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Arbeitnow API endpoint
            url = "https://www.arbeitnow.com/api/job-board-api"
            
            print(f"Fetching jobs from Arbeitnow API for: {search_query}")
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                job_list = data['data']
                print(f"Found {len(job_list)} jobs from Arbeitnow API")
                
                # Filter by search query if provided
                if search_query:
                    search_lower = search_query.lower()
                    job_list = [j for j in job_list if search_lower in j.get('title', '').lower() or search_lower in j.get('description', '').lower()]
                
                for job_data in job_list[:50]:  # Limit to 50 jobs
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': job_data.get('title', 'Unknown'),
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
            print(f"Error fetching from Arbeitnow API: {e}")
        
        print(f"Total jobs from Arbeitnow API: {len(jobs)}")
        return jobs
