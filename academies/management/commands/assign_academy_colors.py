from django.core.management.base import BaseCommand
from academies.models import Academy


class Command(BaseCommand):
    help = 'Assign colors to academies'

    def handle(self, *args, **options):
        # Define a professional color palette for UGent academies
        colors = [
            '#1e3a8a',  # Deep blue (UGent primary)
            '#dc2626',  # Red
            '#059669',  # Green  
            '#d97706',  # Orange
            '#7c3aed',  # Purple
            '#db2777',  # Pink
            '#0891b2',  # Cyan
            '#65a30d',  # Lime
            '#e11d48',  # Rose
            '#8b5cf6',  # Violet
        ]
        
        academies = Academy.objects.filter(colour__in=['', None]).order_by('name')
        
        for i, academy in enumerate(academies):
            color = colors[i % len(colors)]
            academy.colour = color
            academy.save()
            self.stdout.write(
                self.style.SUCCESS(f'Assigned color {color} to {academy.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned colors to {academies.count()} academies')
        )
