import json
import re

with open('getdata/ugent_academies_data_detailed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

html_count = 0
total_count = len(data['offerings'])

for offering in data['offerings']:
    if re.search(r'<[^>]+>', offering.get('description', '')):
        html_count += 1
        print(f"Found HTML in: {offering['title'][:50]}")
        print(f"Sample: {offering['description'][:200]}")
        break

print(f"{html_count} offerings with HTML out of {total_count} total")
