import sys
from app.scrapers import RSSWeWorkRemotelyScraper, RSSStackOverflowScraper, GitHubJobsScraper

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("=== Testing We Work Remotely RSS ===")
scraper1 = RSSWeWorkRemotelyScraper()
jobs1 = scraper1.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs1)} jobs from We Work Remotely\n')

print("=== Testing Stack Overflow RSS ===")
scraper2 = RSSStackOverflowScraper()
jobs2 = scraper2.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs2)} jobs from Stack Overflow\n')

print("=== Testing GitHub Jobs API ===")
scraper3 = GitHubJobsScraper()
jobs3 = scraper3.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs3)} jobs from GitHub Jobs\n')

print(f"Total jobs from all new sources: {len(jobs1) + len(jobs2) + len(jobs3)}")
