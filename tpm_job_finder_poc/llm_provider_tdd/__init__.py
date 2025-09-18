"""
LLM Provider TDD Module

This module implements the LLM Provider Service following Test-Driven Development
methodology. The service provides unified access to multiple Large Language Model
providers with comprehensive error handling, fallback mechanisms, and monitoring.

Following established microservice patterns and TDD methodology.
"""

from .service import LLMProviderService
from .api import app

__all__ = ["LLMProviderService", "app"]

# Version information
__version__ = "1.0.0"
__author__ = "TPM Job Finder POC Team"
__description__ = "TDD-based LLM Provider Service for unified multi-provider LLM access"