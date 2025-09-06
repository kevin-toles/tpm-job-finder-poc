"""
Application settings and configuration management.

This module handles loading and managing application configuration
from environment variables and configuration files.
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field


class JobFinderSettings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    lever_api_key: Optional[str] = Field(None, env="LEVER_API_KEY")
    indeed_api_key: Optional[str] = Field(None, env="INDEED_API_KEY")
    linkedin_api_key: Optional[str] = Field(None, env="LINKEDIN_API_KEY")
    
    # Database Configuration
    database_url: str = Field("sqlite:///jobs.db", env="DATABASE_URL")
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    
    # Application Configuration
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_concurrent_requests: int = Field(10, env="MAX_CONCURRENT_REQUESTS")
    
    # Job Search Configuration
    default_search_radius: int = Field(50, env="DEFAULT_SEARCH_RADIUS")  # miles
    max_job_age_days: int = Field(30, env="MAX_JOB_AGE_DAYS")
    min_salary_threshold: int = Field(80000, env="MIN_SALARY_THRESHOLD")
    
    # Rate Limiting
    requests_per_minute: int = Field(60, env="REQUESTS_PER_MINUTE")
    requests_per_hour: int = Field(1000, env="REQUESTS_PER_HOUR")
    
    # Email Configuration
    smtp_host: Optional[str] = Field(None, env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    
    # Feature Flags
    enable_email_notifications: bool = Field(False, env="ENABLE_EMAIL_NOTIFICATIONS")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    enable_rate_limiting: bool = Field(True, env="ENABLE_RATE_LIMITING")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = JobFinderSettings()


def get_connector_config(connector_name: str) -> dict:
    """
    Get configuration for a specific job board connector.
    
    Args:
        connector_name: Name of the connector
        
    Returns:
        Configuration dictionary
    """
    configs = {
        'lever': {
            'api_key': settings.lever_api_key,
            'base_url': 'https://api.lever.co/v0',
            'rate_limit': 100  # requests per hour
        },
        'indeed': {
            'api_key': settings.indeed_api_key,
            'base_url': 'https://api.indeed.com',
            'rate_limit': 1000
        },
        'linkedin': {
            'api_key': settings.linkedin_api_key,
            'base_url': 'https://api.linkedin.com',
            'rate_limit': 500
        }
    }
    
    return configs.get(connector_name, {})


def get_search_keywords() -> List[str]:
    """Get default search keywords for TPM positions."""
    return [
        "technical program manager",
        "tpm",
        "technical programme manager",
        "program manager technical",
        "technical project manager",
        "engineering program manager",
        "product technical manager"
    ]


def get_excluded_companies() -> List[str]:
    """Get list of companies to exclude from searches."""
    # This could be loaded from a config file or database
    return []


def validate_settings() -> bool:
    """
    Validate that required settings are configured.
    
    Returns:
        True if settings are valid
    """
    required_for_production = [
        'database_url',
    ]
    
    for setting in required_for_production:
        if not getattr(settings, setting):
            return False
    
    return True