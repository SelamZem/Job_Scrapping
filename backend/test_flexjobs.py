import sys
from app.scrapers import RSSFlexJobsScraper

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scraper = RSSFlexJobsScraper()
jobs = scraper.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs)} real jobs from FlexJobs RSS')
for job in jobs[:10]:
    print(f"- {job['title']} at {job['company']}")
