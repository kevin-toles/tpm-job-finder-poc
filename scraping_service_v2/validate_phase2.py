#!/usr/bin/env python3
"""
Simple Phase 2 validation script.

Tests that all scrapers can be imported and initialized without errors.
"""

import sys
from pathlib import Path

# Add the parent directory to path to import the package
sys.path.append(str(Path(__file__).parent.parent))

def test_scraper_imports():
    """Test that all scrapers can be imported."""
    print("🔍 Testing scraper imports...")
    
    try:
        from scraping_service_v2.scrapers import (
            BaseScraper,
            IndeedScraper,
            LinkedInScraper, 
            ZipRecruiterScraper,
            GreenhouseScraper
        )
        print("✅ All scraper imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_scraper_creation():
    """Test that all scrapers can be instantiated."""
    print("\n🏗️ Testing scraper instantiation...")
    
    try:
        from scraping_service_v2.scrapers import (
            IndeedScraper,
            LinkedInScraper,
            ZipRecruiterScraper, 
            GreenhouseScraper
        )
        
        # Create scrapers
        scrapers = [
            IndeedScraper(),
            LinkedInScraper(),
            ZipRecruiterScraper(),
            GreenhouseScraper()
        ]
        
        for scraper in scrapers:
            print(f"   ✅ {scraper.name} scraper created")
            print(f"      • Type: {scraper.source_type.value}")
            print(f"      • Base URL: {scraper.base_url}")
            
        print("✅ All scraper instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False

def test_service_registry():
    """Test service registry functionality."""
    print("\n📋 Testing service registry...")
    
    try:
        from scraping_service_v2 import registry
        
        # Register default scrapers
        registry.register_default_scrapers()
        
        # List sources
        sources = registry.list_sources()
        print(f"   📝 Registered sources: {sources}")
        
        # Get stats
        stats = registry.get_registry_stats()
        print(f"   📊 Total sources: {stats['total_sources']}")
        print(f"   📊 Source types: {stats['sources_by_type']}")
        
        print("✅ Service registry test successful")
        return True
    except Exception as e:
        print(f"❌ Service registry test failed: {e}")
        return False

def main():
    """Run Phase 2 validation tests."""
    print("🚀 Phase 2 Scraper Validation")
    print("="*40)
    
    success_count = 0
    total_tests = 3
    
    # Test imports
    if test_scraper_imports():
        success_count += 1
        
    # Test instantiation  
    if test_scraper_creation():
        success_count += 1
        
    # Test registry
    if test_service_registry():
        success_count += 1
        
    print("\n" + "="*40)
    print(f"📊 VALIDATION RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 Phase 2 implementation is structurally sound!")
        print("📝 All scrapers successfully created:")
        print("   • LinkedIn scraper with authentication support")
        print("   • ZipRecruiter scraper with job board parsing")  
        print("   • Greenhouse scraper with company discovery")
        print("   • Service registry integration")
        return 0
    else:
        print("❌ Some validation tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
