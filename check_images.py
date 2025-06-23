import json

# Load the scraped data
with open('getdata/ugent_academies_data_detailed.json', encoding='utf-8') as f:
    data = json.load(f)

# Find offerings with images
offerings_with_images = [o for o in data['offerings'] if o.get('image_url')]

print(f'Offerings with images: {len(offerings_with_images)}')
print(f'Total offerings: {len(data["offerings"])}')
print(f'Percentage with images: {len(offerings_with_images)/len(data["offerings"])*100:.1f}%')

print('\nSample offerings with images:')
for i, offering in enumerate(offerings_with_images[:5]):
    print(f'{i+1}. {offering["title"][:60]}...')
    print(f'   Image: {offering["image_url"]}')
    print(f'   Academy: {offering["academy"]}')
    print()
