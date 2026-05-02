import sys
from app.scrapers.landing_jobs_scraper import LandingJobsScraper

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scraper = LandingJobsScraper()
jobs = scraper.scrape_jobs('developer', '', max_pages=1)
print(f'Found {len(jobs)} real jobs from Landing.jobs API')
for job in jobs[:10]:
    print(f"- {job['title']} at {job['company']}")
