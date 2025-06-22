"""
Test script to check that offerings correctly have multiple categories.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_site.settings')
django.setup()

from academies.models import Offering, Category
from django.db.models import Count

# Get offerings with multiple categories
offerings_with_multiple = Offering.objects.annotate(
    category_count=Count('categories')
).filter(category_count__gt=1).order_by('-category_count')

print(f"Found {offerings_with_multiple.count()} offerings with multiple categories")

# Print the top 10 offerings with the most categories
print("\nTop 10 offerings with the most categories:")
for i, offering in enumerate(offerings_with_multiple[:10], 1):
    print(f"{i}. {offering.title} ({offering.academy.name})")
    print(f"   Categories ({offering.categories.count()}):")
    for category in offering.categories.all():
        print(f"   - {category.name}")
    print()

# Print some statistics
total_offerings = Offering.objects.count()
offerings_with_no_categories = Offering.objects.annotate(
    category_count=Count('categories')
).filter(category_count=0).count()

print(f"Total offerings: {total_offerings}")
print(f"Offerings with no categories: {offerings_with_no_categories}")
print(f"Offerings with one category: {total_offerings - offerings_with_multiple.count() - offerings_with_no_categories}")
print(f"Offerings with multiple categories: {offerings_with_multiple.count()}")
