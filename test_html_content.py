import os
import django
import sys

# Set up Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_site.settings')
django.setup()

from academies.models import Offering, Variation

# Create an offering with HTML content for testing
html_description = """
<div class="clearfix text-formatted field field--name-field-course-desc field--type-text-long field--label-hidden field__item">
<p>De studenten verwerven communicatieve vaardigheden in het Engels binnen een algemeen economische en bedrijfscontext.&nbsp;</p>

<h2>Inhoud</h2>

<p>1) Spreek- en luistervaardigheid: het geven en beluisteren van presentaties, kritische vragen stellen en beantwoorden, mondeling peer feedback geven; opbouwen van een informatieve&nbsp; of persuasieve presentatie; adequaat werken met visuele hulpmiddelen en multimedia.</p>

<p>2) Schrijfvaardigheid: schrijven van een zakelijke e-mail, een executive summary of kort&nbsp; rapport; schrijven van een sollicitatiebrief.</p>

<p>3) Leesvaardigheid en woordenschatuitbreiding: het lezen en bespreken van teksten van&nbsp; economische aard uit gespecialiseerde tijdschriften (bv The Economist); het zelfstandig&nbsp; verzamelen, lezen, analyseren en samenvatten van een aantal gespecialiseerde teksten rond een (bedrijfs)economisch thema ter voorbereiding van de eigen presentatie en 'executive summary' of kort rapport.</p>

<p>4) Taalverbetering: remediërende uitspraak-, woordenschat- en grammaticaoefeningen&nbsp; gebaseerd op frequent gemaakte fouten; woordenschatuitbreiding met aandacht voor ESP,&nbsp; collocaties en 'false friends'.</p>

<h2>Begincompetenties</h2>

<p>Studenten moeten deelnemen aan een toelatingsproef, via een schrijftest en een kort interview in week 1.</p>

<h2>Leerresultaten</h2>

<p>1) Be able to listen critically to presentations within the domain of economics and business&nbsp; administration.</p>

<p>2) Be able to give an informative/persuasive presentation on a topic related to (business)&nbsp; economics in fluent and correct English.</p>

<p>3) Be able to read and interpret specialised (business) economic texts.</p>

<p>4) Be able to write an executive summary or short report in good English.</p>

<p>5) Be able to write an adequate letter of application in good English.</p>

<p>6) Be able to write a formal email.</p>
</div>
"""

# Create a test offering with HTML content
offering = Offering.objects.filter(title='HTML Test Offering').first()
if not offering:
    from academies.models import Academy
    
    # Get the first academy or create one if none exists
    academy = Academy.objects.first()
    if not academy:
        academy = Academy.objects.create(name='Test Academy')
    
    # Create a test offering with HTML content
    offering = Offering.objects.create(
        title='HTML Test Offering',
        url='http://example.com/test-offering',
        academy=academy,
        description=html_description,
        is_active=True
    )
    print(f"Created test offering with ID {offering.id}")
else:
    # Update existing offering with HTML content
    offering.description = html_description
    offering.save()
    print(f"Updated test offering with ID {offering.id}")

print("HTML content has been added to the database, you can now check it in the web UI.")
print("Visit: http://localhost:8000/offerings/{}/".format(offering.id))
