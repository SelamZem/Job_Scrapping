import sys
from app.scrapers.findwork_api_scraper import FindWorkAPIScraper

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scraper = FindWorkAPIScraper()
jobs = scraper.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs)} real jobs from FindWork API')
for job in jobs[:10]:
    print(f"- {job['title']} at {job['company']}")
