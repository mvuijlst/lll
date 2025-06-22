from django import forms
from .models import Academy


class AcademyLogoUploadForm(forms.ModelForm):
    """Form for uploading academy logos."""
    
    class Meta:
        model = Academy
        fields = ['logo']
        widgets = {
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logo'].help_text = (
            'Upload a logo image for this academy. '
            'Supported formats: PNG, JPG, GIF, SVG. '
            'Recommended size: 200x60 pixels or similar aspect ratio.'
        )
