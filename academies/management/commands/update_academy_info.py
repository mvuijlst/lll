from django.core.management.base import BaseCommand
from academies.models import Academy


class Command(BaseCommand):
    help = 'Update academy information with descriptions and sort orders'

    def handle(self, *args, **options):
        academy_data = {            'Academie voor Diergeneeskunde': {
                'description': 'Specialized veterinary education and professional development for animal health experts.',
                'sort_order': 1,
            },
            'Academy for Lifelong Learning in Pharmacy': {
                'description': 'Continuing education programs for pharmaceutical professionals and healthcare providers.',
                'sort_order': 2,
            },
            'Academy for Political and Social Sciences': {
                'description': 'Advanced courses in political science, sociology, and public administration.',
                'sort_order': 3,
            },
            'Dunant Academie': {
                'description': 'Healthcare and medical education programs honoring the humanitarian spirit.',
                'sort_order': 4,
            },
            'FEB Academy': {
                'description': 'Business and economics education for professionals and entrepreneurs.',
                'sort_order': 5,
            },
            'Gandaius Permanente Vorming': {
                'description': 'Continuous learning programs across various disciplines and professional fields.',
                'sort_order': 6,
            },
            'Humanities Academie': {
                'description': 'Literature, philosophy, history, and cultural studies for lifelong learners.',
                'sort_order': 7,
            },
            'Science Academy': {
                'description': 'Scientific research methods, innovation, and technology advancement programs.',
                'sort_order': 8,
            },
            'The GHALL': {
                'description': 'Ghent Academy for Lifelong Learning - interdisciplinary educational programs.',
                'sort_order': 9,
            },
            'UGain - UGent Academie voor Ingenieurs': {
                'description': 'Engineering and technical education for professional development and innovation.',
                'sort_order': 10,
            },
        }

        updated_count = 0
        for academy_name, data in academy_data.items():
            try:
                academy = Academy.objects.get(name=academy_name)
                updated = False
                
                if not academy.description and data.get('description'):
                    academy.description = data['description']
                    updated = True
                
                if academy.sort_order == 0 and data.get('sort_order'):
                    academy.sort_order = data['sort_order']
                    updated = True
                
                if updated:
                    academy.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated {academy.name}')
                    )
                else:
                    self.stdout.write(f'No updates needed for {academy.name}')
                    
            except Academy.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Academy "{academy_name}" not found')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} academies')
        )
