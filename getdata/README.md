# UGent Academy Scraper

## Usage

The scraper is now configured to automatically scrape all UGent academies by default.

### Quick Start

```bash
python scrape.py
```

This will scrape all 10 configured academies and save the results to `ugent_academies_complete.json`.

### Configured Academies

The scraper will automatically scrape these academies:

1. **Humanities Academy** - https://humanitiesacademie.ugent.be
2. **Gandaius Academy** - https://gandaiusacademy.ugent.be
3. **Beta Academy** - https://beta-academy.ugent.be
4. **Ghent University Academic Hall** - https://ghall.ugent.be
5. **UGain** - https://ugain.ugent.be
6. **Faculty of Economics and Business Administration Academy** - https://febacademy.ugent.be
7. **Academy of Veterinary Medicine** - https://acvetmed.ugent.be
8. **Dunant Academy** - https://dunantacademie.ugent.be
9. **Allpha** - https://allpha.ugent.be
10. **APSS** - https://apss.ugent.be

### Output

The scraper will create:
- `ugent_academies_complete.json` - Complete results from all academies
- `intermediate_<academy>_<category>.json` - Intermediate results for each category

### Features

- **Automatic academy name extraction** - Extracts official academy names from page titles (e.g., "Programma | Academie voor Diergeneeskunde")
- **Automatic deduplication** - Offerings are deduplicated by URL
- **Category tracking** - Offerings can belong to multiple categories
- **Variation support** - Handles offerings with multiple parts/variations
- **Error handling** - Continues processing if individual requests fail
- **Progress tracking** - Detailed logging and progress updates
- **Rate limiting** - Respectful delays between requests

### Programmatic Usage

```python
from scrape import AcademyScraper

# Use default configuration (all academies)
scraper = AcademyScraper()
result = scraper.run()

# Or specify custom academies
custom_academies = ["https://humanitiesacademie.ugent.be"]
scraper = AcademyScraper(custom_academies)
result = scraper.run()
```
