# UGent Academy Data Management

This project manages data from UGent academies while preserving customizations like logos, colors, and sort orders. The application is fully bilingual (English/Dutch) and displays formatted HTML content from the original sites.

## ✅ COMPLETED FEATURES

This project now includes all the originally requested features:

✅ **Full Bilingual Support (EN/NL)** - Django internationalization enabled with comprehensive translations  
✅ **HTML Content Preservation** - Safely displays formatted HTML from course descriptions  
✅ **Complete Data Import** - Sessions, dates, and variations properly imported  
✅ **Image Support** - Offering images scraped and displayed on cards and detail pages  
✅ **Enhanced UI/UX** - Improved styling, filtering, and navigation  
✅ **Academy Introductions** - Homepage introduction text scraped and displayed  
✅ **Teacher Photos & Descriptions** - Full teacher profile information with photos  
✅ **Smart Filtering** - "Show upcoming only" and category filters work together  
✅ **UGain Integration** - Automatic post-import migration of UGain offerings  
✅ **One-Step Operation** - Single command updates everything automatically

## 🚀 ONE-STEP OPERATION

**Simply run this single command to get everything:**

```bash
python update_data.py
```

This command will automatically:
1. ✅ **Scrape** all data from academy websites (including images and teacher photos)
2. ✅ **Import** the data into Django database  
3. ✅ **Move** UGain offerings from Science Academy to UGain Academy
4. ✅ **Preserve** all customizations (logos, colors, sort orders)
5. ✅ **Handle** all file locations and dependencies

That's it! No other steps needed.

## Quick Start

### Using the Helper Script (Recommended)
The helper script automates the complete scraping, importing, and post-processing with a single command:

```bash
# Run the complete automated update process (scrape, import, and move UGain offerings)
python update_data.py

# To clear existing data before importing
python update_data.py --clear
```

This single command will:
1. ✅ Scrape data from all academy websites
2. ✅ Import the data into Django database  
3. ✅ Move UGain offerings from Science Academy to UGain Academy
4. ✅ Handle all file locations and dependencies automatically

### Running the Scraper and Import Separately (Manual Process)

If you need more control over each step, you can run them individually:

#### Step 1: Run the Scraper
```bash
# Run the scraper from the project root
python getdata/scrape2.py
# OR
cd getdata
python scrape2.py
```

#### Step 2: Import the Data into Django
```bash
# Import data from the detailed JSON file
python manage.py import_detailed_data getdata/ugent_academies_data_detailed.json

# To clear existing data before import (caution: this removes all existing data)
python manage.py import_detailed_data getdata/ugent_academies_data_detailed.json --clear
```

#### Step 3: Move UGain Offerings
```bash
# Move UGain offerings from Science Academy to UGain Academy
python manage.py move_ugain_offerings
```

### Legacy Methods
These methods are maintained for backward compatibility but using the newer methods above is recommended:

```bash
# Full scrape and import (legacy method)
python manage.py scrape_and_update

# Only scrape (legacy method)
python manage.py scrape_and_update --scrape-only

# Only import from specific JSON file (legacy method)
python manage.py scrape_and_update --import-only --json-file "path/to/data.json"
```

## What Gets Preserved

When you run the update process, the following academy customizations are **preserved**:
- ✅ Academy logos
- ✅ Academy colors (`colour` field)
- ✅ Sort order (`sort_order` field)
- ✅ Academy descriptions
- ✅ Creation timestamps
- ✅ HTML formatting in descriptions and program content

## What Gets Updated

The following data is refreshed from the websites:
- 🔄 All course offerings
- 🔄 Course variations (sessions with specific dates, prices, locations)
- 🔄 Teachers and their profiles
- 🔄 Categories
- 🔄 Languages
- 🔄 Locations
- 🔄 HTML-formatted content (descriptions, program content, remarks)

## File Structure

```
├── academies/                     # Django app
│   ├── management/commands/       # Custom management commands
│   │   ├── import_detailed_data.py # New import command (recommended)
│   │   ├── scrape_and_update.py   # Legacy update command
│   │   └── ...                    # Other management commands
│   ├── models.py                  # Database models
│   ├── views.py                   # Web views
│   ├── context_processors.py      # Context processors for language switcher
│   └── templates/                 # HTML templates
│       └── academies/             # App-specific templates
│           ├── base.html          # Base template with language switcher
│           ├── academy_list.html  # List of academies
│           ├── academy_detail.html # Academy detail page
│           ├── offering_list.html # List of offerings
│           ├── offering_detail.html # Offering detail with variations
│           └── ...                # Other templates
├── academy_site/                  # Django project settings
│   ├── settings.py                # Includes i18n configuration
│   └── urls.py                    # URL routing
├── getdata/                       # Data scraping tools
│   ├── scrape2.py                 # Improved scraper (preserves HTML)
│   ├── scrape.py                  # Legacy web scraper
│   └── ugent_academies_data_detailed.json  # Latest scraped data
├── locale/                        # Translation files
│   └── nl/                        # Dutch translations
│       └── LC_MESSAGES/
│           └── django.po          # Translation strings
├── media/                         # Media files
│   └── academy_logos/             # Academy logo images
├── update_data.py                 # Automated helper script (recommended)
├── manage.py                      # Django management script
└── README.md                      # This documentation
```

