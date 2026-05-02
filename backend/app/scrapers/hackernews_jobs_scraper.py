from typing import List, Dict
from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup
import re

class HackerNewsJobsScraper(BaseScraper):
    """Scrapes jobs from Hacker News 'Who is Hiring' monthly threads"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            # Hacker News Algolia API - search for "Who is Hiring" posts
            # Get the latest "Who is Hiring" post
            url = "https://hn.algolia.com/api/v1/search_by_date"
            
            print(f"Fetching jobs from Hacker News 'Who is Hiring'")
            
            # Search for the latest "Who is Hiring" thread
            params = {
                'query': 'Who is hiring',
                'tags': 'story',
                'restrictSearchableAttributes': 'title',
                'hitsPerPage': 5
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'hits' in data and len(data['hits']) > 0:
                # Get the most recent "Who is Hiring" post
                hiring_post = None
                for hit in data['hits']:
                    title = hit.get('title', '')
                    if 'who is hiring' in title.lower():
                        hiring_post = hit
                        break
                
                if not hiring_post:
                    print("No 'Who is Hiring' post found")
                    return jobs
                
                object_id = hiring_post.get('objectID')
                print(f"Found 'Who is Hiring' post: {hiring_post.get('title')}")
                
                # Get comments from the hiring post
                comments_url = f"https://hn.algolia.com/api/v1/search"
                comments_params = {
                    'query': search_query if search_query else '',
                    'tags': f'comment,story_{object_id}',
                    'hitsPerPage': 100
                }
                
                comments_response = requests.get(comments_url, params=comments_params, timeout=30)
                comments_response.raise_for_status()
                
                comments_data = comments_response.json()
                
                if 'hits' in comments_data:
                    job_list = comments_data['hits']
                    print(f"Found {len(job_list)} job comments")
                    
                    for job_data in job_list[:50]:
                        try:
                            text = job_data.get('text', '')
                            if not text:
                                continue
                            
                            # Clean HTML from text
                            text = self.strip_html(text)
                            
                            # Try to extract company and position from the text
                            lines = text.split('\n')
                            first_line = lines[0] if lines else ''
                            
                            # Common format: "Company | Position | Location"
                            # or "Company - Position - Location"
                            company = 'Unknown Company'
                            position = 'Software Engineer'
                            job_location = 'Remote'
                            
                            # Parse first line for company/position
                            if '|' in first_line:
                                parts = [p.strip() for p in first_line.split('|')]
                                if len(parts) >= 2:
                                    company = parts[0]
                                    position = parts[1]
                                    if len(parts) >= 3:
                                        job_location = parts[2]
                            elif '-' in first_line and first_line.count('-') >= 2:
                                parts = [p.strip() for p in first_line.split('-')]
                                if len(parts) >= 2:
                                    company = parts[0]
                                    position = parts[1]
                                    if len(parts) >= 3:
                                        job_location = parts[2]
                            else:
                                # Just use first line as position
                                position = first_line[:100] if first_line else position
                            
                            # Truncate description
                            description = text[:500] + '...' if len(text) > 500 else text
                            
                            # Get the comment URL
                            comment_id = job_data.get('objectID')
                            job_url = f"https://news.ycombinator.com/item?id={comment_id}"
                            
                            job = {
                                'title': position,
                                'company': company,
                                'location': job_location,
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
            print(f"Error fetching from Hacker News: {e}")
        
        print(f"Total jobs from Hacker News: {len(jobs)}")
        return jobs
