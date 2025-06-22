import json
import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from academies.models import (
    Academy, Category, Language, Offering, Link
)


class Command(BaseCommand):
    help = 'Import academy and offering data from the detailed JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the detailed JSON file containing academy data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        clear_data = options['clear']
        
        if clear_data:
            self.stdout.write('Clearing existing data...')
            # Delete related data first to avoid integrity errors
            Link.objects.all().delete()
            Offering.objects.all().delete()
            Category.objects.all().delete()
            Language.objects.all().delete()
            Academy.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared successfully'))

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON: {e}'))
            return

        # Import academies
        self.import_academies(data['academies'])
        
        # Import categories
        self.import_categories(data['categories'])
        
        # Import offerings
        self.import_offerings(data['offerings'])
        
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))

    def import_academies(self, academies_data):
        """Import academies from the JSON data."""
        self.stdout.write('Importing academies...')
        created_count = 0
        updated_count = 0
        
        for item in academies_data:
            academy, created = Academy.objects.update_or_create(
                name=item['name'],
                defaults={
                    'base_url': item['url'],
                    'program_url': item.get('program_url', ''),
                    'colour': item.get('colour', ''),
                    'sort_order': item.get('sort_order', 0),                    'logo': item.get('logo', '')
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(f'Created {created_count} academies, updated {updated_count} academies')
        
    def import_categories(self, categories_data):
        """Import categories from the JSON data."""
        self.stdout.write('Importing categories...')
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # Create a mapping for academy name variations
        academy_name_mapping = {
            'Gandaius Academy': 'Gandaius Permanente Vorming',
            'Beta Academy': 'Science Academy',
            'Ghall': 'The GHALL',
            'ACVetMed': 'Academie voor Diergeneeskunde',
            'ALLPHA': 'Academy for Lifelong Learning in Pharmacy',
            'APSS': 'Academy for Political and Social Sciences',
        }
        
        for item in categories_data:
            academy_name = item['academy']
            
            # Map academy name if a known variation exists
            if academy_name in academy_name_mapping:
                academy_name = academy_name_mapping[academy_name]
            
            try:
                # First try to find the academy by exact name
                academy = Academy.objects.get(name=academy_name)
            except Academy.DoesNotExist:
                # If exact match fails, try a case-insensitive search with partial match
                academies = Academy.objects.filter(name__icontains=academy_name)
                if academies.exists():
                    academy = academies.first()
                else:
                    self.stdout.write(self.style.WARNING(f"Academy not found for category: {item['name']} (Academy: {academy_name})"))
                    skipped_count += 1
                    continue
            
            category, created = Category.objects.update_or_create(
                name=item['name'],
                academy=academy,                defaults={}
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(f'Created {created_count} categories, updated {updated_count} categories, skipped {skipped_count} categories')
        
    def import_offerings(self, offerings_data):
        """Import offerings from the JSON data."""
        self.stdout.write('Importing offerings...')
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # Create a mapping for academy name variations
        academy_name_mapping = {
            'Gandaius Academy': 'Gandaius Permanente Vorming',
            'Beta Academy': 'Science Academy',
            'Ghall': 'The GHALL',
            'ACVetMed': 'Academie voor Diergeneeskunde',
            'ALLPHA': 'Academy for Lifelong Learning in Pharmacy',
            'APSS': 'Academy for Political and Social Sciences',
        }
        
        # Process each offering
        for item in offerings_data:
            if not item or 'title' not in item or 'academy' not in item:
                skipped_count += 1
                continue
                
            academy_name = item['academy']
            
            # Map academy name if a known variation exists
            if academy_name in academy_name_mapping:
                academy_name = academy_name_mapping[academy_name]
                
            try:
                # First try to find the academy by exact name
                academy = Academy.objects.get(name=academy_name)
            except Academy.DoesNotExist:
                # If exact match fails, try a case-insensitive search with partial match
                academies = Academy.objects.filter(name__icontains=academy_name)
                if academies.exists():
                    academy = academies.first()
                else:
                    self.stdout.write(self.style.WARNING(f"Academy not found for offering: {item['title']} (Academy: {academy_name})"))
                    skipped_count += 1
                    continue
            
            # Process language
            language = None
            if 'language' in item and item['language']:
                language_names = item['language'].split('\n')
                for lang_name in language_names:
                    lang_name = lang_name.strip()
                    if lang_name:
                        language, _ = Language.objects.get_or_create(name=lang_name)
                        break  # Just use the first language for now
            
            # Find or create the offering
            defaults = {
                'title': item['title'],
                'academy': academy,
                'description': item.get('description', ''),
                'program_content': item.get('program', ''),
                'course_id': item.get('course_id', ''),
                'language': language,
                'is_active': True
            }
            
            offering, created = Offering.objects.update_or_create(
                url=item['link'],
                defaults=defaults
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1            # Create categories for this offering if they exist
            if 'categories' in item and item['categories']:
                for full_category_name in item['categories']:
                    # Format in JSON is typically "Academy Name - Category Name"
                    # Try to extract just the category name
                    if ' - ' in full_category_name:
                        category_name = full_category_name.split(' - ')[1].strip()
                    else:
                        category_name = full_category_name.strip()
                        
                    # Try to find the category by name for this academy
                    matching_categories = Category.objects.filter(
                        name__icontains=category_name, 
                        academy=academy
                    )
                    
                    if matching_categories.exists():
                        # Use the first matching category
                        category = matching_categories.first()
                        # Add to the new many-to-many relationship
                        offering.categories.add(category)
                        # Also set the old single category field for the first category only
                        if offering.category is None:
                            offering.category = category
                            offering.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"Added category '{category.name}' to offering '{offering.title}'"
                        ))
                    else:
                        # If category doesn't exist yet, create it
                        category = Category.objects.create(
                            name=category_name,
                            academy=academy
                        )
                        # Add to the new many-to-many relationship
                        offering.categories.add(category)
                        # Also set the old single category field for the first category only
                        if offering.category is None:
                            offering.category = category
                            offering.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"Created and added category '{category.name}' to offering '{offering.title}'"
                        ))
                        
                        
        self.stdout.write(f'Created {created_count} offerings, updated {updated_count} offerings, skipped {skipped_count} offerings')
