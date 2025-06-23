import json
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from academies.models import (
    Academy, Category, Language, Location, Teacher, 
    Offering, Variation, VariationTeacher, Link
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
            VariationTeacher.objects.all().delete()
            Variation.objects.all().delete()
            Offering.objects.all().delete()
            Category.objects.all().delete()
            Language.objects.all().delete()
            Location.objects.all().delete()
            Teacher.objects.all().delete()
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
            return        # Import academies
        self.import_academies(data['academies'])
        
        # Import categories
        self.import_categories(data['categories'])
        
        # Import teachers
        self.import_teachers(data.get('teachers', []))
        
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
                    'sort_order': item.get('sort_order', 0),
                    'introduction': item.get('introduction', ''),
                    'logo': item.get('logo', '')
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
            except Academy.DoesNotExist:                # If exact match fails, try a case-insensitive search with partial match
                academies = Academy.objects.filter(name__icontains=academy_name)
                if academies.exists():
                    academy = academies.first()
                else:
                    self.stdout.write(self.style.WARNING(f"Academy not found for category: {item['name']} (Academy: {academy_name})"))
                    skipped_count += 1
                    continue
            
            category, created = Category.objects.update_or_create(
                name=item['name'],
                academy=academy,
                defaults={}
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(f'Created {created_count} categories, updated {updated_count} categories, skipped {skipped_count} categories')
        
    def import_teachers(self, teachers_data):
        """Import teachers from the JSON data."""
        self.stdout.write('Importing teachers...')
        created_count = 0
        updated_count = 0
        
        for teacher_data in teachers_data:
            teacher_name = teacher_data.get('name', '').strip()
            if not teacher_name:
                continue
                
            teacher, created = Teacher.objects.update_or_create(
                name=teacher_name,
                defaults={
                    'profile_url': teacher_data.get('link', ''),
                    'photo_url': teacher_data.get('photo_url', ''),
                    'description': teacher_data.get('description', ''),
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(f'Created {created_count} teachers, updated {updated_count} teachers')
        
    def import_offerings(self, offerings_data):
        """Import offerings from the JSON data."""
        self.stdout.write('Importing offerings...')
        created_count = 0
        updated_count = 0
        skipped_count = 0
        variation_count = 0
        
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
                'description': item.get('description', ''),  # Preserve HTML content
                'program_content': item.get('program', ''),  # Preserve HTML content
                'remarks': item.get('remarks', ''),  # Preserve HTML content
                'course_id': item.get('course_id', ''),
                'language': language,
                'image_url': item.get('image_url', ''),
                'is_active': True
            }
            
            offering, created = Offering.objects.update_or_create(
                url=item['link'],
                defaults=defaults
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
            # Create categories for this offering if they exist
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

            # Process variations for this offering
            if 'variations' in item and item['variations']:
                variation_count += self.import_variations(offering, item['variations'])
                        
        self.stdout.write(f'Created {created_count} offerings, updated {updated_count} offerings, skipped {skipped_count} offerings')
        self.stdout.write(f'Created {variation_count} variations')

    def import_variations(self, offering, variations_data):
        """Import variations for an offering."""
        count = 0
        
        # Clear existing variations for this offering to avoid duplicates
        Variation.objects.filter(offering=offering).delete()
        
        for variation_data in variations_data:
            # Process location
            location = None
            if 'location' in variation_data and variation_data['location'] and 'name' in variation_data['location']:
                location_name = variation_data['location']['name']
                location_url = variation_data['location'].get('link', '')
                location, _ = Location.objects.get_or_create(
                    name=location_name,
                    defaults={'url': location_url}
                )
            
            # Process dates
            lesson_dates = ''
            start_date = None
            end_date = None
            
            if 'dates' in variation_data and variation_data['dates']:
                # Join all dates into a single string
                lesson_dates = ', '.join(variation_data['dates'])
                
                # Try to parse the first date range
                for date_str in variation_data['dates']:
                    # Common format: "16/09/2025 - 09:00 – 30/06/2026 - 16:00"
                    date_pattern = r'(\d{1,2}/\d{1,2}/\d{4})'
                    dates = re.findall(date_pattern, date_str)
                    
                    if dates:
                        try:
                            # Parse the start date (first date found)
                            start_date = datetime.strptime(dates[0], '%d/%m/%Y')
                            start_date = timezone.make_aware(start_date)
                            
                            # Parse the end date if available (last date found)
                            if len(dates) > 1:
                                end_date = datetime.strptime(dates[-1], '%d/%m/%Y')
                                end_date = timezone.make_aware(end_date)
                            break  # Successfully parsed a date, no need to try other strings
                        except ValueError:
                            # If parsing fails, continue with the next date string
                            continue
              # Create the variation
            variation = Variation.objects.create(
                offering=offering,
                title=variation_data.get('title', ''),
                price=variation_data.get('price', ''),
                lesson_dates=lesson_dates,
                start_date=start_date,
                end_date=end_date,
                location=location,
                description=variation_data.get('description', ''),  # Preserve HTML content
                is_available=True
            )
            count += 1
            
            # Process teachers
            if 'teachers' in variation_data and variation_data['teachers']:
                for teacher_data in variation_data['teachers']:
                    if 'name' in teacher_data:
                        teacher_name = teacher_data['name']
                        teacher_url = teacher_data.get('link', '')
                        
                        teacher, _ = Teacher.objects.get_or_create(
                            name=teacher_name,
                            defaults={'profile_url': teacher_url}
                        )
                        
                        # Create the teacher-variation relationship
                        VariationTeacher.objects.create(
                            variation=variation,
                            teacher=teacher
                        )
            
            # Add registration URL if available
            if 'registration_url' in variation_data and variation_data['registration_url']:
                variation.registration_url = variation_data['registration_url']
                variation.save()
        
        return count
