# UGent Academy Data Management

This project manages data from UGent academies while preserving customizations like logos, colors, and sort orders.

## Quick Start

### Using the Detailed JSON Import
```bash
# Import data from the detailed JSON file
python manage.py import_detailed_data getdata/ugent_academies_data_detailed.json

# Clear existing data before import
python manage.py import_detailed_data getdata/ugent_academies_data_detailed.json --clear
```

### Legacy Methods
```bash
# Full scrape and import
python manage.py scrape_and_update

# Only scrape
python manage.py scrape_and_update --scrape-only

# Only import from specific JSON file
python manage.py scrape_and_update --import-only --json-file "path/to/data.json"
```

## What Gets Preserved

When you run the update process, the following academy customizations are **preserved**:
- ✅ Academy logos
- ✅ Academy colors (`colour` field)
- ✅ Sort order (`sort_order` field)
- ✅ Academy descriptions
- ✅ Creation timestamps

## What Gets Updated

The following data is refreshed from the websites:
- 🔄 All course offerings
- 🔄 Course variations (dates, prices, locations)
- 🔄 Teachers and their profiles
- 🔄 Categories
- 🔄 Languages
- 🔄 Locations

## File Structure

```
├── academies/                      # Django app
│   ├── management/commands/        
│   │   ├── scrape_and_update.py   # Main update command
│   │   ├── load_academy_data.py   # Legacy import command
│   │   └── ...
│   ├── models.py                   # Database models
│   └── views.py                    # Web views
├── getdata/
│   ├── scrape.py                   # Web scraper
│   └── ugent_academies_complete.json  # Latest scraped data
├── update_academy_data.py          # Helper script
└── README.md                       # This file
```

## How It Works

1. **Export Metadata**: Current academy customizations are exported from the database
2. **Scraping**: The scraper visits all academy websites and collects fresh data
3. **Import with Preservation**: New data is imported while preserving existing customizations

## Troubleshooting

### Scraper Issues
- Check internet connection
- Verify academy websites are accessible
- Look for scraper output in `getdata/ugent_academies_complete.json`

### Import Issues
- Ensure JSON file exists and is valid
- Check Django database connection
- Verify all required models are migrated

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
The scraper uses multiple selectors to capture:
- Regular course links
- Academic year-specific links (e.g., `/25-26/`, `/24-25/`)
- Category-based navigation
- Pagination handling

### Data Preservation
Academy customizations are preserved using Django's `update_or_create()` with the preserved data in the `defaults` parameter, ensuring existing customizations aren't overwritten.

## Future Enhancements

- Automated scheduling (cron jobs)
- Change detection and notifications
- Backup/restore functionality
- Web interface for running updates
- Selective academy updates
