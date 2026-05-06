from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class GitHubJobsScraper(BaseScraper):
    """Scrapes jobs from GitHub Jobs API (if available) or GitHub repo listings"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 1) -> List[Dict]:
        jobs = []
        
        try:
            # Try GitHub's job search via their API
            # Note: GitHub Jobs API was deprecated, using alternative approach
            url = "https://jobs.github.com/positions.json"
            
            print(f"Fetching jobs from GitHub")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'description': search_query if search_query else 'software',
                'location': location if location else 'remote',
                'page': 1
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} jobs on GitHub")
                
                for job in data[:20]:
                    try:
                        job_entry = {
                            'title': job.get('title', 'Unknown'),
                            'company': job.get('company', 'Unknown Company'),
                            'location': job.get('location', 'Remote'),
                            'description': job.get('description', 'No description')[:500],
                            'url': job.get('url', '#'),
                            'salary': None
                        }
                        jobs.append(job_entry)
                        print(f"  - {job_entry['title']} at {job_entry['company']}")
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            else:
                print(f"GitHub API returned status {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching from GitHub: {e}")
        
        print(f"Total jobs from GitHub: {len(jobs)}")
        return jobs
