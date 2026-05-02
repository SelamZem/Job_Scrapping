import sys
from app.scrapers import (
    RemotiveAPIScraper, 
    ArbeitnowAPIScraper, 
    RSSWeWorkRemotelyScraper, 
    RSSRemoteOKScraper,
    RSSStackOverflowScraper,
    GitHubJobsScraper,
    RSSFlexJobsScraper
)

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

scrapers = [
    ('Remotive', RemotiveAPIScraper()),
    ('Arbeitnow', ArbeitnowAPIScraper()),
    ('We Work Remotely RSS', RSSWeWorkRemotelyScraper()),
    ('RemoteOK RSS', RSSRemoteOKScraper()),
    ('Stack Overflow RSS', RSSStackOverflowScraper()),
    ('GitHub Jobs', GitHubJobsScraper()),
    ('FlexJobs RSS', RSSFlexJobsScraper())
]

total_jobs = 0
for name, scraper in scrapers:
    print(f"\n=== Testing {name} ===")
    try:
        jobs = scraper.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
        print(f"Found {len(jobs)} jobs")
        total_jobs += len(jobs)
    except Exception as e:
        print(f"Error: {e}")

print(f"\n=== Total jobs from all sources: {total_jobs} ===")
