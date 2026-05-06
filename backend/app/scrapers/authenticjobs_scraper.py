from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
import json

class AuthenticJobsScraper(BaseScraper):
    """Scrapes jobs from Authentic Jobs API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 1) -> List[Dict]:
        jobs = []
        
        try:
            # Authentic Jobs API
            url = "https://authenticjobs.com/api/?api_method=aj.jobs.search"
            
            print(f"Fetching jobs from Authentic Jobs")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            params = {
                'keywords': search_query if search_query else 'developer',
                'perpage': 25,
                'format': 'json'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    listings = data.get('listings', {}).get('listing', [])
                    
                    if not isinstance(listings, list):
                        listings = [listings] if listings else []
                    
                    print(f"Found {len(listings)} jobs on Authentic Jobs")
                    
                    for job in listings[:25]:
                        try:
                            job_entry = {
                                'title': job.get('title', 'Unknown'),
                                'company': job.get('company', {}).get('name', 'Unknown Company'),
                                'location': job.get('company', {}).get('location', {}).get('name', 'Remote'),
                                'description': job.get('description', 'View on Authentic Jobs')[:500],
                                'url': job.get('apply_url', job.get('url', '#')),
                                'salary': None
                            }
                            jobs.append(job_entry)
                            print(f"  - {job_entry['title']} at {job_entry['company']}")
                        except Exception as e:
                            print(f"Error processing job: {e}")
                            continue
                except Exception as e:
                    print(f"Error parsing Authentic Jobs response: {e}")
            else:
                print(f"Authentic Jobs API returned status {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching from Authentic Jobs: {e}")
        
        print(f"Total jobs from Authentic Jobs: {len(jobs)}")
        return jobs
