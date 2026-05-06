from typing import List, Dict
from app.scrapers.base import BaseScraper
import feedparser
import requests

class WorkingNomadsScraper(BaseScraper):
    """Scrapes jobs from Working Nomads RSS feed"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Working Nomads RSS feed
            url = "https://www.workingnomads.com/jobs/rss.xml"
            
            print(f"Fetching jobs from Working Nomads RSS")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                print(f"Found {len(feed.entries)} jobs in Working Nomads RSS")
                
                search_lower = search_query.lower() if search_query else ""
                
                for entry in feed.entries[:50]:
                    try:
                        title = entry.get('title', 'Unknown')
                        
                        # Filter by search query
                        if search_lower and search_lower not in title.lower():
                            continue
                        
                        # Parse title: usually "Job Title at Company"
                        company = 'Unknown Company'
                        position = title
                        
                        if ' at ' in title:
                            parts = title.split(' at ')
                            position = parts[0].strip()
                            company = parts[1].strip()
                        elif ' @ ' in title:
                            parts = title.split(' @ ')
                            position = parts[0].strip()
                            company = parts[1].strip()
                        
                        description = entry.get('summary', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        job = {
                            'title': position,
                            'company': company,
                            'location': 'Remote',
                            'description': description,
                            'url': entry.get('link', '#'),
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from Working Nomads: {e}")
        
        print(f"Total jobs from Working Nomads: {len(jobs)}")
        return jobs
