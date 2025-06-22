from django.conf import settings

def language_settings(request):
    """Add available languages to template context."""
    return {
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
