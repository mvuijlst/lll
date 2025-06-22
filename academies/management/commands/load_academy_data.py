import json
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from academies.models import (
    Academy, Category, Language, Location, Teacher, 
    Offering, Variation, VariationTeacher, Link
)


class Command(BaseCommand):
    help = 'Load academy and offering data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the JSON file containing academy data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Link.objects.all().delete()
            VariationTeacher.objects.all().delete()
            Variation.objects.all().delete()
            Offering.objects.all().delete()
            Category.objects.all().delete()
            Teacher.objects.all().delete()
            Location.objects.all().delete()
            Language.objects.all().delete()
            Academy.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared'))

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON: {e}'))
            return

        # Load academies
        self.stdout.write('Loading academies...')
        academy_objects = {}
        for academy_data in data.get('academies', []):
            academy, created = Academy.objects.get_or_create(
                name=academy_data['name'],
                defaults={
                    'base_url': academy_data.get('base_url', ''),
                    'program_url': academy_data.get('program_url', ''),
                }
            )
            academy_objects[academy.name] = academy
            
            # Create categories for this academy
            for category_name in academy_data.get('categories', []):
                if category_name.strip():
                    Category.objects.get_or_create(
                        name=category_name,
                        academy=academy
                    )
            
            if created:
                self.stdout.write(f'  Created academy: {academy.name}')

        # Load offerings
        self.stdout.write('Loading offerings...')
        for offering_data in data.get('offerings', []):
            if not offering_data.get('url') or not offering_data.get('title'):
                continue
                
            academy_name = offering_data.get('academy')
            if academy_name not in academy_objects:
                self.stdout.write(f'  Skipping offering: Academy "{academy_name}" not found')
                continue
                
            academy = academy_objects[academy_name]
            
            # Get or create language
            language = None
            if offering_data.get('fields', {}).get('field-course-language'):
                language, _ = Language.objects.get_or_create(
                    name=offering_data['fields']['field-course-language']
                )
            
            # Get category
            category = None
            category_data = offering_data.get('fields', {}).get('field-course-category')
            if isinstance(category_data, dict) and category_data.get('text'):
                try:
                    category = Category.objects.get(
                        name=category_data['text'],
                        academy=academy
                    )
                except Category.DoesNotExist:
                    pass
            
            # Create offering
            offering, created = Offering.objects.get_or_create(
                url=offering_data['url'],
                defaults={
                    'title': offering_data['title'],
                    'academy': academy,
                    'category': category,
                    'language': language,
                    'course_id': offering_data.get('fields', {}).get('field-course-id', ''),
                    'description': offering_data.get('fields', {}).get('field-course-desc', ''),
                    'program_content': offering_data.get('fields', {}).get('field-course-program', ''),
                    'remarks': offering_data.get('fields', {}).get('field-course-remarks', ''),
                    'image_url': offering_data.get('fields', {}).get('field-course-img', ''),
                    'thumbnail_url': offering_data.get('fields', {}).get('thumbnail', ''),
                }
            )
            
            if created:
                self.stdout.write(f'  Created offering: {offering.title[:50]}...')
            
            # Process variations if they exist
            variations_data = offering_data.get('fields', {}).get('variations')
            if variations_data:
                self.process_variation(offering, variations_data)
                
        self.stdout.write(self.style.SUCCESS('Data loading completed'))

    def process_variation(self, offering, variation_data):
        """Process a single variation of an offering."""
        # Get or create location
        location = None
        location_data = variation_data.get('field-location-ref') or variation_data.get('location')
        if isinstance(location_data, dict) and location_data.get('text'):
            location, _ = Location.objects.get_or_create(
                name=location_data['text'],
                defaults={'url': location_data.get('url', '')}
            )
        elif isinstance(location_data, str) and location_data.strip():
            location, _ = Location.objects.get_or_create(
                name=location_data
            )
        
        # Parse dates
        start_date, end_date = self.parse_lesson_dates(
            variation_data.get('field-lesson-dates') or variation_data.get('lesson_dates', '')
        )
        
        # Create variation
        variation = Variation.objects.create(
            offering=offering,
            title=variation_data.get('title', ''),
            price=variation_data.get('price', ''),
            lesson_dates=variation_data.get('field-lesson-dates') or variation_data.get('lesson_dates', ''),
            start_date=start_date,
            end_date=end_date,
            location=location,
            description=self.extract_description_text(variation_data.get('field-description')),
            registration_url=self.extract_registration_url(variation_data.get('field-description'))
        )
        
        # Process teachers
        teachers_data = variation_data.get('field-teachers') or variation_data.get('teachers')
        if teachers_data and isinstance(teachers_data, dict):
            self.process_teachers(variation, teachers_data)

    def process_teachers(self, variation, teachers_data):
        """Process teachers for a variation."""
        links = teachers_data.get('links', [])
        for link in links:
            if link.get('text') and link.get('url'):
                teacher, _ = Teacher.objects.get_or_create(
                    name=link['text'],
                    defaults={'profile_url': link['url']}
                )
                VariationTeacher.objects.get_or_create(
                    variation=variation,
                    teacher=teacher
                )

    def parse_lesson_dates(self, date_string):
        """Parse lesson dates from various formats."""
        if not date_string:
            return None, None
            
        # Try to extract dates using regex
        date_pattern = r'(\d{1,2}/\d{1,2}/\d{4})'
        dates = re.findall(date_pattern, date_string)
        
        start_date = None
        end_date = None
        
        if dates:
            try:
                start_date = datetime.strptime(dates[0], '%d/%m/%Y')
                start_date = timezone.make_aware(start_date)
                if len(dates) > 1:
                    end_date = datetime.strptime(dates[-1], '%d/%m/%Y')
                    end_date = timezone.make_aware(end_date)
            except ValueError:
                pass
                
        return start_date, end_date

    def extract_description_text(self, description_data):
        """Extract description text from field data."""
        if isinstance(description_data, dict):
            return description_data.get('text', '')
        elif isinstance(description_data, str):
            return description_data
        return ''

    def extract_registration_url(self, description_data):
        """Extract registration URL from field data."""
        if isinstance(description_data, dict):
            links = description_data.get('links', [])
            for link in links:
                if 'registratie' in link.get('text', '').lower() or 'inschrijv' in link.get('text', '').lower():
                    return link.get('url', '')
        return ''
