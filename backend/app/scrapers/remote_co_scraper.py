from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup

class RemoteCoScraper(BaseScraper):
    """Scrapes jobs from Remote.co"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Remote.co job listings page
            url = "https://remote.co/remote-jobs/"
            
            print(f"Fetching jobs from Remote.co")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings
            job_cards = soup.find_all('div', class_='job-card') or soup.find_all('div', class_='job-listing')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('article', class_='job') or soup.find_all('div', class_='job')
            
            print(f"Found {len(job_cards)} job cards on Remote.co")
            
            for card in job_cards[:50]:
                try:
                    # Extract job details
                    title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='job-title')
                    title = title_elem.get_text(strip=True) if title_elem else 'Unknown'
                    
                    company_elem = card.find('span', class_='company') or card.find('div', class_='company')
                    company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
                    
                    link_elem = card.find('a', href=True)
                    job_url = link_elem['href'] if link_elem else '#'
                    if job_url.startswith('/'):
                        job_url = f"https://remote.co{job_url}"
                    
                    description_elem = card.find('div', class_='description') or card.find('p')
                    description = description_elem.get_text(strip=True) if description_elem else 'No description'
                    if len(description) > 500:
                        description = description[:500] + '...'
                    
                    location_elem = card.find('span', class_='location') or card.find('div', class_='location')
                    job_location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'description': description,
                        'url': job_url,
                        'salary': None
                    }
                    jobs.append(job)
                    print(f"  - {job['title']} at {job['company']}")
                    
                except Exception as e:
                    print(f"Error processing job card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error fetching from Remote.co: {e}")
        
        print(f"Total jobs from Remote.co: {len(jobs)}")
        return jobs
