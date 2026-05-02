from typing import List, Dict
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import requests
import time

class IndeedScraper(BaseScraper):
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        try:
            # Format query for URL
            query = search_query.replace(" ", "+")
            loc = location.replace(" ", "+") if location else ""
            
            for page in range(max_pages):
                start = page * 10
                url = f"https://www.indeed.com/jobs?q={query}&l={loc}&start={start}"
                
                print(f"Scraping Indeed page {page + 1}...")
                soup = self._get_page(url)
                
                # Try multiple selectors for job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                if not job_cards:
                    job_cards = soup.find_all('div', {'class': 'jobsearch-SerpJobCard'})
                if not job_cards:
                    job_cards = soup.find_all('div', {'class': 'slider_item'})
                
                print(f"Found {len(job_cards)} job cards on page {page + 1}")
                
                for card in job_cards:
                    try:
                        job = self._extract_job_data(card)
                        if job:
                            job['source'] = 'indeed'
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job: {e}")
                        continue
                
                # Rate limiting
                time.sleep(2)
                
                if len(job_cards) == 0:
                    break
                    
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
            
        print(f"Total jobs scraped from Indeed: {len(jobs)}")
        return jobs
    
    def _extract_job_data(self, card: BeautifulSoup) -> Dict:
        # Try multiple selectors for title
        title_elem = card.find('h2', class_='jobTitle')
        if not title_elem:
            title_elem = card.find('a', {'data-jk': True})
        if not title_elem:
            title_elem = card.find('h2')
        
        # Try multiple selectors for company
        company_elem = card.find('span', {'data-testid': 'company-name'})
        if not company_elem:
            company_elem = card.find('span', class_='companyName')
        if not company_elem:
            company_elem = card.find('div', class_='companyName')
        
        # Try multiple selectors for location
        location_elem = card.find('div', {'data-testid': 'text-location'})
        if not location_elem:
            location_elem = card.find('div', class_='companyLocation')
        if not location_elem:
            location_elem = card.find('div', class_='location')
        
        # Try multiple selectors for link
        link_elem = card.find('a', class_='jcs-JobTitle')
        if not link_elem:
            link_elem = card.find('a', {'data-jk': True})
        if not link_elem:
            link_elem = card.find('h2').find('a') if card.find('h2') else None
        
        if not title_elem:
            return None
            
        title = self._clean_text(title_elem.get_text())
        company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
        location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
        
        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                url = "https://www.indeed.com" + href
            elif href.startswith('http'):
                url = href
            else:
                url = "https://www.indeed.com/viewjob?jk=" + link_elem.get('data-jk', '')
        else:
            url = "#"
        
        # Try to get salary
        salary_elem = card.find('div', {'data-testid': 'salary-snippet'})
        salary = self._clean_text(salary_elem.get_text()) if salary_elem else None
        
        # Get job description from detail page (skip for performance)
        description = f"Job listing for {title} at {company} in {location}. Click to view full details."
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'salary': salary
        }
    
    def _get_job_description(self, url: str) -> str:
        try:
            soup = self._get_page(url)
            desc_elem = soup.find('div', {'data-testid': 'jobsearch-JobDescription'})
            if desc_elem:
                return self._clean_text(desc_elem.get_text())
        except:
            pass
        return "Description not available"
