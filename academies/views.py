from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, Min
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
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
    offerings = academy.offerings.select_related(        'category', 'language'
    ).prefetch_related(
        'variations__location', 'categories'
    ).filter(is_active=True)
    
    # Filter by upcoming (default is on only when no form submission)
    # If any form parameter is present, don't use default
    has_form_params = any([
        request.GET.get('category'),
        request.GET.get('sort'),
        'upcoming' in request.GET
    ])
    
    if has_form_params:
        show_upcoming = request.GET.get('upcoming') == 'on'
    else:
        show_upcoming = True  # Default to True only when no form submitted
    
    if show_upcoming:
        now = timezone.now()
        offerings = offerings.filter(
            Q(variations__start_date__gte=now) | Q(variations__start_date__isnull=True)
        ).distinct()
    
    # Sort by
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'date':
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
    elif sort_by == 'title':
        offerings = offerings.order_by('title')
    else:
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
    
    # Get categories for this academy
    categories = academy.categories.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).order_by('name')
      # Filter by category if specified
    category_filter = request.GET.get('category')
    if category_filter:
        offerings = offerings.filter(
            Q(category__name=category_filter) | Q(categories__name=category_filter)
        ).distinct()
    
    # Get total count before pagination
    total_offerings = offerings.count()
    
    # Pagination
    paginator = Paginator(offerings, 12)  # Show 12 offerings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'academies/academy_detail.html', {
        'academy': academy,
        'offerings': page_obj,
        'categories': categories,
        'selected_category': category_filter,
        'selected_sort': sort_by,
        'show_upcoming': show_upcoming,
        'total_offerings': total_offerings
    })


def offering_list(request):
    """Display all offerings with filtering and search capabilities."""
    from django.utils import timezone
    
    offerings = Offering.objects.select_related(
        'academy', 'category', 'language'
    ).prefetch_related(
        'variations__location', 'categories'
    ).filter(is_active=True)    # Search functionality
    search_query = request.GET.get('search')
    if search_query and search_query.strip() and search_query.lower() != 'none':
        offerings = offerings.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(academy__name__icontains=search_query)
        )
    else:
        search_query = ''  # Clean up for template display
    
    # Filter by academy
    academy_filter = request.GET.get('academy')
    if academy_filter:
        offerings = offerings.filter(academy__id=academy_filter)
      # Filter by language
    language_filter = request.GET.get('language')
    if language_filter:
        offerings = offerings.filter(language__id=language_filter)
    
    # Filter by upcoming (default is on only when no form submission)
    # If any form parameter is present, don't use default
    has_form_params = any([
        request.GET.get('search'),
        request.GET.get('academy'),
        request.GET.get('language'),
        request.GET.get('sort'),
        'upcoming' in request.GET
    ])
    
    if has_form_params:
        show_upcoming = request.GET.get('upcoming') == 'on'
    else:
        show_upcoming = True  # Default to True only when no form submitted
    
    if show_upcoming:
        now = timezone.now()
        offerings = offerings.filter(
            Q(variations__start_date__gte=now) | Q(variations__start_date__isnull=True)
        ).distinct()
    
    # Sort by
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'date':
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
    elif sort_by == 'title':
        offerings = offerings.order_by('title')
    elif sort_by == 'academy':
        offerings = offerings.order_by('academy__name', 'title')
    else:
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
      # Get filter options
    academies = Academy.objects.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).filter(offering_count__gt=0).order_by('name')
    
    languages = Language.objects.annotate(
        offering_count=Count('offerings', filter=Q(offerings__is_active=True))
    ).filter(offering_count__gt=0).order_by('name')
    
    # Get total count before pagination
    total_count = offerings.count()
    
    # Pagination
    paginator = Paginator(offerings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'academies/offering_list.html', {
        'offerings': page_obj,
        'academies': academies,
        'languages': languages,
        'search_query': search_query,
        'selected_academy': academy_filter,
        'selected_language': language_filter,
        'selected_sort': sort_by,
        'show_upcoming': show_upcoming,
        'total_count': total_count
    })


# Add a language test view
def language_test(request):
    """A simple view to test language switching functionality."""
    return render(request, 'academies/language_test.html', {})

# Add a dedicated language switcher page
def language_switcher(request):
    """A dedicated page for switching languages."""
    redirect_to = request.GET.get('next', '/')
    return render(request, 'academies/language_switcher.html', {
        'redirect_to': redirect_to,
        'languages': settings.LANGUAGES
    })


def offering_detail(request, pk):
    """Display detailed view of a specific offering."""
    offering = get_object_or_404(
        Offering.objects.select_related(
            'academy', 'category', 'language'
        ).prefetch_related(
            'variations__location',
            'variations__variation_teachers__teacher',
            'links',
            'categories'
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
    ).prefetch_related(
        'categories', 'variations'
    ).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(program_content__icontains=query) |        Q(categories__name__icontains=query),
        is_active=True
    ).distinct()
    
    # Filter by upcoming (default is on only when no form submission)
    # If any form parameter is present, don't use default
    has_form_params = any([
        request.GET.get('sort'),
        'upcoming' in request.GET
    ])
    
    if has_form_params:
        show_upcoming = request.GET.get('upcoming') == 'on'
    else:
        show_upcoming = True  # Default to True only when no form submitted
    
    if show_upcoming:
        now = timezone.now()
        offerings = offerings.filter(
            Q(variations__start_date__gte=now) | Q(variations__start_date__isnull=True)
        ).distinct()
    
    # Sort by
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'date':
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
    elif sort_by == 'title':
        offerings = offerings.order_by('title')
    elif sort_by == 'academy':
        offerings = offerings.order_by('academy__name', 'title')
    else:
        offerings = offerings.annotate(
            earliest_date=Min('variations__start_date')
        ).order_by('earliest_date', 'title')
    
    offerings = offerings[:20]
    
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
        'selected_sort': sort_by,
        'show_upcoming': show_upcoming,
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
