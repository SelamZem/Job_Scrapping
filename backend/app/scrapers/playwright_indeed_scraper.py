from typing import List, Dict
from app.scrapers.base import BaseScraper
from playwright.sync_api import sync_playwright
import time

class PlaywrightIndeedScraper(BaseScraper):
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        with sync_playwright() as p:
            # Launch with stealth options
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = context.new_page()
            
            # Add stealth scripts to hide automation
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            try:
                # Format query for URL
                query = search_query.replace(" ", "+")
                loc = location.replace(" ", "+") if location else ""
                
                for page_num in range(max_pages):
                    start = page_num * 10
                    url = f"https://www.indeed.com/jobs?q={query}&l={loc}&start={start}"
                    
                    print(f"Scraping Indeed page {page_num + 1} with Playwright...")
                    
                    # Navigate with longer timeout and different wait strategy
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    
                    # Wait a bit for dynamic content
                    time.sleep(3)
                    
                    # Scroll to bottom to trigger lazy loading
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(2)
                    
                    # Try to find job cards with multiple selectors
                    job_cards = page.query_selector_all('div.job_seen_beacon')
                    if not job_cards:
                        job_cards = page.query_selector_all('div[data-jk]')
                    if not job_cards:
                        job_cards = page.query_selector_all('.jobsearch-SerpJobCard')
                    if not job_cards:
                        job_cards = page.query_selector_all('[class*="job"]')
                    
                    print(f"Found {len(job_cards)} job cards on page {page_num + 1}")
                    
                    for card in job_cards:
                        try:
                            job = self._extract_job_data(page, card)
                            if job:
                                job['source'] = 'indeed'
                                jobs.append(job)
                        except Exception as e:
                            print(f"Error extracting job: {e}")
                            continue
                    
                    if len(job_cards) == 0:
                        break
                    
                    # Rate limiting
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Error scraping Indeed with Playwright: {e}")
            finally:
                context.close()
                browser.close()
        
        print(f"Total jobs scraped from Indeed: {len(jobs)}")
        return jobs
    
    def _extract_job_data(self, page, card) -> Dict:
        try:
            # Try to get title
            title_elem = card.query_selector('h2.jobTitle')
            if not title_elem:
                title_elem = card.query_selector('a[data-jk]')
            if not title_elem:
                title_elem = card.query_selector('h2')
            
            if not title_elem:
                return None
            
            title = title_elem.inner_text().strip()
            
            # Try to get company
            company_elem = card.query_selector('span[data-testid="company-name"]')
            if not company_elem:
                company_elem = card.query_selector('.companyName')
            
            company = company_elem.inner_text().strip() if company_elem else "Unknown Company"
            
            # Try to get location
            location_elem = card.query_selector('div[data-testid="text-location"]')
            if not location_elem:
                location_elem = card.query_selector('.companyLocation')
            
            location = location_elem.inner_text().strip() if location_elem else "Remote"
            
            # Try to get URL
            link_elem = card.query_selector('a.jcs-JobTitle')
            if not link_elem:
                link_elem = card.query_selector('a[data-jk]')
            
            if link_elem:
                href = link_elem.get_attribute('href')
                if href and href.startswith('/'):
                    url = "https://www.indeed.com" + href
                elif href and href.startswith('http'):
                    url = href
                else:
                    jk = link_elem.get_attribute('data-jk')
                    url = f"https://www.indeed.com/viewjob?jk={jk}" if jk else "#"
            else:
                url = "#"
            
            # Try to get salary
            salary_elem = card.query_selector('div[data-testid="salary-snippet"]')
            salary = salary_elem.inner_text().strip() if salary_elem else None
            
            description = f"Job listing for {title} at {company} in {location}. Click to view full details."
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': url,
                'salary': salary
            }
            
        except Exception as e:
            print(f"Error in _extract_job_data: {e}")
            return None
