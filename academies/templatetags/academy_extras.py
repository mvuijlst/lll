from django import template

register = template.Library()

@register.filter
def language_code(language_name):
    """Convert language name to short code."""
    if not language_name:
        return ''
    
    language_map = {
        'Nederlands': 'NL',
        'English': 'EN',
        'Français': 'FR',
        'Deutsch': 'DE',
    }
    
    return language_map.get(language_name, language_name[:2].upper())

@register.filter
def first_variation_date(offering):
    """Get the first upcoming variation date for an offering."""
    if not offering.variations.exists():
        return None
    
    # Get the first variation with the earliest date
    first_variation = offering.variations.filter(
        lesson_dates__isnull=False
    ).exclude(lesson_dates='').first()
    
    if first_variation:
        return first_variation.lesson_dates
    
    return None
