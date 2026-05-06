from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup

class StackOverflowScraper(BaseScraper):
    """Scrapes jobs from Stack Overflow Jobs RSS feed"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 1) -> List[Dict]:
        jobs = []
        
        try:
            # Stack Overflow Jobs RSS feed
            url = "https://stackoverflow.com/jobs/feed"
            
            print(f"Fetching jobs from Stack Overflow")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse RSS XML
            from xml.etree import ElementTree as ET
            
            root = ET.fromstring(response.content)
            
            # RSS 2.0 format
            channel = root.find('channel')
            if channel is None:
                print("No channel found in Stack Overflow RSS")
                return jobs
            
            items = channel.findall('item')
            print(f"Found {len(items)} job entries on Stack Overflow")
            
            for item in items[:25]:
                try:
                    title = item.find('title')
                    title_text = title.text if title is not None else 'Unknown'
                    
                    link = item.find('link')
                    job_url = link.text if link is not None else '#'
                    
                    description = item.find('description')
                    desc_text = description.text if description is not None else 'View on Stack Overflow'
                    
                    # Clean description
                    if desc_text and len(desc_text) > 500:
                        desc_text = desc_text[:500] + '...'
                    
                    # Try to extract company from title (usually "Title at Company")
                    company = 'Unknown Company'
                    if ' at ' in title_text:
                        parts = title_text.split(' at ')
                        title_text = parts[0]
                        company = parts[1]
                    
                    job = {
                        'title': title_text,
                        'company': company,
                        'location': 'Remote',
                        'description': desc_text,
                        'url': job_url,
                        'salary': None
                    }
                    jobs.append(job)
                    print(f"  - {job['title']} at {job['company']}")
                    
                except Exception as e:
                    print(f"Error processing job entry: {e}")
                    continue
            
        except Exception as e:
            print(f"Error fetching from Stack Overflow: {e}")
        
        print(f"Total jobs from Stack Overflow: {len(jobs)}")
        return jobs
