from django.core.management.base import BaseCommand
from academies.models import Academy, Offering, Category


class Command(BaseCommand):
    help = 'Move UGain offerings from Science Academy to UGain Academy'

    def handle(self, *args, **options):
        # Get the academies
        try:
            science_academy = Academy.objects.get(name="Science Academy")
            ugain_academy = Academy.objects.get(name="UGain - UGent Academie voor Ingenieurs")
        except Academy.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Academy not found: {e}'))
            return        # Find the UGain category in Science Academy
        ugain_category_name = "Opleidingen UGain (UGent Academie voor Ingenieurs)"
        
        try:
            ugain_category = Category.objects.get(
                name=ugain_category_name,
                academy=science_academy
            )
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'UGain category not found in Science Academy'))
            return

        # Find all offerings in this category
        ugain_offerings = Offering.objects.filter(
            academy=science_academy,
            categories=ugain_category
        )

        moved_count = 0
        
        for offering in ugain_offerings:
            # Remove the offering from the UGain category in Science Academy
            offering.categories.remove(ugain_category)
            
            # Move the offering to UGain Academy
            offering.academy = ugain_academy
            offering.save()
            
            # Create or get a general category for UGain
            ugain_general_category, created = Category.objects.get_or_create(
                name="All Offerings",
                academy=ugain_academy
            )
            
            # Add the offering to the UGain general category
            offering.categories.add(ugain_general_category)
            
            moved_count += 1
            
            self.stdout.write(f'Moved: {offering.title}')

        # If the UGain category in Science Academy is now empty, we can delete it
        if ugain_category.offerings.count() == 0:
            ugain_category.delete()
            self.stdout.write(f'Deleted empty category: {ugain_category_name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully moved {moved_count} offerings from Science Academy to UGain Academy')
        )
