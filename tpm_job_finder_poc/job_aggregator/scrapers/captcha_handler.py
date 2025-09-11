"""CAPTCHA detection and handling utilities."""

import asyncio
from typing import Optional, Tuple, Any
import logging
from bs4 import BeautifulSoup
import re
import json
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)

@dataclass
class CaptchaInfo:
    """Information about detected CAPTCHA."""
    type: str  # 'recaptcha', 'hcaptcha', 'custom', etc.
    site_key: Optional[str] = None
    form_action: Optional[str] = None
    challenge_url: Optional[str] = None
    image_data: Optional[str] = None

class CaptchaDetector:
    """Detects various types of CAPTCHAs in responses."""
    
    CAPTCHA_PATTERNS = [
        # reCAPTCHA
        {
            'type': 'recaptcha',
            'patterns': [
                r'www\.google\.com/recaptcha/api\.js',
                r'class=["\']g-recaptcha["\']',
                r'data-sitekey=["\']([^"\']+)["\']'
            ]
        },
        # hCaptcha
        {
            'type': 'hcaptcha',
            'patterns': [
                r'hcaptcha\.com/1/api\.js',
                r'class=["\']h-captcha["\']',
                r'data-sitekey=["\']([^"\']+)["\']'
            ]
        },
        # Custom/Simple CAPTCHAs
        {
            'type': 'custom',
            'patterns': [
                r'captcha\.(jpg|png|gif)',
                r'class=["\']captcha-image["\']',
                r'id=["\']captcha["\']',
                r'name=["\']captcha["\']'
            ]
        }
    ]
    
    def detect_captcha(self, html: str) -> Optional[CaptchaInfo]:
        """Detect if response contains a CAPTCHA.
        
        Args:
            html: HTML content to check
            
        Returns:
            CaptchaInfo if CAPTCHA detected, None otherwise
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        for captcha_type in self.CAPTCHA_PATTERNS:
            for pattern in captcha_type['patterns']:
                # Check script tags
                for script in soup.find_all('script'):
                    if script.string and re.search(pattern, script.string):
                        return self._extract_captcha_info(soup, captcha_type['type'])
                        
                # Check for elements matching pattern
                if re.search(pattern, html):
                    return self._extract_captcha_info(soup, captcha_type['type'])
                    
        return None
        
    def _extract_captcha_info(self, soup: BeautifulSoup, captcha_type: str) -> CaptchaInfo:
        """Extract detailed information about detected CAPTCHA.
        
        Args:
            soup: BeautifulSoup object of the page
            captcha_type: Type of CAPTCHA detected
            
        Returns:
            CaptchaInfo object with CAPTCHA details
        """
        info = CaptchaInfo(type=captcha_type)
        
        if captcha_type == 'recaptcha':
            captcha_div = soup.find('div', class_='g-recaptcha')
            if captcha_div:
                info.site_key = captcha_div.get('data-sitekey')
                form = captcha_div.find_parent('form')
                if form:
                    info.form_action = form.get('action')
                    
        elif captcha_type == 'hcaptcha':
            captcha_div = soup.find('div', class_='h-captcha')
            if captcha_div:
                info.site_key = captcha_div.get('data-sitekey')
                form = captcha_div.find_parent('form')
                if form:
                    info.form_action = form.get('action')
                    
        elif captcha_type == 'custom':
            img = soup.find('img', class_='captcha-image') or soup.find('img', id='captcha')
            if img and img.get('src'):
                info.challenge_url = img['src']
                
        return info

class CaptchaHandler:
    """Handles detected CAPTCHAs."""
    
    def __init__(self, service_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize handler with optional CAPTCHA solving service credentials."""
        self.service_url = service_url
        self.api_key = api_key
        self.detector = CaptchaDetector()
        
    async def handle_captcha(self, html: str, session: Any) -> Optional[dict]:
        """Handle CAPTCHA if detected in response.
        
        Args:
            html: HTML content to check
            session: aiohttp ClientSession for making requests
            
        Returns:
            Dict with CAPTCHA solution if solved, None if no CAPTCHA or unable to solve
        """
        captcha_info = self.detector.detect_captcha(html)
        if not captcha_info:
            return None
            
        logger.warning(f"CAPTCHA detected: {captcha_info.type}")
        
        if not self.service_url or not self.api_key:
            logger.error("No CAPTCHA solving service configured")
            return None
            
        try:
            solution = await self._solve_captcha(captcha_info, session)
            return solution
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return None
            
    async def _solve_captcha(self, info: CaptchaInfo, session: Any) -> dict:
        """Attempt to solve CAPTCHA using configured service.
        
        Args:
            info: CaptchaInfo object with CAPTCHA details
            session: aiohttp ClientSession for making requests
            
        Returns:
            Dict with solution information
            
        Raises:
            Exception if unable to solve CAPTCHA
        """
        # This is where you'd implement the actual CAPTCHA solving logic,
        # typically by calling an external service API
        raise NotImplementedError("CAPTCHA solving not implemented")
