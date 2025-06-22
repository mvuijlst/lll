import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AcademyScraper:
    def __init__(self, base_urls=None):
        if base_urls is None:
            # Default list of all UGent academies to scrape
            base_urls = [
                "https://humanitiesacademie.ugent.be",
                "https://gandaiusacademy.ugent.be",
                "https://beta-academy.ugent.be",
                "https://ghall.ugent.be",
                "https://ugain.ugent.be",
                "https://febacademy.ugent.be",
                "https://acvetmed.ugent.be",
                "https://dunantacademie.ugent.be",
                "https://allpha.ugent.be",
                "https://apss.ugent.be"
            ]
        
        # Accept both string and list
        if isinstance(base_urls, str):
            base_urls = [base_urls]
            
        self.base_urls = base_urls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_data = {
            'academies': [],  # List of academies
            'offerings': {}  # Use dict to avoid duplicates, keyed by URL
        }
        
    def get_page(self, url, retries=3):
        """Fetch a page with retry logic"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
    
    def extract_field_data(self, soup, base_url):
        """Extract all field data from a detail page"""
        fields = {}
        field_divs = soup.find_all('div', class_='field')
        
        logger.info(f"Found {len(field_divs)} field elements")
        
        for field_div in field_divs:
            # Extract field name from class
            field_classes = field_div.get('class', [])
            field_name = None
            
            for cls in field_classes:
                if cls.startswith('field--name-'):
                    field_name = cls.replace('field--name-', '')
                    break
            
            if not field_name:
                logger.warning(f"Could not extract field name from classes: {field_classes}")
                continue
                  # Extract field value
            field_item = field_div.find(class_='field__item')
            if field_item:
                # Special handling for variations field
                if field_name == 'variations':
                    variations_data = self.extract_variations_data(field_item, base_url)
                    fields[field_name] = variations_data
                # Handle different content types
                elif field_item.find('a'):
                    # If it contains links, extract both text and URLs
                    links = []
                    for link in field_item.find_all('a'):
                        href = link.get('href')
                        if href:
                            href = urljoin(base_url, href)
                        links.append({
                            'text': link.get_text(strip=True),
                            'url': href
                        })
                    fields[field_name] = {
                        'text': field_item.get_text(strip=True),
                        'links': links
                    }
                else:
                    # Plain text content
                    fields[field_name] = field_item.get_text(strip=True)
            else:                # Sometimes the content is directly in the field div
                fields[field_name] = field_div.get_text(strip=True)
        
        return fields
    
    def extract_variations_data(self, variations_item, base_url):
        """Extract structured data from the variations field"""
        variations_data = {}
          # Extract title from h3
        title_elem = variations_item.find('h3')
        if title_elem:
            title_field = title_elem.find('div', class_='field__item')
            if title_field:
                variations_data['title'] = title_field.get_text(strip=True)
            else:
                # Try to get content directly from the h3
                title_div = title_elem.find('div')
                if title_div:
                    variations_data['title'] = title_div.get_text(strip=True)
        
        # Extract teachers
        teachers_field = variations_item.find('div', class_='field--name-field-teachers')
        if teachers_field:
            teachers = []
            teacher_links = []
            for teacher_item in teachers_field.find_all('div', class_='field__item'):
                teacher_text = teacher_item.get_text(strip=True)
                if teacher_text:
                    teachers.append(teacher_text)
                
                # Check for links
                teacher_link = teacher_item.find('a')
                if teacher_link:
                    href = teacher_link.get('href')
                    if href:
                        href = urljoin(base_url, href)
                    teacher_links.append({
                        'text': teacher_text,
                        'url': href
                    })
            
            if teachers:
                if teacher_links:
                    variations_data['teachers'] = {
                        'text': ', '.join(teachers),
                        'links': teacher_links
                    }
                else:
                    variations_data['teachers'] = ', '.join(teachers)
        
        # Extract description
        description_field = variations_item.find('div', class_='field--name-field-description')
        if description_field:
            desc_item = description_field.find('div', class_='field__item')
            if desc_item:
                description_text = desc_item.get_text(strip=True)
                desc_links = []
                
                # Extract links from description
                for link in desc_item.find_all('a'):
                    href = link.get('href')
                    if href:
                        href = urljoin(base_url, href)
                    desc_links.append({
                        'text': link.get_text(strip=True),
                        'url': href
                    })
                
                if desc_links:
                    variations_data['description'] = {
                        'text': description_text,
                        'links': desc_links
                    }
                else:
                    variations_data['description'] = description_text
        
        # Extract price
        price_field = variations_item.find('div', class_='field--name-price')
        if price_field:
            price_item = price_field.find('div', class_='field__item')
            if price_item:
                variations_data['price'] = price_item.get_text(strip=True)
        
        # Extract lesson dates
        dates_field = variations_item.find('div', class_='field--name-field-lesson-dates')
        if dates_field:
            dates_item = dates_field.find('div', class_='field__item')
            if dates_item:
                variations_data['lesson_dates'] = dates_item.get_text(strip=True)        # Extract location
        location_field = variations_item.find('div', class_='field--name-field-location-ref')
        if location_field:
            location_item = location_field.find('div', class_='field__item')
            if location_item:
                location_text = location_item.get_text(strip=True)
                location_link = location_item.find('a')
                
                if location_link:
                    href = location_link.get('href')
                    if href:
                        href = urljoin(base_url, href)
                    variations_data['location'] = {
                        'text': location_text,
                        'url': href
                    }
                else:
                    variations_data['location'] = location_text
            else:
                # Try to get content directly from the field div
                location_text = location_field.get_text(strip=True)
                location_link = location_field.find('a')
                
                if location_link:
                    href = location_link.get('href')
                    if href:
                        href = urljoin(base_url, href)
                    variations_data['location'] = {
                        'text': location_text,
                        'url': href
                    }
                elif location_text:
                    variations_data['location'] = location_text
        
        # Also extract these fields directly to the top level for easier access
        if 'title' in variations_data:
            variations_data['title'] = variations_data['title']
        if 'teachers' in variations_data:
            variations_data['field-teachers'] = variations_data['teachers']
        if 'price' in variations_data:
            variations_data['price'] = variations_data['price']
        if 'lesson_dates' in variations_data:
            variations_data['field-lesson-dates'] = variations_data['lesson_dates']
        if 'location' in variations_data:
            variations_data['field-location-ref'] = variations_data['location']
        if 'description' in variations_data:
            variations_data['field-description'] = variations_data['description']
        
        # Also keep the original combined text for backwards compatibility
        variations_data['combined_text'] = variations_item.get_text(strip=True)
        
        return variations_data
    
    def scrape_offering_detail(self, url, category_name, base_url, academy_name):
        """Scrape a single offering detail page"""
        logger.info(f"Scraping offering detail: {url}")
        
        response = self.get_page(url)
        if not response:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else "Unknown Title"
        
        # Extract all field data
        fields = self.extract_field_data(soup, base_url)
        
        offering_data = {
            'url': url,
            'title': title_text,
            'fields': fields,
            'academy': academy_name,
            'categories': [category_name]  # Initialize with current category
        }
        
        logger.info(f"Extracted {len(fields)} fields from {title_text}")
        
        return offering_data
    
    def add_or_update_offering(self, offering_data):
        """Add a new offering or update existing one with additional categories"""
        url = offering_data['url']
        
        if url in self.scraped_data['offerings']:
            # Offering already exists, add category if not already present
            existing = self.scraped_data['offerings'][url]
            for category in offering_data['categories']:
                if category not in existing['categories']:
                    existing['categories'].append(category)
            logger.info(f"Updated categories for existing offering: {offering_data['title']}")
        else:
            # New offering
            self.scraped_data['offerings'][url] = offering_data
            logger.info(f"Added new offering: {offering_data['title']}")

    def scrape_category_list(self, url, category_name, base_url, academy_name):
        """Scrape a category list page to get all offerings"""
        print(f"      🗂️  Processing category: {category_name}")
        logger.info(f"Scraping category list: {category_name} - {url}")
        
        response = self.get_page(url)
        if not response:
            print(f"      ❌ Failed to access category page")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        offerings = []
        
        # Look for links that might be offerings
        # Try different selectors based on common patterns
        potential_selectors = [
            'a[href*="/MC/"]',  # Micro-credentials
            'a[href*="/programma/"]',  # Program links
            '.view-content a',  # Views content links
            '.item-list a',  # Item list links
            'article a',  # Article links
            '.node a'  # Node links
        ]
        
        offering_links = []
        for selector in potential_selectors:
            links = soup.select(selector)
            if links:
                logger.info(f"Found {len(links)} links with selector: {selector}")
                offering_links.extend(links)
                break
        
        # Remove duplicates and filter valid links
        seen_urls = set()
        for link in offering_links:
            href = link.get('href')
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            
            # Skip if already seen or if it's not a detail page
            if full_url in seen_urls or full_url == url:
                continue
                
            # Skip navigation/system links
            if any(skip in href.lower() for skip in ['login', 'search', 'contact', 'home', 'admin']):
                continue
                
            seen_urls.add(full_url)
            
            title = link.get_text(strip=True)
            if title:
                offering_links_filtered = {
                    'title': title,
                    'url': full_url
                }
                offerings.append(offering_links_filtered)
        
        logger.info(f"Found {len(offerings)} unique offerings in {category_name}")
        print(f"      📋 Found {len(offerings)} potential offerings")
        
        # Filter out offerings that only have minimal fields (likely category pages)
        detailed_offerings = []
        for i, offering in enumerate(offerings, 1):
            print(f"      📄 [{i}/{len(offerings)}] {offering['title'][:50]}{'...' if len(offering['title']) > 50 else ''}")
            logger.info(f"Processing offering: {offering['title']}")
            
            detail_data = self.scrape_offering_detail(offering['url'], category_name, base_url, academy_name)
            if detail_data and len(detail_data['fields']) > 2:  # Only keep offerings with substantial content
                self.add_or_update_offering(detail_data)
                detailed_offerings.append(detail_data)
                print(f"         ✅ Added ({len(detail_data['fields'])} fields)")
            else:
                print(f"         ⚠️  Skipped (insufficient data)")
              # Small delay to be respectful
            time.sleep(0.5)
        
        print(f"      ✅ Category complete: {len(detailed_offerings)} offerings added")
        return detailed_offerings

    def scrape_main_page(self, url, academy_name):
        """Scrape the main program page to get categories"""
        logger.info(f"Scraping main page: {url}")
        print(f"      🌐 Connecting to website...")
          # Extract base URL from the main page URL
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        response = self.get_page(url)
        if not response:
            print(f"      ❌ Failed to connect to website")
            return False
            
        print(f"      ✅ Connected successfully")
        soup = BeautifulSoup(response.content, 'html.parser')
          # Extract actual academy name from page title
        print(f"      📄 Analyzing page structure...")
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Title format is usually "Programma | Academy Name"
            if '|' in title_text:
                actual_academy_name = title_text.split('|')[1].strip()
                print(f"      🏷️  Academy name: {actual_academy_name}")
                logger.info(f"Extracted academy name from title: {actual_academy_name}")
                academy_name = actual_academy_name
            else:
                logger.info(f"Using title as academy name: {title_text}")
                academy_name = title_text
        else:
            logger.warning(f"No title found, using URL-derived name: {academy_name}")
            print(f"      ⚠️  Using URL-derived name: {academy_name}")

        # Look for category links
        print(f"      🔍 Searching for program categories...")
        category_links = []
        
        # Try different selectors for finding categories
        potential_selectors = [
            'a[href*="/programma/"]',
            '.menu a',
            '.block-menu a',
            '.view-content a',
            'nav a'
        ]
        
        for selector in potential_selectors:
            links = soup.select(selector)
            if links:
                logger.info(f"Found {len(links)} potential category links with selector: {selector}")
                category_links.extend(links)
          # Filter and deduplicate category links
        categories = []
        seen_urls = set()
        
        for link in category_links:
            href = link.get('href')
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            
            # Skip if already seen or if it's the same as the main page
            if full_url in seen_urls or full_url == url:
                continue
                
            # Must be a programma subpage
            if '/programma/' not in full_url:
                continue
                
            seen_urls.add(full_url)
            
            title = link.get_text(strip=True)
            if title:
                categories.append({
                    'name': title,
                    'url': full_url
                })

        logger.info(f"Found {len(categories)} categories for {academy_name}")
        print(f"      📚 Found {len(categories)} program categories")
        
        if len(categories) == 0:
            print(f"      ⚠️  No categories found - this might be a single-page academy")
        else:
            print(f"      📋 Categories: {', '.join([cat['name'] for cat in categories])}")

        # Store academy info
        academy_info = {
            'name': academy_name,
            'base_url': base_url,
            'program_url': url,
            'categories': [cat['name'] for cat in categories]
        }
        self.scraped_data['academies'].append(academy_info)
        
        # Scrape each category
        print(f"      🚀 Starting category scraping...")
        for i, category in enumerate(categories, 1):
            print(f"   📁 [{i}/{len(categories)}] Processing: {category['name']}")
            logger.info(f"Processing category: {category['name']} for {academy_name}")
            
            self.scrape_category_list(category['url'], category['name'], base_url, academy_name)
            
            print(f"   ✅ [{i}/{len(categories)}] Completed: {category['name']}")
        
        if len(categories) > 0:
            print(f"      🎉 All categories processed for {academy_name}")
        
        return True, academy_name
    
    def save_data(self, filename=None):
        """Save scraped data to JSON file"""
        if not filename:
            filename = f"humanities_academy_data_{int(time.time())}.json"
        
        filepath = os.path.join(os.getcwd(), filename)
        # Convert offerings dict to list for final output
        output_data = {
            'academies': self.scraped_data['academies'],
            'offerings': list(self.scraped_data['offerings'].values())
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filepath}")
        return filepath

    def run(self):
        """Run the complete scraping process for all academies"""
        print(f"\n🚀 UGent Academy Scraper Started")
        print(f"={'=' * 60}")
        print(f"📊 Target: {len(self.base_urls)} academies")
        print(f"🕐 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}")
        
        logger.info(f"Starting scraper for {len(self.base_urls)} academies")
        
        success_count = 0
        failed_academies = []
        
        for i, base_url in enumerate(self.base_urls, 1):
            # Extract academy name from URL
            academy_name = self.extract_academy_name(base_url)
            
            print(f"\n📍 [{i}/{len(self.base_urls)}] {academy_name}")
            print(f"   🌐 URL: {base_url}")
            
            # Construct program URL
            program_url = f"{base_url}/programma"
            
            print(f"   🔍 Scraping from: {program_url}")
            logger.info(f"Scraping {academy_name} from {program_url}")
            
            # Track start time for this academy
            academy_start_time = time.time()
            
            result = self.scrape_main_page(program_url, academy_name)
            
            academy_duration = time.time() - academy_start_time
            
            if result:
                success, actual_academy_name = result
                if success:
                    success_count += 1
                    offerings_count = len([o for o in self.scraped_data['offerings'].values() 
                                         if o.get('academy') == actual_academy_name])
                    print(f"   ✅ Success! Found {offerings_count} offerings ({academy_duration:.1f}s)")
                    logger.info(f"Successfully scraped {actual_academy_name}")
                else:
                    failed_academies.append(actual_academy_name)
                    print(f"   ❌ Failed to scrape offerings ({academy_duration:.1f}s)")
                    logger.error(f"Failed to scrape {actual_academy_name}")
            else:
                failed_academies.append(academy_name)
                print(f"   ❌ Failed to access website ({academy_duration:.1f}s)")
                logger.error(f"Failed to scrape {academy_name}")
              # Progress indicator
            progress = (i / len(self.base_urls)) * 100
            print(f"   📈 Progress: {progress:.1f}% ({i}/{len(self.base_urls)} completed)")
        
        print(f"\n🏁 Scraping Phase Complete")
        print(f"{'=' * 60}")
        
        if success_count > 0:
            print(f"💾 Saving data to file...")
            final_filename = "ugent_academies_complete.json"
            filepath = self.save_data(final_filename)
            
            # Print detailed summary
            total_offerings = len(self.scraped_data['offerings'])
            total_academies = len(self.scraped_data['academies'])
            
            print(f"\n🎉 === SCRAPING COMPLETE ===")
            print(f"{'=' * 60}")
            print(f"✅ Successfully scraped: {success_count}/{len(self.base_urls)} academies")
            if failed_academies:
                print(f"❌ Failed academies: {len(failed_academies)}")
                for failed in failed_academies:
                    print(f"   • {failed}")
            print(f"📊 Total unique offerings found: {total_offerings}")
            print(f"🏫 Academy breakdown:")
            
            # Show breakdown by academy
            for academy_info in self.scraped_data['academies']:
                academy_offerings = len([o for o in self.scraped_data['offerings'].values() 
                                       if o.get('academy') == academy_info['name']])
                print(f"   • {academy_info['name']}: {academy_offerings} offerings in {len(academy_info['categories'])} categories")
                
            print(f"💾 Data saved to: {filepath}")
            print(f"🕐 Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 60}")
            
            return filepath
        else:
            print(f"❌ All scraping attempts failed!")
            if failed_academies:
                print(f"Failed academies: {', '.join(failed_academies)}")
            logger.error("All scraping attempts failed")
            return None
    
    def extract_academy_name(self, base_url):
        """Extract academy name from URL"""
        # Remove protocol and www
        domain = base_url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Extract the first part of the domain
        parts = domain.split('.')
        if len(parts) > 0:
            name = parts[0]
            # Convert to title case and replace common patterns
            name = name.replace('academie', 'Academy').replace('academy', 'Academy')
            return name.title()
        
        return "Unknown Academy"

def main():
    # Create scraper with default configuration (all UGent academies)
    print("🎓 UGent Academy Scraper")
    print("=" * 50)
    print("📖 This will scrape all configured UGent academies")
    print("   and extract their program offerings with details.")
    print("=" * 50)
    
    scraper = AcademyScraper()  # Uses default list of all academies
    
    print(f"\n📋 Configured to scrape {len(scraper.base_urls)} academies:")
    for i, url in enumerate(scraper.base_urls, 1):
        academy_name = scraper.extract_academy_name(url)
        print(f"  {i:2d}. {academy_name:<20} | {url}")
    
    print(f"\n🚀 Starting scrape process...")
    print("=" * 50)
    
    start_time = time.time()
    result = scraper.run()
    total_time = time.time() - start_time
    
    if result:
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📁 Data saved to: {result}")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
    else:
        print(f"\n❌ Scraping failed.")
        print(f"⏱️  Total time: {total_time:.1f} seconds")

if __name__ == "__main__":
    main()
