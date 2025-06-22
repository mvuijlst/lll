from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from academies.models import Academy
import requests
import os
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Download and convert academy logos from URLs to uploaded files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--academy-name',
            type=str,
            help='Name of specific academy to process (optional)',
        )

    def handle(self, *args, **options):
        academies = Academy.objects.all()
        
        if options['academy_name']:
            academies = academies.filter(name__icontains=options['academy_name'])

        processed_count = 0
        
        # Sample logos that could be added manually
        sample_logos = {
            'Academie voor Diergeneeskunde': 'https://www.ugent.be/favicon.ico',
            'Science Academy': 'https://www.ugent.be/favicon.ico',
            # Add more as needed
        }

        for academy in academies:
            # Skip if already has a logo
            if academy.logo:
                self.stdout.write(f'{academy.name} already has a logo uploaded')
                continue
            
            # Check if we have a sample logo URL for this academy
            logo_url = sample_logos.get(academy.name)
            if not logo_url:
                self.stdout.write(f'No logo URL configured for {academy.name}')
                continue
            
            try:
                # Download the image
                response = requests.get(logo_url, timeout=10)
                response.raise_for_status()
                
                # Get the file extension from the URL
                parsed_url = urlparse(logo_url)
                file_name = os.path.basename(parsed_url.path)
                if not file_name or '.' not in file_name:
                    file_name = f'{academy.name.lower().replace(" ", "_")}.png'
                
                # Save the image to the academy
                academy.logo.save(
                    file_name,
                    ContentFile(response.content),
                    save=True
                )
                
                processed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Downloaded and saved logo for {academy.name}')
                )
                
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to download logo for {academy.name}: {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {academy.name}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Processed {processed_count} academy logos')
        )
        
        if processed_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    'No logos were downloaded. You can now upload logos manually '
                    'through the Django admin interface at /admin/academies/academy/'
                )
            )
