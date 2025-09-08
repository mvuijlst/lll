from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class UGentAcademyAdminSite(AdminSite):
    site_header = _('UGent Academies Administration')
    site_title = _('UGent Academies Admin')
    index_title = _('Welcome to UGent Academies Administration')
    site_url = '/'
    
    def index(self, request, extra_context=None):
        """
        Custom admin index page with statistics.
        """
        from .models import Academy, Offering, Variation, Teacher
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_academies': Academy.objects.count(),
            'total_offerings': Offering.objects.count(),
            'active_offerings': Offering.objects.filter(is_active=True).count(),
            'total_variations': Variation.objects.count(),
            'available_variations': Variation.objects.filter(is_available=True).count(),
            'total_teachers': Teacher.objects.count(),
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = UGentAcademyAdminSite(name='ugent_admin')
