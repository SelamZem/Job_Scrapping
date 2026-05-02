from typing import List, Dict
from app.scrapers.base import BaseScraper

class SampleDataScraper(BaseScraper):
    """Fallback scraper that returns sample job data when real scraping fails"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        print("Using sample data scraper (fallback)")
        
        sample_jobs = [
            {
                'title': f'{search_query} - Senior Position',
                'company': 'Tech Corp Inc.',
                'location': location if location else 'Remote',
                'description': f'We are looking for an experienced {search_query} to join our team. Requirements include strong technical skills, problem-solving abilities, and experience with modern frameworks.',
                'url': 'https://example.com/job/1',
                'salary': '$120,000 - $150,000'
            },
            {
                'title': f'{search_query} - Mid Level',
                'company': 'Innovation Labs',
                'location': location if location else 'Remote',
                'description': f'Join our growing team as a {search_query}. You will work on cutting-edge projects and collaborate with talented engineers.',
                'url': 'https://example.com/job/2',
                'salary': '$90,000 - $120,000'
            },
            {
                'title': f'{search_query} - Junior Developer',
                'company': 'Startup XYZ',
                'location': location if location else 'Remote',
                'description': f'Great opportunity for a junior {search_query} to learn and grow. We offer mentorship and exciting projects.',
                'url': 'https://example.com/job/3',
                'salary': '$60,000 - $80,000'
            },
            {
                'title': f'Lead {search_query}',
                'company': 'Enterprise Solutions',
                'location': location if location else 'New York, NY',
                'description': f'Lead our {search_query} team and drive technical excellence. Must have 5+ years of experience.',
                'url': 'https://example.com/job/4',
                'salary': '$150,000 - $180,000'
            },
            {
                'title': f'{search_query} - Contract',
                'company': 'Agency One',
                'location': location if location else 'Remote',
                'description': f'6-month contract for a skilled {search_query}. Flexible hours and competitive rate.',
                'url': 'https://example.com/job/5',
                'salary': '$70 - $90/hour'
            }
        ]
        
        return sample_jobs
