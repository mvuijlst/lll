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
from django.db.models import Q, Min
from academies.models import Offering
import datetime

# Test the filtering logic
now = timezone.now()
print(f"Current time: {now}")

# Get all active offerings
all_offerings = Offering.objects.filter(is_active=True)
print(f"Total active offerings: {all_offerings.count()}")

# Test the upcoming filter logic
upcoming_offerings = all_offerings.filter(
    Q(variations__start_date__gte=now) | Q(variations__start_date__isnull=True)
).distinct()
print(f"Offerings with upcoming variations: {upcoming_offerings.count()}")

# Check how many variations have null start dates
null_variations = all_offerings.filter(variations__start_date__isnull=True).distinct()
print(f"Offerings with NULL start date variations: {null_variations.count()}")

# Check how many have future dates
future_variations = all_offerings.filter(variations__start_date__gte=now).distinct()
print(f"Offerings with future start date variations: {future_variations.count()}")

# Let's see what happens when we sort by date
sorted_upcoming = upcoming_offerings.annotate(
    earliest_date=Min('variations__start_date')
).order_by('earliest_date', 'title')
print(f"After sorting by date: {sorted_upcoming.count()}")

# Check if the issue is with the is_available filter
available_variations = all_offerings.filter(variations__is_available=True).distinct()
print(f"Offerings with available variations: {available_variations.count()}")

# Combine filters as in the view
combined_filter = all_offerings.filter(
    Q(variations__start_date__gte=now) | Q(variations__start_date__isnull=True)
).distinct().annotate(
    earliest_date=Min('variations__start_date')
).order_by('earliest_date', 'title')
print(f"Combined filter result: {combined_filter.count()}")

# Let's check a specific offering's variations
if all_offerings.exists():
    offering = all_offerings.first()
    print(f"\nChecking first offering: {offering.title}")
    print(f"Variations count: {offering.variations.count()}")
    for v in offering.variations.all():
        print(f"  - Start date: {v.start_date}, Available: {v.is_available}")
