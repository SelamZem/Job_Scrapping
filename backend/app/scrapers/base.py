from abc import ABC, abstractmethod
from typing import List, Dict
import random
import requests
from bs4 import BeautifulSoup
import re

class BaseScraper(ABC):
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def get_headers(self):
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    @abstractmethod
    def scrape_jobs(self, search_query: str, location: str = "", max_pages: int = 2) -> List[Dict]:
        raise NotImplementedError("Subclasses must implement scrape_jobs")
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace"""
        if not text:
            return ""
        return ' '.join(text.split())
    
    def strip_html(self, text: str) -> str:
        """Strip HTML tags from text"""
        if not text:
            return ""
        # Use BeautifulSoup to strip HTML
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def _get_page(self, url: str) -> BeautifulSoup:
        headers = self.get_headers()
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            response = session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        return " ".join(text.split())
