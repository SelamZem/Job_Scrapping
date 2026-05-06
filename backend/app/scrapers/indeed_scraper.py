from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup

class IndeedScraper(BaseScraper):
    """Scrapes jobs from Indeed RSS feed"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Indeed RSS feed for remote jobs
            url = "https://www.indeed.com/rss"
            
            print(f"Fetching jobs from Indeed")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'q': search_query if search_query else 'software engineer',
                'l': location if location else 'Remote',
                'jt': 'remote'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            import feedparser
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                print(f"Found {len(feed.entries)} jobs from Indeed")
                
                for entry in feed.entries[:25]:
                    try:
                        title = entry.get('title', 'Unknown')
                        
                        # Parse title: usually "Job Title - Company - Location"
                        company = 'Unknown Company'
                        position = title
                        job_location = 'Remote'
                        
                        if ' - ' in title:
                            parts = title.split(' - ')
                            if len(parts) >= 2:
                                position = parts[0].strip()
                                company = parts[1].strip()
                            if len(parts) >= 3:
                                job_location = parts[2].strip()
                        
                        summary = entry.get('summary', 'No description available')
                        summary = self.strip_html(summary)
                        if len(summary) > 500:
                            summary = summary[:500] + '...'
                        
                        job = {
                            'title': position,
                            'company': company,
                            'location': job_location,
                            'description': summary,
                            'url': entry.get('link', '#'),
                            'salary': None
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from Indeed: {e}")
        
        print(f"Total jobs from Indeed: {len(jobs)}")
        return jobs
