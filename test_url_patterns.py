#!/usr/bin/env python3
"""
Test script to verify that the scraper can now find offerings 
with different URL patterns like /25-26/ instead of just /programma/
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'getdata'))

from scrape import AcademyScraper

def main():
    print("🧪 Testing Enhanced URL Pattern Recognition")
    print("=" * 60)
    print("Testing with Gandaius Academy to find /25-26/ offerings...")
    
    # Create scraper with just Gandaius Academy for testing
    test_scraper = AcademyScraper(["https://gandaiusacademy.ugent.be"])
    
    print(f"\n📋 Test target:")
    print(f"  1. Gandaius Academy: https://gandaiusacademy.ugent.be")
    print(f"  Expected to find: /25-26/bemiddeling and similar offerings")
    
    print(f"\n🚀 Starting test scrape...")
    print("=" * 60)
    
    result = test_scraper.run()
    
    if result:
        print(f"\n✅ Test completed!")
        print(f"📁 Data saved to: {result}")
        
        # Check if we found the specific offering mentioned
        found_bemiddeling = False
        for offering in test_scraper.scraped_data['offerings'].values():
            if 'bemiddeling' in offering['url'].lower():
                found_bemiddeling = True
                print(f"🎯 Found target offering: {offering['title']}")
                print(f"   URL: {offering['url']}")
                break
        
        if not found_bemiddeling:
            print(f"⚠️  Target offering 'bemiddeling' not found, but may have different path")
            
        print(f"\n📊 Total offerings found: {len(test_scraper.scraped_data['offerings'])}")
        
        # Show some examples of found URLs to verify pattern diversity
        print(f"\n🔍 Sample offering URLs found:")
        for i, offering in enumerate(list(test_scraper.scraped_data['offerings'].values())[:5], 1):
            print(f"  {i}. {offering['title'][:40]}...")
            print(f"     {offering['url']}")
            
    else:
        print(f"\n❌ Test failed.")

if __name__ == "__main__":
    main()
