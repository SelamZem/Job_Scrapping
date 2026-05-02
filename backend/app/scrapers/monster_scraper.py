from typing import List, Dict
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import time

class MonsterScraper(BaseScraper):
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        try:
            # Format query for URL
            query = search_query.replace(" ", "-")
            loc = location.replace(" ", "-") if location else ""
            
            for page in range(max_pages):
                url = f"https://www.monster.com/jobs/search/?q={query}"
                if loc:
                    url += f"&where={loc}"
                if page > 0:
                    url += f"&page={page+1}"
                
                print(f"Scraping Monster page {page + 1}...")
                soup = self._get_page(url)
                
                # Try multiple selectors for job cards
                job_cards = soup.find_all('div', class_='card-content')
                if not job_cards:
                    job_cards = soup.find_all('section', class_='card')
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-testid': 'job-item'})
                
                print(f"Found {len(job_cards)} job cards on page {page + 1}")
                
                for card in job_cards:
                    try:
                        job = self._extract_job_data(card)
                        if job:
                            job['source'] = 'monster'
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job: {e}")
                        continue
                
                # Rate limiting
                time.sleep(2)
                
                if len(job_cards) == 0:
                    break
                    
        except Exception as e:
            print(f"Error scraping Monster: {e}")
            
        print(f"Total jobs scraped from Monster: {len(jobs)}")
        return jobs
    
    def _extract_job_data(self, card: BeautifulSoup) -> Dict:
        # Try multiple selectors for title
        title_elem = card.find('h2', class_='title')
        if not title_elem:
            title_elem = card.find('a', class_='job-title')
        if not title_elem:
            title_elem = card.find('h3')
        
        # Try multiple selectors for company
        company_elem = card.find('span', class_='company')
        if not company_elem:
            company_elem = card.find('div', class_='company-name')
        
        # Try multiple selectors for location
        location_elem = card.find('div', class_='location')
        if not location_elem:
            location_elem = card.find('span', class_='job-location')
        
        # Try multiple selectors for link
        link_elem = card.find('a', class_='job-title')
        if not link_elem:
            link_elem = card.find('a', {'data-testid': 'job-link'})
        
        if not title_elem:
            return None
            
        title = self._clean_text(title_elem.get_text())
        company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
        location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
        
        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                url = "https://www.monster.com" + href
            elif href.startswith('http'):
                url = href
            else:
                url = "#"
        else:
            url = "#"
        
        # Try to get salary
        salary_elem = card.find('div', class_='salary')
        salary = self._clean_text(salary_elem.get_text()) if salary_elem else None
        
        description = f"Job listing for {title} at {company} in {location}. Click to view full details on Monster."
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'salary': salary
        }
