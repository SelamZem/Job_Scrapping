from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
import os

class RapidAPIScraper(BaseScraper):
    """Scrapes jobs from RapidAPI (requires API key, free tier available)"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        # Check for API key in environment
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            print("RapidAPI key not found in environment variables. Skipping.")
            return jobs
        
        try:
            # Using JSearch API from RapidAPI (free tier available)
            url = "https://jsearch.p.rapidapi.com/search"
            
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            params = {
                "query": f"{search_query} in {location}" if location else search_query,
                "page": "1",
                "num_pages": str(max_pages)
            }
            
            print(f"Fetching jobs from RapidAPI JSearch for: {search_query}")
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                job_list = data['data']
                print(f"Found {len(job_list)} jobs from RapidAPI")
                
                for job_data in job_list[:50]:
                    try:
                        job = {
                            'title': job_data.get('job_title', 'Unknown'),
                            'company': job_data.get('employer_name', 'Unknown Company'),
                            'location': job_data.get('job_location', 'Remote') or 'Remote',
                            'description': job_data.get('job_description', '')[:500] + '...' if len(job_data.get('job_description', '')) > 500 else job_data.get('job_description', 'No description available'),
                            'url': job_data.get('job_apply_link', '#'),
                            'salary': job_data.get('job_min_salary') or job_data.get('job_max_salary')
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")
                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue
            
        except Exception as e:
            print(f"Error fetching from RapidAPI: {e}")
        
        print(f"Total jobs from RapidAPI: {len(jobs)}")
        return jobs
