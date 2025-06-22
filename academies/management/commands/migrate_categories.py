import json
from django.core.management.base import BaseCommand
from academies.models import Offering, Category
from django.db.models import Q

class Command(BaseCommand):
    help = 'Migrate existing category data to the new categories M2M relationship'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            help='Optional: Path to the detailed JSON file to import multiple categories'
        )

    def handle(self, *args, **options):
        json_file = options.get('json_file')
        
        # First, copy all existing single category relationships to the new M2M
        self.migrate_existing_categories()
        
        # If a JSON file is specified, use it to import multiple categories
        if json_file:
            self.import_from_json(json_file)
            
        self.stdout.write(self.style.SUCCESS('Category migration completed successfully'))
    
    def migrate_existing_categories(self):
        """Copy existing category data to the new categories relationship."""
        self.stdout.write('Migrating existing categories...')
        updated_count = 0
        
        # Get all offerings with a category
        offerings_with_category = Offering.objects.filter(
            category__isnull=False
        ).select_related('category')
        
        for offering in offerings_with_category:
            # Add the existing category to the M2M relationship if it's not already there
            if not offering.categories.filter(id=offering.category.id).exists():
                offering.categories.add(offering.category)
                updated_count += 1
                
        self.stdout.write(f'Updated {updated_count} offerings with existing categories')
    
    def import_from_json(self, json_file):
        """Import multiple categories from the JSON file."""
        self.stdout.write(f'Importing multiple categories from {json_file}...')
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON: {e}'))
            return
        
        # Process offerings in the JSON file
        updated_count = 0
        for item in data.get('offerings', []):
            if not item or 'link' not in item or 'categories' not in item or not item['categories']:
                continue
            
            # Find the offering by URL
            try:
                offering = Offering.objects.get(url=item['link'])
            except Offering.DoesNotExist:
                continue
            
            # Process each category
            for full_category_name in item['categories']:
                # Format in JSON is typically "Academy Name - Category Name"
                if ' - ' in full_category_name:
                    academy_name, category_name = full_category_name.split(' - ', 1)
                else:
                    category_name = full_category_name.strip()
                
                # Try to find the category
                matching_categories = Category.objects.filter(
                    Q(name__icontains=category_name) & 
                    Q(academy=offering.academy)
                )
                
                if matching_categories.exists():
                    category = matching_categories.first()
                    # Add to M2M if not already there
                    if not offering.categories.filter(id=category.id).exists():
                        offering.categories.add(category)
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"Added category '{category.name}' to offering '{offering.title}'"
                        ))
        
        self.stdout.write(f'Updated {updated_count} offerings with categories from JSON')
