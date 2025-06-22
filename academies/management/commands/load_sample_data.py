from django.core.management.base import BaseCommand
from academies.models import Academy, Offering


class Command(BaseCommand):
    help = 'Load sample data for academies and offerings'

    def handle(self, *args, **options):
        # Clear existing data
        Offering.objects.all().delete()
        Academy.objects.all().delete()

        # Create sample academies
        tech_academy = Academy.objects.create(
            name="Technology Academy",
            colour="#FF6B35"
        )

        business_academy = Academy.objects.create(
            name="Business Academy",
            colour="#004225"
        )

        arts_academy = Academy.objects.create(
            name="Arts Academy",
            colour="#7209B7"
        )

        health_academy = Academy.objects.create(
            name="Health Academy",
            colour="#0077BE"
        )

        # Create sample offerings for Technology Academy
        Offering.objects.create(
            name="Web Development Bootcamp",
            description="Learn modern web development with HTML, CSS, JavaScript, and popular frameworks like React and Vue.js.",
            academy=tech_academy
        )

        Offering.objects.create(
            name="Data Science Fundamentals",
            description="Master the basics of data science including Python, statistics, and machine learning algorithms.",
            academy=tech_academy
        )

        Offering.objects.create(
            name="Mobile App Development",
            description="Build native and cross-platform mobile applications for iOS and Android devices.",
            academy=tech_academy
        )

        # Create sample offerings for Business Academy
        Offering.objects.create(
            name="Digital Marketing Mastery",
            description="Learn comprehensive digital marketing strategies including SEO, social media, and content marketing.",
            academy=business_academy
        )

        Offering.objects.create(
            name="Entrepreneurship Essentials",
            description="Develop the skills needed to start and scale your own business from idea to execution.",
            academy=business_academy
        )

        Offering.objects.create(
            name="Financial Management",
            description="Master personal and business financial management, budgeting, and investment strategies.",
            academy=business_academy
        )

        # Create sample offerings for Arts Academy
        Offering.objects.create(
            name="Digital Art & Design",
            description="Create stunning digital artwork using industry-standard tools like Photoshop, Illustrator, and Figma.",
            academy=arts_academy
        )

        Offering.objects.create(
            name="Music Production",
            description="Learn music production, recording, mixing, and mastering using professional software and equipment.",
            academy=arts_academy
        )

        Offering.objects.create(
            name="Creative Writing Workshop",
            description="Develop your writing skills for fiction, non-fiction, screenwriting, and digital content creation.",
            academy=arts_academy
        )

        # Create sample offerings for Health Academy
        Offering.objects.create(
            name="Nutrition & Wellness",
            description="Understand the science of nutrition and learn to create healthy lifestyle habits for optimal well-being.",
            academy=health_academy
        )

        Offering.objects.create(
            name="Fitness Training Certification",
            description="Become a certified personal trainer with comprehensive knowledge of exercise science and training methods.",
            academy=health_academy
        )

        Offering.objects.create(
            name="Mental Health First Aid",
            description="Learn to recognize and respond to mental health challenges in yourself and others.",
            academy=health_academy
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {Academy.objects.count()} academies and {Offering.objects.count()} offerings'
            )
        )
