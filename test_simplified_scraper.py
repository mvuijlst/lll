#!/usr/bin/env python3
"""
Test script to verify the simplified scraper logic works correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lll.settings')
django.setup()

from getdata.scrape import AcademyScraper

def test_simplified_scraper():
    """Test that the simplified scraper still finds all offerings"""
    print("🧪 Testing simplified scraper logic...")
    
    scraper = AcademyScraper()
    
    # Test with one academy
    test_url = "https://cursus.ugent.be/2024/nl/MC/programma"
    academy_name = "MCT"
    
    print(f"\n📋 Testing with: {academy_name}")
    print(f"🔗 URL: {test_url}")
    
    # Run the scraper
    try:
        success = scraper.scrape_main_page(test_url, academy_name)
        
        if success:
            offerings_count = len(scraper.scraped_data['offerings'])
            print(f"\n✅ Success! Found {offerings_count} offerings")
            
            # Show first few offerings for verification
            if offerings_count > 0:
                print("\n📄 Sample offerings found:")
                for i, (url, data) in enumerate(list(scraper.scraped_data['offerings'].items())[:5]):
                    print(f"  {i+1}. {data['title']}")
                    print(f"     URL: {url}")
                    print(f"     Categories: {', '.join(data['categories'])}")
                    print(f"     Fields: {len(data['fields'])}")
                    print()
                
                if offerings_count > 5:
                    print(f"  ... and {offerings_count - 5} more offerings")
            
            # Check for specific URL pattern
            bemiddeling_found = any('/bemiddeling' in url for url in scraper.scraped_data['offerings'].keys())
            if bemiddeling_found:
                print("✅ Found offerings with '/bemiddeling' pattern")
            else:
                print("ℹ️  No '/bemiddeling' offerings found (might not exist for this academy)")
                
        else:
            print("❌ Scraper failed")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simplified_scraper()
