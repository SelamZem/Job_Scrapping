from typing import List, Dict
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import time

class GlassdoorScraper(BaseScraper):
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        try:
            # Format query for URL
            query = search_query.replace(" ", "-").lower()
            loc = location.replace(" ", "-").lower() if location else ""
            
            for page in range(max_pages):
                url = f"https://www.glassdoor.com/Job/{query}-jobs-SRCH_KO0,{page+1}.htm?includeNoSalaryJobs=true"
                if loc:
                    url = f"https://www.glassdoor.com/Job/{query}-jobs-{loc}-SRCH_IL.0,{page+1}_IL.0,{page+1}.htm"
                
                print(f"Scraping Glassdoor page {page + 1}...")
                soup = self._get_page(url)
                
                # Try multiple selectors for job cards
                job_cards = soup.find_all('li', class_='JobsList__JobListItem__css-1sqjxhz')
                if not job_cards:
                    job_cards = soup.find_all('div', class_='jobCard')
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-test': 'job-item'})
                
                print(f"Found {len(job_cards)} job cards on page {page + 1}")
                
                for card in job_cards:
                    try:
                        job = self._extract_job_data(card)
                        if job:
                            job['source'] = 'glassdoor'
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job: {e}")
                        continue
                
                # Rate limiting
                time.sleep(2)
                
                if len(job_cards) == 0:
                    break
                    
        except Exception as e:
            print(f"Error scraping Glassdoor: {e}")
            
        print(f"Total jobs scraped from Glassdoor: {len(jobs)}")
        return jobs
    
    def _extract_job_data(self, card: BeautifulSoup) -> Dict:
        # Try multiple selectors for title
        title_elem = card.find('a', class_='JobCard__JobTitle__css-1g5zgie')
        if not title_elem:
            title_elem = card.find('a', {'data-test': 'job-title'})
        if not title_elem:
            title_elem = card.find('h3')
        
        # Try multiple selectors for company
        company_elem = card.find('span', class_='JobCard__CompanyInfo__css-1v7o29d')
        if not company_elem:
            company_elem = card.find('span', {'data-test': 'company-name'})
        if not company_elem:
            company_elem = card.find('div', class_='css-1vh5rwk')
        
        # Try multiple selectors for location
        location_elem = card.find('div', class_='JobCard__Location__css-1v7o29d')
        if not location_elem:
            location_elem = card.find('span', {'data-test': 'location'})
        if not location_elem:
            location_elem = card.find('div', class_='css-1vh5rwk')
        
        # Try multiple selectors for link
        link_elem = card.find('a', class_='JobCard__JobTitle__css-1g5zgie')
        if not link_elem:
            link_elem = card.find('a', {'data-test': 'job-title'})
        
        if not title_elem:
            return None
            
        title = self._clean_text(title_elem.get_text())
        company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
        location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
        
        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                url = "https://www.glassdoor.com" + href
            elif href.startswith('http'):
                url = href
            else:
                url = "#"
        else:
            url = "#"
        
        # Try to get salary
        salary_elem = card.find('span', class_='JobCard__Salary__css-1v7o29d')
        salary = self._clean_text(salary_elem.get_text()) if salary_elem else None
        
        description = f"Job listing for {title} at {company} in {location}. Click to view full details on Glassdoor."
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'salary': salary
        }
