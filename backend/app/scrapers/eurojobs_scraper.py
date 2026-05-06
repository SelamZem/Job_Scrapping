from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup

class EuroJobsScraper(BaseScraper):
    """Scrapes remote jobs from EuroJobs"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 1) -> List[Dict]:
        jobs = []
        
        try:
            # EuroJobs has an RSS feed
            url = "https://eurojobs.com/feed/"
            
            print(f"Fetching jobs from EuroJobs")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            from xml.etree import ElementTree as ET
            
            root = ET.fromstring(response.content)
            channel = root.find('channel')
            
            if channel is None:
                print("No channel found in EuroJobs RSS")
                return jobs
            
            items = channel.findall('item')
            print(f"Found {len(items)} job entries on EuroJobs")
            
            for item in items[:20]:
                try:
                    title = item.find('title')
                    title_text = title.text if title is not None else 'Unknown'
                    
                    link = item.find('link')
                    job_url = link.text if link is not None else '#'
                    
                    description = item.find('description')
                    desc_text = description.text if description is not None else 'View on EuroJobs'
                    
                    # Try to extract company and location
                    company = 'Unknown Company'
                    location = 'Europe'
                    
                    job = {
                        'title': title_text,
                        'company': company,
                        'location': location,
                        'description': desc_text[:500] if desc_text else 'View on EuroJobs',
                        'url': job_url,
                        'salary': None
                    }
                    jobs.append(job)
                    print(f"  - {job['title']}")
                    
                except Exception as e:
                    print(f"Error processing job entry: {e}")
                    continue
            
        except Exception as e:
            print(f"Error fetching from EuroJobs: {e}")
        
        print(f"Total jobs from EuroJobs: {len(jobs)}")
        return jobs
