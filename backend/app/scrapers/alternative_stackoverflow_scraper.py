from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup

class AlternativeStackOverflowScraper(BaseScraper):
    """Alternative approach: Scrape Stack Overflow Jobs HTML page"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Build URL for Stack Overflow Jobs search
            query = search_query.replace(" ", "+")
            loc = location.replace(" ", "+") if location else ""
            url = f"https://stackoverflow.com/jobs?q={query}&l={loc}&d=20&u=Km"
            
            print(f"Fetching jobs from Stack Overflow Jobs HTML page")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://stackoverflow.com/',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards with multiple selector fallbacks
            job_cards = soup.find_all('div', class_='-job')
            if not job_cards:
                job_cards = soup.find_all('div', class_='listResults')
            if not job_cards:
                job_cards = soup.find_all('div', {'data-testid': 'job-item'})
            
            print(f"Found {len(job_cards)} job cards")
            
            for card in job_cards[:20]:
                try:
                    # Try to extract job data
                    title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='s-link')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    company_elem = card.find('span', class_='fc-black-700') or card.find('span', class_='company')
                    company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
                    
                    location_elem = card.find('span', class_='fc-black-500') or card.find('span', class_='location')
                    location_text = location_elem.get_text(strip=True) if location_elem else 'Remote'
                    
                    link_elem = card.find('a', class_='s-link')
                    if link_elem:
                        href = link_elem.get('href', '')
                        if href.startswith('/'):
                            job_url = "https://stackoverflow.com" + href
                        else:
                            job_url = href
                    else:
                        job_url = '#'
                    
                    description = f"Job listing for {title} at {company} in {location_text}. Click to view full details."
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'description': description,
                        'url': job_url,
                        'salary': None
                    }
                    jobs.append(job)
                    print(f"  - {job['title']} at {job['company']}")
                    
                except Exception as e:
                    print(f"Error processing job: {e}")
                    continue
            
        except Exception as e:
            print(f"Error fetching from Stack Overflow: {e}")
        
        print(f"Total jobs from Stack Overflow: {len(jobs)}")
        return jobs
