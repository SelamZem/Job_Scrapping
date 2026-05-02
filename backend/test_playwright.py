from app.scrapers import PlaywrightIndeedScraper

scraper = PlaywrightIndeedScraper()
jobs = scraper.scrape_jobs('Software Engineer', 'Remote', max_pages=1)
print(f'Found {len(jobs)} real jobs from Indeed')
for job in jobs:
    print(f"- {job['title']} at {job['company']} - {job['location']}")
