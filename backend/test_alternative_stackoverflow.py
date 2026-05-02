import sys
from app.scrapers.alternative_stackoverflow_scraper import AlternativeStackOverflowScraper

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scraper = AlternativeStackOverflowScraper()
jobs = scraper.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs)} real jobs from Stack Overflow (alternative)')
for job in jobs[:10]:
    print(f"- {job['title']} at {job['company']}")
