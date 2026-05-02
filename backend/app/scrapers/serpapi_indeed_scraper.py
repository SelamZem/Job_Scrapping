from typing import List, Dict
from app.scrapers.base import BaseScraper
from serpapi import GoogleSearch
import os

class SerpAPIIndeedScraper(BaseScraper):
    """Scrapes jobs from Indeed using SerpAPI (handles anti-scraping, requires API key)"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        # Check for API key in environment
        api_key = os.getenv('SERPAPI_KEY')
        if not api_key:
            print("SerpAPI key not found in environment variables. Skipping Indeed scraping.")
            print("Get a free API key from https://serpapi.com/ and add SERPAPI_KEY to .env")
            return jobs
        
        try:
            print(f"Fetching jobs from Indeed via SerpAPI for: {search_query}")
            
            for page in range(max_pages):
                params = {
                    "engine": "google_jobs",
                    "q": f"{search_query} jobs",
                    "location": location if location else "United States",
                    "api_key": api_key,
                    "start": page * 10
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                if 'jobs_results' in results:
                    job_list = results['jobs_results']
                    print(f"Found {len(job_list)} jobs on page {page + 1}")
                    
                    for job_data in job_list:
                        try:
                            job = {
                                'title': job_data.get('title', 'Unknown'),
                                'company': job_data.get('company_name', 'Unknown Company'),
                                'location': job_data.get('location', 'Remote') or 'Remote',
                                'description': job_data.get('description', '')[:500] + '...' if len(job_data.get('description', '')) > 500 else job_data.get('description', 'No description available'),
                                'url': job_data.get('job_link', '#'),
                                'salary': self._extract_salary(job_data)
                            }
                            jobs.append(job)
                            print(f"  - {job['title']} at {job['company']}")
                        except Exception as e:
                            print(f"Error processing job: {e}")
                            continue
                else:
                    print(f"No jobs found on page {page + 1}")
                    break
            
        except Exception as e:
            print(f"Error fetching from SerpAPI: {e}")
        
        print(f"Total jobs from Indeed (via SerpAPI): {len(jobs)}")
        return jobs
    
    def _extract_salary(self, job_data: Dict) -> str:
        """Try to extract salary information"""
        # Check for salary in different fields
        salary = job_data.get('salary')
        if salary:
            return salary
        
        # Check in description
        description = job_data.get('description', '').lower()
        salary_keywords = ['salary', '$', 'per year', 'per hour', 'k-', 'annual']
        
        if any(keyword in description for keyword in salary_keywords):
            return "See job description for salary"
        
        return None
