from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Academy, Offering, Category, Language, Location, Teacher, Variation
from .forms import AcademyLogoUploadForm


def academy_list(request):
    """Display all academies with their offering counts."""
    academies = Academy.objects.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).order_by('sort_order', 'name')
    
    return render(request, 'academies/academy_list.html', {
        'academies': academies
    })


def academy_detail(request, pk):
    """Display detailed view of an academy with its offerings and categories."""
    academy = get_object_or_404(Academy, pk=pk)
    
    # Get offerings with related data
    offerings = academy.offerings.select_related(
        'category', 'language'
    ).prefetch_related(
        'variations__location'
    ).filter(is_active=True).order_by('title')
    
    # Get categories for this academy
    categories = academy.categories.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).order_by('name')
    
    # Filter by category if specified
    category_filter = request.GET.get('category')
    if category_filter:
        offerings = offerings.filter(category__name=category_filter)
    
    # Pagination
    paginator = Paginator(offerings, 12)  # Show 12 offerings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'academies/academy_detail.html', {
        'academy': academy,
        'offerings': page_obj,
        'categories': categories,
        'selected_category': category_filter,
        'total_offerings': offerings.count()
    })


def offering_list(request):
    """Display all offerings with filtering and search capabilities."""
    offerings = Offering.objects.select_related(
        'academy', 'category', 'language'
    ).prefetch_related(
        'variations__location'
    ).filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        offerings = offerings.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(academy__name__icontains=search_query)
        )
    
    # Filter by academy
    academy_filter = request.GET.get('academy')
    if academy_filter:
        offerings = offerings.filter(academy__id=academy_filter)
    
    # Filter by language
    language_filter = request.GET.get('language')
    if language_filter:
        offerings = offerings.filter(language__id=language_filter)
    
    # Get filter options
    academies = Academy.objects.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).filter(offering_count__gt=0).order_by('name')
    
    languages = Language.objects.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).filter(offering_count__gt=0).order_by('name')
    
    # Pagination
    paginator = Paginator(offerings.order_by('academy__name', 'title'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'academies/offering_list.html', {
        'offerings': page_obj,
        'academies': academies,
        'languages': languages,
        'search_query': search_query,
        'selected_academy': academy_filter,
        'selected_language': language_filter,
        'total_count': offerings.count()
    })


def offering_detail(request, pk):
    """Display detailed view of a specific offering."""
    offering = get_object_or_404(
        Offering.objects.select_related(
            'academy', 'category', 'language'
        ).prefetch_related(
            'variations__location',
            'variations__variation_teachers__teacher',
            'links'
        ),
        pk=pk,
        is_active=True
    )
    
    # Get active variations
    variations = offering.variations.filter(
        is_available=True
    ).order_by('start_date')
    
    # Get upcoming variations
    now = timezone.now()
    upcoming_variations = variations.filter(
        Q(start_date__gte=now) | Q(start_date__isnull=True)
    )
    
    return render(request, 'academies/offering_detail.html', {
        'offering': offering,
        'variations': variations,
        'upcoming_variations': upcoming_variations,
    })


def teacher_list(request):
    """Display all teachers."""
    teachers = Teacher.objects.annotate(
        variation_count=Count('variation_teachers__variation', distinct=True)
    ).order_by('name')
    
    # Pagination
    paginator = Paginator(teachers, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'academies/teacher_list.html', {
        'teachers': page_obj
    })


def teacher_detail(request, pk):
    """Display detailed view of a teacher."""
    teacher = get_object_or_404(Teacher, pk=pk)
    
    # Get variations taught by this teacher
    variations = Variation.objects.select_related(
        'offering__academy', 'location'
    ).filter(
        variation_teachers__teacher=teacher,
        is_available=True
    ).order_by('-start_date')
    
    return render(request, 'academies/teacher_detail.html', {
        'teacher': teacher,
        'variations': variations
    })


def search_results(request):
    """Global search across all content."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'academies/search_results.html', {
            'query': query,
            'no_query': True
        })
    
    # Search offerings
    offerings = Offering.objects.select_related(
        'academy', 'category'
    ).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(program_content__icontains=query),
        is_active=True
    ).order_by('academy__name', 'title')[:20]
    
    # Search academies
    academies = Academy.objects.filter(
        name__icontains=query
    ).order_by('name')[:10]
    
    # Search teachers
    teachers = Teacher.objects.filter(
        Q(name__icontains=query) |
        Q(bio__icontains=query)
    ).order_by('name')[:15]
    
    total_results = offerings.count() + academies.count() + teachers.count()
    
    return render(request, 'academies/search_results.html', {
        'query': query,
        'offerings': offerings,
        'academies': academies,
        'teachers': teachers,
        'total_results': total_results
    })


@staff_member_required
def academy_logo_upload(request, pk):
    """Allow staff to upload logos for academies."""
    academy = get_object_or_404(Academy, pk=pk)
    
    if request.method == 'POST':
        form = AcademyLogoUploadForm(request.POST, request.FILES, instance=academy)
        if form.is_valid():
            form.save()
            messages.success(request, f'Logo uploaded successfully for {academy.name}')
            return redirect('academies:academy_detail', pk=academy.pk)
    else:
        form = AcademyLogoUploadForm(instance=academy)
    
    return render(request, 'academies/academy_logo_upload.html', {
        'academy': academy,
        'form': form
    })
