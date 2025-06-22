import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_site.settings')
django.setup()

# Import models
from academies.models import Academy, Category, Offering, Language

def test_categories():
    """Test that categories are properly assigned to offerings."""
    
    total_offerings = Offering.objects.count()
    offerings_with_category = Offering.objects.exclude(category__isnull=True).count()
    
    print(f"\n=== CATEGORY ASSIGNMENT TEST ===")
    print(f"Total offerings: {total_offerings}")
    print(f"Offerings with assigned category: {offerings_with_category}")
    print(f"Percentage with category: {offerings_with_category / total_offerings * 100:.2f}%")
    
    # Get offerings without category
    offerings_without_category = Offering.objects.filter(category__isnull=True)
    print(f"\nOfferings without category: {offerings_without_category.count()}")
    
    # Display first 5 offerings without category if any
    if offerings_without_category.exists():
        print("\nSample offerings without category:")
        for i, offering in enumerate(offerings_without_category[:5]):
            print(f"{i+1}. {offering.title} (Academy: {offering.academy.name})")
    
    # Display category distribution
    print("\nCategory distribution:")
    categories = Category.objects.all().order_by('academy__name', 'name')
    for category in categories:
        offering_count = Offering.objects.filter(category=category).count()
        if offering_count > 0:
            print(f"- {category.name} ({category.academy.name}): {offering_count} offerings")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_categories()
