from typing import List, Dict
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import time

class ZipRecruiterScraper(BaseScraper):
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        try:
            # Format query for URL
            query = search_query.replace(" ", "+")
            loc = location.replace(" ", "+") if location else ""
            
            for page in range(max_pages):
                url = f"https://www.ziprecruiter.com/jobs/search?search={query}&location={loc}"
                if page > 0:
                    url += f"&page={page+1}"
                
                print(f"Scraping ZipRecruiter page {page + 1}...")
                soup = self._get_page(url)
                
                # Try multiple selectors for job cards
                job_cards = soup.find_all('div', class_='job_result')
                if not job_cards:
                    job_cards = soup.find_all('div', {'class': 'job_card'})
                if not job_cards:
                    job_cards = soup.find_all('a', class_='job_link')
                
                print(f"Found {len(job_cards)} job cards on page {page + 1}")
                
                for card in job_cards:
                    try:
                        job = self._extract_job_data(card)
                        if job:
                            job['source'] = 'ziprecruiter'
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job: {e}")
                        continue
                
                # Rate limiting
                time.sleep(2)
                
                if len(job_cards) == 0:
                    break
                    
        except Exception as e:
            print(f"Error scraping ZipRecruiter: {e}")
            
        print(f"Total jobs scraped from ZipRecruiter: {len(jobs)}")
        return jobs
    
    def _extract_job_data(self, card: BeautifulSoup) -> Dict:
        # Try multiple selectors for title
        title_elem = card.find('h2', class_='job_title')
        if not title_elem:
            title_elem = card.find('a', class_='job_title')
        if not title_elem:
            title_elem = card.find('h2')
        
        # Try multiple selectors for company
        company_elem = card.find('span', class_='company_name')
        if not company_elem:
            company_elem = card.find('div', class_='company')
        
        # Try multiple selectors for location
        location_elem = card.find('div', class_='job_location')
        if not location_elem:
            location_elem = card.find('span', class_='location')
        
        # Try multiple selectors for link
        link_elem = card.find('a', class_='job_title')
        if not link_elem:
            link_elem = card.find('a', class_='job_link')
        
        if not title_elem:
            return None
            
        title = self._clean_text(title_elem.get_text())
        company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
        location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
        
        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                url = "https://www.ziprecruiter.com" + href
            elif href.startswith('http'):
                url = href
            else:
                url = "#"
        else:
            url = "#"
        
        # Try to get salary
        salary_elem = card.find('div', class_='job_salary')
        salary = self._clean_text(salary_elem.get_text()) if salary_elem else None
        
        description = f"Job listing for {title} at {company} in {location}. Click to view full details on ZipRecruiter."
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'salary': salary
        }
