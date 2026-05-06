from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests

class LandingJobsScraper(BaseScraper):
    """Scrapes jobs from Landing.jobs API"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []

        try:
            # Landing.jobs API
            url = "https://landing.jobs/api/v1/jobs"

            print(f"Fetching jobs from Landing.jobs API for: {search_query}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }

            params = {}
            if search_query:
                params['search'] = search_query
            if location:
                params['location'] = location
            else:
                params['remote'] = 'true'

            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, list):
                job_list = data
                print(f"Found {len(job_list)} jobs from Landing.jobs API")

                for job_data in job_list[:50]:
                    try:
                        description = job_data.get('description', 'No description available')
                        description = self.strip_html(description)
                        if len(description) > 500:
                            description = description[:500] + '...'

                        # Extract company name from URL (format: /at/company-name/...)
                        job_url = job_data.get('url', '')
                        company = 'Unknown Company'
                        if job_url and '/at/' in job_url:
                            parts = job_url.split('/at/')
                            if len(parts) > 1:
                                company = parts[1].split('/')[0].replace('-', ' ').title()

                        # Format salary if available
                        salary = None
                        if job_data.get('gross_salary_low') and job_data.get('gross_salary_high'):
                            salary = f"${job_data['gross_salary_low']:,} - ${job_data['gross_salary_high']:,}"

                        job = {
                            'title': job_data.get('title', 'Unknown'),
                            'company': company,
                            'location': 'Remote' if job_data.get('remote') else 'On-site',
                            'description': description,
                            'url': job_url if job_url else '#',
                            'salary': salary
                        }
                        jobs.append(job)
                        print(f"  - {job['title']} at {job['company']}")

                    except Exception as e:
                        print(f"Error processing job: {e}")
                        continue

        except Exception as e:
            print(f"Error fetching from Landing.jobs API: {e}")

        print(f"Total jobs from Landing.jobs API: {len(jobs)}")
        return jobs
