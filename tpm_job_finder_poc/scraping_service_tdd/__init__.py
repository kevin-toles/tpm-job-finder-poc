"""
Scraping Service TDD Package

This package contains the Test-Driven Development implementation of the
Scraping Service microservice. The implementation follows strict TDD
methodology where tests define the requirements before implementation.

TDD Process:
1. RED: Write failing tests that define the interface (REWRITTEN FOR TRUE TDD)
2. GREEN: Implement minimal code to pass tests (PENDING)
3. REFACTOR: Optimize while keeping tests passing (PENDING)

The service will be implemented to satisfy all the interface contracts
defined in the comprehensive test suite that tests REAL requirements
from the README.md documentation.

Key Requirements Tested:
- Multi-source orchestration (Indeed, LinkedIn, ZipRecruiter, Greenhouse)
- Browser automation with Selenium WebDriver
- Anti-detection mechanisms (user agent rotation, viewport randomization)
- Service registry for scraper discovery and management
- Health monitoring and rate limiting enforcement
- Performance requirements (50-100 jobs/minute throughput)
- Error handling and recovery (browser crashes, timeouts)
- Configuration management with environment variables
"""

from .service import ScrapingServiceTDD

__all__ = ["ScrapingServiceTDD"]