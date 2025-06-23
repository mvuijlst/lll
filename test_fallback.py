#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_site.settings')
django.setup()

from academies.models import Offering

def test_fallback_images():
    print("Testing fallback image functionality...")
    print("=" * 50)
    
    # Test with offerings that don't have images
    offerings = Offering.objects.filter(image_url='').select_related('academy')[:5]
    
    for offering in offerings:
        print(f"Academy: {offering.academy.name}")
        print(f"Offering: {offering.title[:60]}...")
        print(f"Original image URL: {offering.image_url or 'None'}")
        print(f"Display image URL: {offering.get_display_image_url()}")
        print("-" * 30)
    
    # Test consistency
    print("\nTesting consistency (same offering, multiple calls):")
    print("=" * 50)
    if offerings:
        test_offering = offerings[0]
        for i in range(3):
            print(f"Call {i+1}: {test_offering.get_display_image_url()}")

if __name__ == "__main__":
    test_fallback_images()
