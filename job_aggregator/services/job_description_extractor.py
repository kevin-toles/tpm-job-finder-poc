"""
Job Description Extraction Service
Scaffolds site-specific adapters and a generic fallback for extracting job descriptions from job URLs.
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

class JobDescriptionExtractor:
    def __init__(self):
        self.adapters = {
            'greenhouse.io': self._extract_greenhouse,
            'lever.co': self._extract_lever,
            'remoteok.com': self._extract_remoteok,
            # Add more site adapters here
        }

    def extract(self, url: str) -> Optional[str]:
        for domain, adapter in self.adapters.items():
            if domain in url:
                return adapter(url)
        return self._extract_generic(url)

    def _extract_greenhouse(self, url: str) -> Optional[str]:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            desc = soup.find('div', class_='description')
            return desc.get_text(strip=True) if desc else None
        except Exception:
            return None

    def _extract_lever(self, url: str) -> Optional[str]:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            desc = soup.find('div', class_='content')
            return desc.get_text(strip=True) if desc else None
        except Exception:
            return None

    def _extract_remoteok(self, url: str) -> Optional[str]:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            desc = soup.find('div', class_='job-description')
            return desc.get_text(strip=True) if desc else None
        except Exception:
            return None

    def _extract_generic(self, url: str) -> Optional[str]:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Try common patterns
            for cls in ['description', 'job-description', 'content', 'details']:
                desc = soup.find('div', class_=cls)
                if desc:
                    return desc.get_text(strip=True)
            # Fallback: get largest text block
            paragraphs = soup.find_all('p')
            if paragraphs:
                return max((p.get_text(strip=True) for p in paragraphs), key=len, default=None)
            return None
        except Exception:
            return None
