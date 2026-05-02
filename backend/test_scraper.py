from app.scrapers import SampleDataScraper

scraper = SampleDataScraper()
jobs = scraper.scrape_jobs('Software Engineer', 'Remote')
print(f'Found {len(jobs)} sample jobs')
for job in jobs:
    print(f"- {job['title']} at {job['company']}")
