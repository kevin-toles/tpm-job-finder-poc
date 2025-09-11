"""Browser behavior simulation utilities."""

import asyncio
import random
from typing import Optional, List, Tuple
from dataclasses import dataclass
import json
import os
from datetime import datetime, timedelta

@dataclass
class BrowserProfile:
    """Browser fingerprint profile."""
    user_agent: str
    viewport_width: int
    viewport_height: int
    screen_width: int
    screen_height: int
    color_depth: int
    pixel_ratio: float
    timezone: str
    language: str
    platform: str
    
    @classmethod
    def random_profile(cls) -> 'BrowserProfile':
        """Generate a random but realistic browser profile."""
        profiles = [
            BrowserProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport_width=1440,
                viewport_height=900,
                screen_width=2560,
                screen_height=1600,
                color_depth=24,
                pixel_ratio=2.0,
                timezone="America/Los_Angeles",
                language="en-US",
                platform="MacIntel"
            ),
            BrowserProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport_width=1920,
                viewport_height=1080,
                screen_width=1920,
                screen_height=1080,
                color_depth=24,
                pixel_ratio=1.0,
                timezone="America/New_York",
                language="en-US",
                platform="Win32"
            ),
            # Add more realistic profiles as needed
        ]
        return random.choice(profiles)

class BrowserSimulator:
    """Simulates realistic browser behavior."""
    
    def __init__(self, profile: Optional[BrowserProfile] = None):
        """Initialize simulator with optional browser profile."""
        self.profile = profile or BrowserProfile.random_profile()
        
    async def simulate_scroll(self, page_height: int) -> List[Tuple[int, float]]:
        """Simulate human-like scrolling behavior.
        
        Args:
            page_height: Total height of the page in pixels
            
        Returns:
            List of (scroll_position, delay) tuples
        """
        current_pos = 0
        scroll_points = []
        
        while current_pos < page_height:
            # Random scroll amount between 100-500 pixels
            scroll_amount = random.randint(100, 500)
            # Random delay between 0.5-2 seconds
            delay = random.uniform(0.5, 2.0)
            # Sometimes pause longer to simulate reading
            if random.random() < 0.2:
                delay += random.uniform(1.0, 3.0)
                
            current_pos = min(current_pos + scroll_amount, page_height)
            scroll_points.append((current_pos, delay))
            
        return scroll_points
        
    async def simulate_mouse_movement(self, elements: List[Tuple[int, int]]) -> List[Tuple[int, int, float]]:
        """Simulate human-like mouse movements between elements.
        
        Args:
            elements: List of (x, y) coordinates of elements to move between
            
        Returns:
            List of (x, y, delay) movement points
        """
        movements = []
        for i in range(len(elements) - 1):
            start = elements[i]
            end = elements[i + 1]
            
            # Generate intermediate points with Bezier curve
            points = self._generate_bezier_curve(start, end)
            
            # Add random delays between movements
            for point in points:
                delay = random.uniform(0.01, 0.1)
                movements.append((point[0], point[1], delay))
                
        return movements
        
    def _generate_bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int], points: int = 10) -> List[Tuple[int, int]]:
        """Generate a bezier curve between two points for natural mouse movement.
        
        Args:
            start: Starting coordinates
            end: Ending coordinates
            points: Number of points to generate
            
        Returns:
            List of (x, y) coordinates along the curve
        """
        # Create control point for curve
        control_x = random.randint(min(start[0], end[0]), max(start[0], end[0]))
        control_y = random.randint(min(start[1], end[1]), max(start[1], end[1]))
        
        curve_points = []
        for i in range(points):
            t = i / (points - 1)
            # Quadratic Bezier curve formula
            x = int((1-t)**2 * start[0] + 2*(1-t)*t * control_x + t**2 * end[0])
            y = int((1-t)**2 * start[1] + 2*(1-t)*t * control_y + t**2 * end[1])
            curve_points.append((x, y))
            
        return curve_points
        
    def generate_headers(self) -> dict:
        """Generate realistic browser headers.
        
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            'User-Agent': self.profile.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': self.profile.language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Sometimes add additional headers
        if random.random() < 0.5:
            headers['DNT'] = '1'
        
        return headers
