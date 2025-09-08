from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from .models import Academy, Offering, Variation, Teacher
from datetime import datetime, timedelta

@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics and recent activity."""
    
    # Basic statistics
    total_academies = Academy.objects.count()
    total_offerings = Offering.objects.count()
    active_offerings = Offering.objects.filter(is_active=True).count()
    total_variations = Variation.objects.count()
    available_variations = Variation.objects.filter(is_available=True).count()
    total_teachers = Teacher.objects.count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_offerings = Offering.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_variations = Variation.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Academy statistics
    academy_stats = Academy.objects.annotate(
        offering_count=Count('offerings', distinct=True),
        variation_count=Count('offerings__variations', distinct=True)
    ).order_by('-offering_count')[:5]
    
    # Most popular languages
    language_stats = Offering.objects.values(
        'language__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_academies': total_academies,
        'total_offerings': total_offerings,
        'active_offerings': active_offerings,
        'total_variations': total_variations,
        'available_variations': available_variations,
        'total_teachers': total_teachers,
        'recent_offerings': recent_offerings,
        'recent_variations': recent_variations,
        'academy_stats': academy_stats,
        'language_stats': language_stats,
        'title': 'UGent Academies Dashboard',
    }
    
    return render(request, 'admin/dashboard.html', context)