## How It Works

1. **Export Metadata**: Current academy customizations are exported from the database
2. **Scraping**: The scraper visits all academy websites and collects fresh data
3. **Import with Preservation**: New data is imported while preserving existing customizations
4. **Multilingual Support**: All templates use translation tags to support English and Dutch

## Language Management

### Translation Files
The application uses Django's translation system:
- Translation strings are defined in templates using `{% trans %}` tags
- Messages are extracted to the `.po` file using `python manage.py makemessages -l nl`
- After translation, they are compiled with `python manage.py compilemessages`

### Adding Translations
To update translations after changing templates:
```bash
# Extract new strings to the .po file
python manage.py makemessages -l nl

# Edit the translations in locale/nl/LC_MESSAGES/django.po

# Compile the translations
python manage.py compilemessages
```

### Language Switching
The application includes a language switcher in the navbar that:
- Sets the user's language preference
- Persists the language choice across sessions
- Automatically switches all content based on the selected language

## Troubleshooting

### Scraper Issues
- Check internet connection
- Verify academy websites are accessible
- Look for scraper output in `getdata/ugent_academies_data_detailed.json`
- If the scraper encounters errors, try running with smaller batches of academies (modify the `academies` list in the script)
- Check HTML formatting in the JSON output to ensure it's being preserved correctly

### File Location Issues
- The scraper (`scrape2.py`) is now configured to save JSON files in the `getdata/` directory
- The `update_data.py` script will automatically check both the root directory and the `getdata/` directory for the JSON file
- If it finds the file in the root directory, it will move it to the correct location automatically
- Always run scripts from the project root directory to ensure correct path resolution

### Import Issues
- Ensure JSON file exists and is valid
- Check Django database connection
- Verify all required models are migrated
- If variations/sessions are not appearing, check:
  - That they exist in the JSON data (look for the "variations" field in offerings)
  - That the import script is correctly processing all variations
  - Run with the `--clear` option to reset all data if necessary

### HTML Content Issues
- If HTML formatting is not displaying correctly, check:
  - That the templates are using the `|safe` filter for fields containing HTML
  - That the HTML content is properly preserved in the JSON file
  - That the import script is not stripping HTML tags

### Session/Date Display Issues
- If sessions/dates are not showing correctly:
  - Check if the variations exist in the JSON data
  - Verify that the variations were properly imported into the database
  - Check the template rendering logic for variations

### Academy Customizations Lost
If customizations were lost, they might be recoverable from:
- Database backups
- Previous JSON exports
- Git history (if tracked)

## Technical Details

### Database Models
- `Academy`: Main academy information with customizations
- `Offering`: Course offerings linked to academies
- `Variation`: Specific course instances with dates/prices
- `Teacher`: Instructor information
- `Category`, `Language`, `Location`: Supporting data

### Scraping Strategy
The scraper (`scrape2.py`) uses multiple selectors to capture:
- Regular course links
- Academic year-specific links (e.g., `/25-26/`, `/24-25/`)
- Category-based navigation
- Pagination handling
- HTML content preservation in descriptions, program content, and remarks
- Session/variation details including dates, teachers, and locations

### Data Preservation
Academy customizations are preserved using Django's `update_or_create()` with the preserved data in the `defaults` parameter, ensuring existing customizations aren't overwritten. HTML formatting in descriptions and content is preserved throughout the import process.

### Multilingual Support
The application supports both English and Dutch:
- Django's internationalization framework is used
- All templates include `{% load i18n %}` and use `{% trans %}` tags
- A language switcher is available in the navbar
- Translations are maintained in `locale/nl/LC_MESSAGES/django.po`

### HTML Content Handling
- HTML content is preserved during scraping and importing
- Templates use the `|safe` filter when displaying HTML content
- Fields that may contain HTML are documented in the models
- The scraper avoids stripping HTML tags from descriptions and program content

## Future Enhancements

- Automated scheduling (scheduled tasks)
- Change detection and notifications
- Backup/restore functionality
- Web interface for running updates
- Selective academy updates
- Expanded language support
