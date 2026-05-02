import sys
from app.scrapers.hackernews_jobs_scraper import HackerNewsJobsScraper

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scraper = HackerNewsJobsScraper()
jobs = scraper.scrape_jobs('developer', '', max_pages=1)
print(f'Found {len(jobs)} real jobs from Hacker News')
for job in jobs[:10]:
    print(f"- {job['title']} at {job['company']}")
