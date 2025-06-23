import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
import os

def scrape_categories(academy_url, academy_name):
    """
    Scrape categories from an academy
    
    Args:
        academy_url: URL of the academy program page
        academy_name: Name of the academy for reference
        
    Returns:
        List of dictionaries containing category information
    """
    print(f"Scraping categories from {academy_name}...")
    
    # Send an HTTP request to the URL
    response = requests.get(academy_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: Status code {response.status_code}")
        return None
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the container with categories using the provided CSS selector
    container = soup.select_one("#block-system-main-block > div > div > div.view-content > div")
    
    if not container:
        print(f"Could not find the categories container on the page for {academy_name}")
        return None
    
    # List to store category data
    categories = []
    
    # Find all list items in the unordered list based on the actual HTML structure
    list_items = container.select('ul li')
    
    for item in list_items:
        # Find the link element inside views-field-name
        link_element = item.select_one('.views-field-name a')
        if link_element:
            name = link_element.get_text().strip()
            link = link_element['href']
            
            # Make the link absolute if it's relative
            if link.startswith('/'):
                # Determine the base URL based on the academy_url
                base_url = academy_url.split('/programma')[0]
                link = f"{base_url}{link}"
            
            categories.append({
                'name': name,
                'link': link,
                'academy': academy_name  # Add the academy name to distinguish categories
            })
    
    return categories

def scrape_offerings(category_url, category_name, academy_name):
    """
    Scrape offerings from a category page
    
    Args:
        category_url: URL of the category page
        category_name: Name of the category for reference
        academy_name: Name of the academy for reference
        
    Returns:
        List of dictionaries containing offering information
    """
    print(f"Scraping offerings for category: {category_name} ({academy_name})")
    
    # Send an HTTP request to the URL
    response = requests.get(category_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the category page: Status code {response.status_code}")
        return None
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the container with offerings using the provided CSS selector
    container = soup.select_one("#block-system-main-block > div")
    
    if not container:
        print(f"Could not find the offerings container on the page for {category_name}")
        return []
    
    # List to store offering data
    offerings = []
    
    # Find all article elements containing offerings
    article_elements = container.find_all('article')
    
    # Get the base URL from the category_url
    base_url = category_url.split('/programma')[0]
    
    for article in article_elements:
        # Find the link (the entire article is wrapped in an <a> tag)
        link_element = article.find('a')
        if link_element:
            link = link_element['href']
            
            # Make the link absolute if it's relative
            if link.startswith('/'):
                link = f"{base_url}{link}"
            
            # Get the title from the h4 element
            title_element = link_element.select_one('h4 .field--name-title')
            if title_element:
                title = title_element.get_text().strip()
                
                offerings.append({
                    'title': title,
                    'link': link,
                    'academy': academy_name  # Add the academy name to distinguish offerings
                })
    
    print(f"Found {len(offerings)} offerings in category: {category_name} ({academy_name})")
    return offerings

# Define academy metadata
academy_metadata = {
    "https://humanitiesacademie.ugent.be": {
        "name": "Humanities Academie",
        "sort_order": 1,
        "colour": "#F1A42B",
        "logo": "academy_logos/humanities.png",
        "program_url": "https://humanitiesacademie.ugent.be/programma"
    },
    "https://gandaiusacademy.ugent.be": {
        "name": "Gandaius Permanente Vorming",
        "sort_order": 2,
        "colour": "#DC4E28",
        "logo": "academy_logos/gandaius.png",
        "program_url": "https://gandaiusacademy.ugent.be/programma"
    },
    "https://beta-academy.ugent.be": {
        "name": "Science Academy",
        "sort_order": 3,
        "colour": "#2D8CA8",
        "logo": "academy_logos/science.png",
        "program_url": "https://beta-academy.ugent.be/programma"
    },
    "https://ghall.ugent.be": {
        "name": "The GHALL",
        "sort_order": 4,
        "colour": "#E85E71",
        "logo": "academy_logos/ghall.png",
        "program_url": "https://ghall.ugent.be/programma"
    },
    "https://ugain.ugent.be": {
        "name": "UGain - UGent Academie voor Ingenieurs",
        "sort_order": 5,
        "colour": "#1E64C8",
        "logo": "academy_logos/ugain.png",
        "program_url": "https://ugain.ugent.be/programma"
    },
    "https://febacademy.ugent.be": {
        "name": "FEB Academy",
        "sort_order": 6,
        "colour": "#AEB050",
        "logo": "academy_logos/feb.png",
        "program_url": "https://febacademy.ugent.be/programma"
    },
    "https://acvetmed.ugent.be": {
        "name": "Academie voor Diergeneeskunde",
        "sort_order": 7,
        "colour": "#825491",
        "logo": "academy_logos/acvetmed.png",
        "program_url": "https://acvetmed.ugent.be/programma"
    },
    "https://dunantacademie.ugent.be": {
        "name": "Dunant Academie",
        "sort_order": 8,
        "colour": "#FB7E3A",
        "logo": "academy_logos/dunant.png",
        "program_url": "https://dunantacademie.ugent.be/programma"
    },
    "https://allpha.ugent.be": {
        "name": "Academy for Lifelong Learning in Pharmacy",
        "sort_order": 9,
        "colour": "#BE5190",
        "logo": "academy_logos/pharma.png",
        "program_url": "https://allpha.ugent.be/programma"
    },
    "https://apss.ugent.be": {
        "name": "Academy for Political and Social Sciences",
        "sort_order": 10,
        "colour": "#71A860",
        "logo": "academy_logos/apss.png",
        "program_url": "https://apss.ugent.be/programma"
    }
}

def scrape_offering_details(offering_url, offering_title, academy_name):
    """
    Scrape detailed information from an offering page
    
    Args:
        offering_url: URL of the offering page
        offering_title: Title of the offering
        academy_name: Name of the academy
        
    Returns:
        Dictionary with detailed offering information
    """
    print(f"Scraping details for: {offering_title}")
    
    # Add a small delay to avoid overwhelming the server
    time.sleep(0.1)  # Reduced from 1 second to 0.1 seconds
    
    # Send an HTTP request to the URL
    try:
        response = requests.get(offering_url, timeout=30)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the offering page: Status code {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error accessing {offering_url}: {e}")
        return {}
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
      # Initialize the details dictionary with basic information
    details = {
        'title': offering_title,
        'link': offering_url,
        'academy': academy_name,
        'description': '',
        'program': '',
        'course_id': '',
        'language': '',
        'image_url': '',
        'partners': [],
        'related_courses': [],
        'variations': []
    }
    
    # Extract course ID if available
    course_id_element = soup.select_one('.course-number .field--name-field-course-id')
    if course_id_element:
        details['course_id'] = course_id_element.get_text().strip()
    
    # Extract language if available
    language_element = soup.select_one('.course-language .field--name-field-course-language')
    if language_element:
        details['language'] = language_element.get_text().strip()      # Extract description with HTML content preserved
    description_element = soup.select_one('.field--name-field-course-desc')
    if description_element:
        # Get the inner HTML content of the element (exclude the container tag)
        # First get all the inner HTML
        inner_html = ''.join(str(child) for child in description_element.children)
        details['description'] = inner_html
    
    # Extract program details with HTML content preserved
    program_element = soup.select_one('.field--name-field-course-program')
    if program_element:
        # Get the inner HTML content of the element (exclude the container tag)
        inner_html = ''.join(str(child) for child in program_element.children)
        details['program'] = inner_html
    
    # Extract partners
    partner_elements = soup.select('.field--name-field-course-partners .field__item')
    for partner in partner_elements:
        partner_link = partner.select_one('a')
        partner_img = partner.select_one('img')
        if partner_link and partner_img:
            details['partners'].append({
                'name': partner_img.get('alt', ''),
                'link': partner_link.get('href', '')
            })
    
    # Extract related courses
    related_course_elements = soup.select('.field--name-field-course-related-courses .field__item a')
    for related in related_course_elements:
        link = related.get('href', '')
        if link.startswith('/'):
            base_url = offering_url.split('/', 3)[0] + '//' + offering_url.split('/', 3)[2]
            link = base_url + link
        
        details['related_courses'].append({
            'title': related.get_text().strip(),
            'link': link
        })
    
    # Extract variations/lessons
    variation_elements = soup.select('.field--name-variations .field__item')
    for variation in variation_elements:
        variation_data = {
            'title': '',
            'description': '',
            'price': '',
            'dates': [],
            'location': '',
            'teachers': []
        }
        
        # Extract variation title
        title_element = variation.select_one('.field--name-title')
        if title_element:
            variation_data['title'] = title_element.get_text().strip()          # Extract variation description with HTML content preserved
        desc_element = variation.select_one('.field--name-field-description')
        if desc_element:
            # Get the inner HTML content of the element (exclude the container tag)
            inner_html = ''.join(str(child) for child in desc_element.children)
            variation_data['description'] = inner_html
        
        # Extract variation price
        price_element = variation.select_one('.field--name-price .field__item')
        if price_element:
            variation_data['price'] = price_element.get_text().strip()
        
        # Extract variation dates
        date_elements = variation.select('.field--name-field-lesson-dates .field__item')
        for date_element in date_elements:
            variation_data['dates'].append(date_element.get_text().strip())
        
        # Extract variation location
        location_element = variation.select_one('.field--name-field-location-ref a')
        if location_element:
            location_text = location_element.get_text().strip()
            location_link = location_element.get('href', '')
            if location_link.startswith('/'):
                base_url = offering_url.split('/', 3)[0] + '//' + offering_url.split('/', 3)[2]
                location_link = base_url + location_link
            
            variation_data['location'] = {
                'name': location_text,
                'link': location_link
            }
        
        # Extract variation teachers
        teacher_elements = variation.select('.field--name-field-teachers .field__item a')
        for teacher in teacher_elements:
            teacher_name = teacher.get_text().strip()
            teacher_link = teacher.get('href', '')
            if teacher_link.startswith('/'):
                base_url = offering_url.split('/', 3)[0] + '//' + offering_url.split('/', 3)[2]
                teacher_link = base_url + teacher_link
            
            variation_data['teachers'].append({
                'name': teacher_name,
                'link': teacher_link
            })
        
        # Add this variation to the list
        if variation_data['title']:
            details['variations'].append(variation_data)
    
    # Extract offering image if available
    image_element = soup.select_one('#block-system-main-block > article > div.course--content > section.sidebar--second > div > article > div > picture > img')
    if image_element:
        image_src = image_element.get('src', '')
        if image_src:
            # Make the image URL absolute if it's relative
            if image_src.startswith('/'):
                base_url = offering_url.split('/', 3)[0] + '//' + offering_url.split('/', 3)[2]
                image_src = base_url + image_src
            details['image_url'] = image_src
    
    return details

def scrape_academy_introduction(academy_base_url, academy_name):
    """
    Scrape introduction text from an academy's homepage
    
    Args:
        academy_base_url: Base URL of the academy (e.g., https://ghall.ugent.be)
        academy_name: Name of the academy for reference
        
    Returns:
        String containing the academy introduction HTML, or empty string if not found
    """
    print(f"Scraping introduction for {academy_name}...")
      # Special case for UGain - hardcoded content
    if "ugain" in academy_base_url.lower():
        return "<p>Welkom bij UGain, de academie voor levenslang leren aan de Faculteit Ingenieurswetenschappen en Architectuur van de Universiteit Gent.</p> <p>UGAin biedt een gevarieerd aanbod aan bijscholingen, studiedagen, opleidingen en postgraduaten rond actuele en innovatieve thema's in engineering en technologie.</p> <p>Met onze activiteiten slaan we de brug tussen universiteit en praktijk, en ondersteunen we ingenieurs en andere professionals in hun verdere ontwikkeling.</p>"
    
    # Special case for Dunant Academie - hardcoded content
    if "dunant" in academy_base_url.lower():
        return "<p>De <strong>Dunant Academie</strong> maakt recente inzichten uit wetenschap en praktijk toegankelijk voor werkveld of breed publiek.</p><p>Ons cursusaanbod helpt je omgaan met vraagstukken van vandaag en morgen. Bepaalde lessen kunnen zowel ter plaatse als online gevolgd worden, in de vorm van theorie of practicum.</p>"
    
    try:
        # Send an HTTP request to the homepage
        response = requests.get(academy_base_url, timeout=30)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the homepage: Status code {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error accessing {academy_base_url}: {e}")
        return ""
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find the introduction text using the provided CSS selector
    intro_element = soup.select_one("#block-system-main-block > article > div.field.field--name-field-body.field--type-entity-reference-revisions.field--label-hidden.field__items > div > article > div > div.layout__item.text--wrapper > div.clearfix.text-formatted.field.field--name-field-text.field--type-text-long.field--label-hidden.field__item")
    
    if intro_element:
        # Get the inner HTML content (preserve HTML formatting)
        inner_html = ''.join(str(child) for child in intro_element.children)
        return inner_html.strip()
    else:
        print(f"Could not find introduction text on {academy_base_url}")
        return ""

def scrape_teacher_details(teacher_url, teacher_name):
    """
    Scrape detailed information from a teacher page
    
    Args:
        teacher_url: URL of the teacher page
        teacher_name: Name of the teacher
        
    Returns:
        Dictionary with detailed teacher information
    """
    print(f"Scraping teacher details for: {teacher_name}")
    
    # Add a small delay to avoid overwhelming the server
    time.sleep(0.1)
    
    # Send an HTTP request to the URL
    try:
        response = requests.get(teacher_url, timeout=30)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the teacher page: Status code {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error accessing {teacher_url}: {e}")
        return {}
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize the details dictionary
    details = {
        'name': teacher_name,
        'link': teacher_url,
        'photo_url': '',
        'description': ''
    }
    
    # Extract teacher photo
    photo_element = soup.select_one("#block-system-main-block > div > section.main--2-columns > div.field.field--name-field-teacher-pic.field--type-image.field--label-hidden.field__item img")
    if photo_element:
        photo_src = photo_element.get('src', '')
        if photo_src:
            # Make the photo URL absolute if it's relative
            if photo_src.startswith('/'):
                base_url = teacher_url.split('/', 3)[0] + '//' + teacher_url.split('/', 3)[2]
                photo_src = base_url + photo_src
            details['photo_url'] = photo_src
    
    # Extract teacher description with HTML content preserved
    description_element = soup.select_one("#block-system-main-block > div > section.sidebar--second > div")
    if description_element:
        # Get the inner HTML content (preserve HTML formatting)
        inner_html = ''.join(str(child) for child in description_element.children)
        details['description'] = inner_html.strip()
    
    return details

if __name__ == "__main__":
    # Define the academies to scrape
    academies = [
        {
            'name': 'Humanities Academie',
            'url': 'https://humanitiesacademie.ugent.be/programma',
            'base_url': 'https://humanitiesacademie.ugent.be'
        },
        {
            'name': 'Gandaius Academy',
            'url': 'https://gandaiusacademy.ugent.be/programma',
            'base_url': 'https://gandaiusacademy.ugent.be'
        },
        {
            'name': 'Beta Academy',
            'url': 'https://beta-academy.ugent.be/programma',
            'base_url': 'https://beta-academy.ugent.be'
        },
        {
            'name': 'Ghall',
            'url': 'https://ghall.ugent.be/programma',
            'base_url': 'https://ghall.ugent.be'
        },        {
            'name': 'UGain',
            'url': 'https://ugain.ugent.be/programma',
            'base_url': 'https://ugain.ugent.be'
        },
        {
            'name': 'FEB Academy',
            'url': 'https://febacademy.ugent.be/programma',
            'base_url': 'https://febacademy.ugent.be'
        },
        {
            'name': 'ACVetMed',
            'url': 'https://acvetmed.ugent.be/programma',
            'base_url': 'https://acvetmed.ugent.be'
        },
        {
            'name': 'Dunant Academie',
            'url': 'https://dunantacademie.ugent.be/programma',
            'base_url': 'https://dunantacademie.ugent.be'
        },
        {
            'name': 'ALLPHA',
            'url': 'https://allpha.ugent.be/programma',
            'base_url': 'https://allpha.ugent.be'
        },
        {
            'name': 'APSS',
            'url': 'https://apss.ugent.be/programma',
            'base_url': 'https://apss.ugent.be'
        }
    ]
      # Dictionary to store all data
    all_data = {
        'academies': [],
        'metadata': academy_metadata,  # Add the metadata to the JSON
        'categories': [],
        'offerings': [],
        'teachers': [],
        'scraped_at': datetime.now().isoformat()
    }
    
    # Dictionary to store unique offerings by URL
    offerings_dict = {}
    
    # Dictionary to store unique teachers by URL
    teachers_dict = {}
    
    # Process each academy
    for academy in academies:
        academy_name = academy['name']
        academy_url = academy['url']
        base_url = academy['base_url']
        
        # Add academy to the data with its metadata
        academy_data = {
            'name': academy_name,
            'url': academy_url
        }
          # Add metadata from our predefined dictionary if available
        if base_url in academy_metadata:
            for key, value in academy_metadata[base_url].items():
                academy_data[key] = value
        
        # Scrape academy introduction text from homepage
        introduction = scrape_academy_introduction(base_url, academy_name)
        if introduction:
            academy_data['introduction'] = introduction
        
        all_data['academies'].append(academy_data)
        
        # Scrape categories for this academy
        categories = scrape_categories(academy_url, academy_name)
        
        if categories:
            print(f"Found {len(categories)} categories in {academy_name}")
            
            # Add categories to the data
            all_data['categories'].extend(categories)
            
            # Print the category results
            for i, category in enumerate(categories, 1):
                print(f"{i}. [{academy_name}] {category['name']} - {category['link']}")
            
            # Scrape offerings from each category
            for category in categories:
                category_offerings = scrape_offerings(category['link'], category['name'], academy_name)
                if category_offerings:
                    for offering in category_offerings:
                        # Use the URL as a unique identifier
                        offering_url = offering['link']
                        
                        if offering_url in offerings_dict:
                            # If this offering was already found in another category,
                            # add the current category to its categories list
                            current_category = f"{academy_name} - {category['name']}"
                            if current_category not in offerings_dict[offering_url]['categories']:
                                offerings_dict[offering_url]['categories'].append(current_category)
                        else:
                            # First time seeing this offering, initialize it with a categories list
                            offerings_dict[offering_url] = {
                                'title': offering['title'],
                                'link': offering_url,
                                'academy': academy_name,
                                'categories': [f"{academy_name} - {category['name']}"]
                            }
      # Now visit each offering page to get detailed information
    print("\nScraping detailed information for each offering...")
    for url, offering in offerings_dict.items():
        details = scrape_offering_details(url, offering['title'], offering['academy'])
        
        # Add the categories to the details
        details['categories'] = offering['categories']
        
        # Collect teachers from this offering
        for variation in details.get('variations', []):
            for teacher in variation.get('teachers', []):
                teacher_url = teacher.get('link', '')
                teacher_name = teacher.get('name', '')
                if teacher_url and teacher_name and teacher_url not in teachers_dict:
                    teachers_dict[teacher_url] = {
                        'name': teacher_name,
                        'link': teacher_url
                    }
        
        # Replace the basic offering with the detailed one
        offerings_dict[url] = details
    
    # Now scrape detailed information for each teacher
    print(f"\nScraping detailed information for {len(teachers_dict)} unique teachers...")
    for teacher_url, teacher_basic in teachers_dict.items():
        teacher_details = scrape_teacher_details(teacher_url, teacher_basic['name'])
        if teacher_details:
            teachers_dict[teacher_url] = teacher_details      # Convert the dictionaries to lists for the final JSON
    all_data['offerings'] = list(offerings_dict.values())
    all_data['teachers'] = list(teachers_dict.values())
    
    # Save all data to a single JSON file
    if all_data['offerings']:
        print(f"\nTotal unique offerings found: {len(all_data['offerings'])}")
        
        # Save to a single JSON file in the getdata directory
        combined_filename = "ugent_academies_data_detailed.json"
        output_path = os.path.join(os.path.dirname(__file__), combined_filename)
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_data, jsonfile, ensure_ascii=False, indent=4)
        
        print(f"Saved all data to {output_path}")
        
        # Print sample of detailed offerings
        print("\nSample of detailed offerings:")
        for i, offering in enumerate(all_data['offerings'][:3], 1):
            print(f"{i}. [{offering['academy']}] {offering['title']}")
            print(f"   - Categories: {', '.join(offering['categories'])}")
            print(f"   - Variations: {len(offering.get('variations', []))}")
        
        if len(all_data['offerings']) > 3:
            print(f"... and {len(all_data['offerings']) - 3} more offerings")
    else:
        print("No offerings were found in any academy")