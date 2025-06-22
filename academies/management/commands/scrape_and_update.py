import json
import os
import sys
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from academies.models import (
    Academy, Category, Language, Location, Teacher, 
    Offering, Variation, VariationTeacher, Link
)


class Command(BaseCommand):
    help = 'Scrape academy data and update database while preserving academy customizations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scrape-only',
            action='store_true',
            help='Only run the scraping, do not import data'
        )
        parser.add_argument(
            '--import-only',
            action='store_true',
            help='Only import data from existing JSON file, do not scrape'
        )
        parser.add_argument(
            '--json-file',
            type=str,
            help='Path to JSON file (for import-only mode)',
            default=None
        )

    def handle(self, *args, **options):
        scrape_only = options['scrape_only']
        import_only = options['import_only']
        json_file = options['json_file']

        if scrape_only and import_only:
            self.stdout.write(self.style.ERROR('Cannot use both --scrape-only and --import-only'))
            return

        # Step 1: Export current academy metadata
        self.stdout.write('Exporting current academy metadata...')
        academy_metadata = self.export_academy_metadata()
        
        # Step 2: Run scraping (unless import-only mode)
        if not import_only:
            self.stdout.write('Running scraper...')
            json_file = self.run_scraper()
            if not json_file:
                self.stdout.write(self.style.ERROR('Scraping failed'))
                return
        elif not json_file:
            # Look for the default scraper output file
            json_file = os.path.join('getdata', 'ugent_academies_complete.json')
            if not os.path.exists(json_file):
                self.stdout.write(self.style.ERROR('No JSON file specified and default file not found'))
                return

        if scrape_only:
            self.stdout.write(self.style.SUCCESS(f'Scraping completed. Data saved to: {json_file}'))
            return

        # Step 3: Import data while preserving academy customizations
        self.stdout.write('Importing data while preserving academy customizations...')
        self.import_data_preserving_academies(json_file, academy_metadata)
        
        self.stdout.write(self.style.SUCCESS('Scrape and import completed successfully!'))

    def export_academy_metadata(self):
        """Export current academy metadata to preserve customizations."""
        # Hardcoded academy metadata - ensures customizations are preserved even if database is empty
        hardcoded_metadata = {
            "Humanities Academie": {
                'base_url': 'https://humanitiesacademie.ugent.be',
                'program_url': 'https://humanitiesacademie.ugent.be/programma',
                'colour': '#F1A42B',
                'sort_order': 1,
                'description': '',
                'logo': 'academy_logos/humanities.png',
            },
            "Gandaius Permanente Vorming": {
                'base_url': 'https://gandaiusacademy.ugent.be',
                'program_url': 'https://gandaiusacademy.ugent.be/programma',
                'colour': '#DC4E28',
                'sort_order': 2,
                'description': '',
                'logo': 'academy_logos/gandaius.png',
            },
            "Science Academy": {
                'base_url': 'https://beta-academy.ugent.be',
                'program_url': 'https://beta-academy.ugent.be/programma',
                'colour': '#2D8CA8',
                'sort_order': 3,
                'description': '',
                'logo': 'academy_logos/science.png',
            },
            "The GHALL": {
                'base_url': 'https://ghall.ugent.be',
                'program_url': 'https://ghall.ugent.be/programma',
                'colour': '#E85E71',
                'sort_order': 4,
                'description': '',
                'logo': 'academy_logos/ghall.png',
            },
            "UGain - UGent Academie voor Ingenieurs": {
                'base_url': 'https://ugain.ugent.be',
                'program_url': 'https://ugain.ugent.be/programma',
                'colour': '#1E64C8',
                'sort_order': 5,
                'description': '',
                'logo': 'academy_logos/ugain.png',
            },
            "FEB Academy": {
                'base_url': 'https://febacademy.ugent.be',
                'program_url': 'https://febacademy.ugent.be/programma',
                'colour': '#AEB050',
                'sort_order': 6,
                'description': '',
                'logo': 'academy_logos/feb.png',
            },
            "Academie voor Diergeneeskunde": {
                'base_url': 'https://acvetmed.ugent.be',
                'program_url': 'https://acvetmed.ugent.be/programma',
                'colour': '#825491',
                'sort_order': 7,
                'description': '',
                'logo': 'academy_logos/acvetmed.png',
            },
            "Dunant Academie": {
                'base_url': 'https://dunantacademie.ugent.be',
                'program_url': 'https://dunantacademie.ugent.be/programma',
                'colour': '#FB7E3A',
                'sort_order': 8,
                'description': '',
                'logo': 'academy_logos/dunant.png',
            },
            "Academy for Lifelong Learning in Pharmacy": {
                'base_url': 'https://allpha.ugent.be',
                'program_url': 'https://allpha.ugent.be/programma',
                'colour': '#BE5190',
                'sort_order': 9,
                'description': '',
                'logo': 'academy_logos/pharma.png',
            },
            "Academy for Political and Social Sciences": {
                'base_url': 'https://apss.ugent.be',
                'program_url': 'https://apss.ugent.be/programma',
                'colour': '#71A860',
                'sort_order': 10,
                'description': '',
                'logo': 'academy_logos/apss.png',
            },
        }
        
        # Try to get current database metadata first
        academies = Academy.objects.all()
        metadata = {}
        
        for academy in academies:
            metadata[academy.name] = {
                'id': academy.id,
                'base_url': academy.base_url,
                'program_url': academy.program_url,
                'colour': academy.colour,
                'sort_order': academy.sort_order,
                'description': academy.description,
                'logo': academy.logo.name if academy.logo else None,
                'created_at': academy.created_at.isoformat() if academy.created_at else None,
            }
        
        # Merge with hardcoded defaults - database values take precedence
        for academy_name, defaults in hardcoded_metadata.items():
            if academy_name not in metadata:
                # Academy not in database, use hardcoded values
                metadata[academy_name] = defaults
                self.stdout.write(f'  Using hardcoded metadata for: {academy_name}')
            else:
                # Academy exists in database, merge missing values from hardcoded defaults
                current = metadata[academy_name]
                for key, default_value in defaults.items():
                    if not current.get(key) and default_value:
                        current[key] = default_value
        
        self.stdout.write(f'Exported metadata for {len(metadata)} academies (including hardcoded defaults)')
        return metadata

    def run_scraper(self):
        """Run the scraper script and return the output JSON file path."""
        # Get the absolute path to the scraper        # Get the absolute path to the scraper
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        scraper_path = os.path.join(base_dir, 'getdata', 'scrape.py')
        getdata_dir = os.path.join(base_dir, 'getdata')
        
        if not os.path.exists(scraper_path):
            self.stdout.write(self.style.ERROR(f'Scraper not found at: {scraper_path}'))
            return None
        
        self.stdout.write('[NET] Starting web scraping process...')
        self.stdout.write(f'   [DIR] Scraper location: {scraper_path}')
        self.stdout.write(f'   [TARGET] Target: All 10 UGent academies')
        self.stdout.write(f'   [TIME] This may take several minutes...')
        self.stdout.write('')  # Empty line for readability
        
        try:
            # Run the scraper with real-time output
            process = subprocess.Popen([
                sys.executable, scraper_path
            ], cwd=getdata_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
               text=True, bufsize=1, universal_newlines=True)
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                if line.strip():  # Only show non-empty lines
                    self.stdout.write(f'   {line.strip()}')
            
            process.wait()
            
            if process.returncode != 0:
                self.stdout.write(self.style.ERROR(f'Scraper failed with exit code {process.returncode}'))
                return None
            
            # Look for output file
            output_file = os.path.join(getdata_dir, 'ugent_academies_complete.json')
            if os.path.exists(output_file):
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('[OK] Scraping completed successfully!'))
                
                # Show file size info
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                self.stdout.write(f'[STATS] Output file: {output_file}')
                self.stdout.write(f'[STATS] File size: {file_size:.1f} MB')
                
                return output_file
            else:
                self.stdout.write(self.style.ERROR('Scraper completed but output file not found'))
                return None
                
        except subprocess.TimeoutExpired:
            self.stdout.write(self.style.ERROR('[TIME] Scraper timed out after 10 minutes'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running scraper: {e}'))
            return None

    def import_data_preserving_academies(self, json_file, academy_metadata):
        """Import data while preserving existing academy customizations."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON: {e}'))
            return

        with transaction.atomic():
            # Clear only the dynamic data, preserve academies
            self.stdout.write('Clearing dynamic data (preserving academies)...')
            Link.objects.all().delete()
            VariationTeacher.objects.all().delete()
            Variation.objects.all().delete()
            Offering.objects.all().delete()
            # Clear categories but we'll recreate them
            Category.objects.all().delete()
            # Clear teachers and locations - they'll be recreated
            Teacher.objects.all().delete()
            Location.objects.all().delete()
            # Clear languages - they'll be recreated
            Language.objects.all().delete()

            # Load academies (update existing, create new)
            self.stdout.write('Processing academies...')
            academy_objects = {}
            for academy_data in data.get('academies', []):
                academy_name = academy_data['name']
                
                # Check if we have existing metadata for this academy
                existing_metadata = academy_metadata.get(academy_name, {})
                
                academy, created = Academy.objects.update_or_create(
                    name=academy_name,
                    defaults={
                        'base_url': academy_data.get('base_url', ''),
                        'program_url': academy_data.get('program_url', ''),
                        # Preserve existing customizations if they exist
                        'colour': existing_metadata.get('colour', ''),
                        'sort_order': existing_metadata.get('sort_order', 0),
                        'description': existing_metadata.get('description', ''),
                        # Don't touch the logo field - it's a file field
                    }
                )
                
                # Restore logo if it existed (logo field is handled separately)
                if not created and existing_metadata.get('logo'):
                    # The logo file should still exist, Django handles this
                    pass
                
                academy_objects[academy.name] = academy
                
                # Create categories for this academy
                for category_name in academy_data.get('categories', []):
                    if category_name.strip():
                        Category.objects.get_or_create(
                            name=category_name,
                            academy=academy
                        )
                
                if created:
                    self.stdout.write(f'  Created new academy: {academy.name}')
                else:
                    self.stdout.write(f'  Updated academy: {academy.name} (preserved customizations)')

            # Load offerings (same as original load_academy_data command)
            self.stdout.write('Loading offerings...')
            offerings_created = 0
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
                    offerings_created += 1
                
                # Process variations if they exist
                variations_data = offering_data.get('fields', {}).get('variations')
                if variations_data:
                    self.process_variation(offering, variations_data)
            
            self.stdout.write(f'Created {offerings_created} offerings')
            self.stdout.write(self.style.SUCCESS('Data import completed'))

    def process_variation(self, offering, variation_data):
        """Process a single variation of an offering (copied from load_academy_data)."""
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
        """Process teachers for a variation (copied from load_academy_data)."""
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
        """Parse lesson dates from various formats (copied from load_academy_data)."""
        if not date_string:
            return None, None
            
        import re
        from django.utils import timezone
        
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
        """Extract description text from field data (copied from load_academy_data)."""
        if isinstance(description_data, dict):
            return description_data.get('text', '')
        elif isinstance(description_data, str):
            return description_data
        return ''

    def extract_registration_url(self, description_data):
        """Extract registration URL from field data (copied from load_academy_data)."""
        if isinstance(description_data, dict):
            links = description_data.get('links', [])
            for link in links:
                if 'registratie' in link.get('text', '').lower() or 'inschrijv' in link.get('text', '').lower():
                    return link.get('url', '')
        return ''
