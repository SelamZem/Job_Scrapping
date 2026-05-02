import sys
from app.scrapers.rss_workingnomads_scraper import RSSWorkingNomadsScraper

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scraper = RSSWorkingNomadsScraper()
jobs = scraper.scrape_jobs('Software Engineer', '', max_pages=1)
print(f'Found {len(jobs)} real jobs from Working Nomads RSS')
for job in jobs[:10]:
    print(f"- {job['title']} at {job['company']}")
