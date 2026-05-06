from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class LinkedInScraper(BaseScraper):
    """Scrapes jobs from LinkedIn public job search"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # LinkedIn jobs API (public endpoint)
            url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            print(f"Fetching jobs from LinkedIn")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.linkedin.com/jobs'
            }
            
            params = {
                'keywords': search_query if search_query else 'software engineer',
                'location': location if location else 'Remote',
                'position': 1,
                'pageNum': 0,
                'start': 0,
                'count': 25
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse HTML response
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='base-card')
            
            print(f"Found {len(job_cards)} job cards on LinkedIn")
            
            for card in job_cards[:25]:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    title = title_elem.get_text(strip=True) if title_elem else 'Unknown'
                    
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
                    
                    location_elem = card.find('span', class_='job-search-card__location')
                    job_location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                    
                    link_elem = card.find('a', class_='base-card__full-link')
                    job_url = link_elem['href'] if link_elem else '#'
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'description': 'View on LinkedIn for full description',
                        'url': job_url,
                        'salary': None
                    }
                    jobs.append(job)
                    print(f"  - {job['title']} at {job['company']}")
                    
                except Exception as e:
                    print(f"Error processing job card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error fetching from LinkedIn: {e}")
        
        print(f"Total jobs from LinkedIn: {len(jobs)}")
        return jobs
