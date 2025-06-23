#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append('c:\\Users\\mvuijlst\\OneDrive - UGent\\Projects\\lll')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_site.settings')
django.setup()

from django.utils import timezone
from django.db.models import Q, Min, Count
from academies.models import Offering, Academy, Language

# Replicate the exact logic from offering_list view
def test_offering_list():
    from django.utils import timezone
    
    offerings = Offering.objects.select_related(
        'academy', 'category', 'language'
    ).prefetch_related(
        'variations__location', 'categories'
    ).filter(is_active=True)
    print(f"Initial offerings: {offerings.count()}")
    
    # No search query, academy filter, or language filter
    search_query = None
    academy_filter = None
    language_filter = None
    
    # Filter by upcoming (default is on)
    show_upcoming = True  # Default when clicking Filter
    if show_upcoming:
        now = timezone.now()
        offerings = offerings.filter(
            Q(variations__start_date__gte=now) | Q(variations__start_date__isnull=True)
        ).distinct()
        print(f"After upcoming filter: {offerings.count()}")
    
    # Sort by date (default)
    sort_by = 'date'
    if sort_by == 'date':
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
        print(f"After sorting by date: {offerings.count()}")
    
    print(f"Final count: {offerings.count()}")
    
    # Let's see the first few offerings
    print("\nFirst 10 offerings:")
    for i, offering in enumerate(offerings[:10]):
        print(f"{i+1}. {offering.title} (Academy: {offering.academy.name})")
    
    return offerings

result = test_offering_list()
