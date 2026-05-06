from typing import List, Dict
from app.scrapers.base import BaseScraper
import feedparser
import requests

class RSSWeWorkRemotelyScraper(BaseScraper):
    """Scrapes jobs from We Work Remotely RSS feed"""
    
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        jobs = []

        try:
            # We Work Remotely RSS feed
            urls = [
                "https://weworkremotely.com/categories/remote-programming-jobs.rss",
                "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
                "https://weworkremotely.com/categories/remote-design-jobs.rss"
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            for url in urls:
                try:
                    print(f"Fetching jobs from We Work Remotely RSS: {url}")

                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()

                    feed = feedparser.parse(response.content)

                    if feed.entries:
                        print(f"Found {len(feed.entries)} jobs in RSS feed")

                        # Filter by search query if provided
                        search_lower = search_query.lower() if search_query else ""

                        for entry in feed.entries[:50]:
                            try:
                                title = entry.get('title', 'Unknown')

                                # Filter by search query
                                if search_lower and search_lower not in title.lower():
                                    continue

                                # Parse title to extract company and position
                                parts = title.split(':')
                                if len(parts) >= 2:
                                    company = parts[0].strip()
                                    position = ':'.join(parts[1:]).strip()
                                else:
                                    company = 'Unknown Company'
                                    position = title

                                description = entry.get('summary', 'No description available')
                                description = self.strip_html(description)
                                if len(description) > 500:
                                    description = description[:500] + '...'

                                job = {
                                    'title': position,
                                    'company': company,
                                    'location': 'Remote',
                                    'description': description,
                                    'url': entry.get('link', '#'),
                                    'salary': None
                                }
                                jobs.append(job)
                                print(f"  - {job['title']} at {job['company']}")

                            except Exception as e:
                                print(f"Error processing job: {e}")
                                continue

                        if len(jobs) >= 20:  # Got enough jobs
                            break

                except Exception as e:
                    print(f"Error fetching from {url}: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching from We Work Remotely RSS: {e}")

        print(f"Total jobs from We Work Remotely RSS: {len(jobs)}")
        return jobs
