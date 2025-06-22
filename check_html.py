from academies.models import Offering
import re

html_count = 0
total_count = Offering.objects.count()

for o in Offering.objects.all():
    if re.search(r'<[^>]+>', o.description):
        html_count += 1
        print(f"Found HTML in: {o.title[:50]}")
        print(f"Sample: {o.description[:200]}")
        break

print(f"{html_count} offerings with HTML out of {total_count} total")
