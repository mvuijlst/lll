import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_site.settings')
django.setup()

# Import models
from academies.models import Academy, Category, Offering, Language

def test_import():
    """Test that the import was successful by printing statistics."""
    
    # Get counts
    academy_count = Academy.objects.count()
    category_count = Category.objects.count()
    offering_count = Offering.objects.count()
    language_count = Language.objects.count()
    
    print("\n=== IMPORT TEST RESULTS ===")
    print(f"Academies: {academy_count}")
    print(f"Categories: {category_count}")
    print(f"Offerings: {offering_count}")
    print(f"Languages: {language_count}")
    
    # Check specific academy data
    if academy_count > 0:
        first_academy = Academy.objects.first()
        print(f"\nFirst Academy: {first_academy.name}")
        print(f"Base URL: {first_academy.base_url}")
        print(f"Color: {first_academy.colour}")
        
        # Check categories for this academy
        academy_categories = Category.objects.filter(academy=first_academy)
        print(f"\nCategories for {first_academy.name}: {academy_categories.count()}")
        for i, category in enumerate(academy_categories[:5]):
            print(f"{i+1}. {category.name}")
        
        if academy_categories.count() > 5:
            print(f"...and {academy_categories.count() - 5} more categories")
        
        # Check offerings for this academy
        academy_offerings = Offering.objects.filter(academy=first_academy)
        print(f"\nOfferings for {first_academy.name}: {academy_offerings.count()}")
        for i, offering in enumerate(academy_offerings[:5]):
            print(f"{i+1}. {offering.title}")
        
        if academy_offerings.count() > 5:
            print(f"...and {academy_offerings.count() - 5} more offerings")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_import()
