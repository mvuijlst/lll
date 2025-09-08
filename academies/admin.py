from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Academy, Category, Language, Location, Teacher, 
    Offering, Variation, VariationTeacher, Link
)


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1
    fields = ('title', 'price', 'lesson_dates', 'start_date', 'end_date', 'location', 'is_available', 'registration_url')
    show_change_link = True
    readonly_fields = ('created_at', 'updated_at')

class VariationTeacherInline(admin.TabularInline):
    model = VariationTeacher
    extra = 1
    fields = ('teacher', 'role')
    autocomplete_fields = ['teacher']


@admin.register(Academy)
class AcademyAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'color_display', 'logo_preview', 'offering_count', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_editable = ('sort_order',)
    ordering = ('sort_order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'offering_count')
    actions = ['export_selected_csv']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'sort_order')
        }),
        ('URLs and Media', {
            'fields': ('base_url', 'program_url', 'logo')
        }),
        ('Display', {
            'fields': ('colour',)
        }),
        ('Statistics', {
            'fields': ('offering_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            offering_count=Count('offerings', distinct=True)
        )
    
    def logo_preview(self, obj):
        """Display a small preview of the academy logo."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 30px; max-width: 60px; object-fit: contain;" />',
                obj.logo.url
            )
        return "No logo"
    logo_preview.short_description = 'Logo Preview'
    
    def color_display(self, obj):
        """Display the academy color as a colored box."""
        if obj.colour:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div> {}',
                obj.colour,
                obj.colour
            )
        return "No color set"
    color_display.short_description = 'Color'
    
    def offering_count(self, obj):
        """Display count of offerings for this academy."""
        return obj.offering_count if hasattr(obj, 'offering_count') else obj.offerings.count()
    offering_count.short_description = 'Offerings'
    offering_count.admin_order_field = 'offering_count'
    
    def export_selected_csv(self, request, queryset):
        """Export selected academies to CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="academies.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Color', 'Sort Order', 'Base URL', 'Created'])
        
        for academy in queryset:
            writer.writerow([
                academy.name,
                academy.colour,
                academy.sort_order,
                academy.base_url,
                academy.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_selected_csv.short_description = "Export selected academies to CSV"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'academy', 'offering_count', 'created_at')
    list_filter = ('academy', 'created_at')
    search_fields = ('name',)
    list_select_related = ('academy',)
    readonly_fields = ('created_at', 'offering_count')
    autocomplete_fields = ['academy']
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            offering_count=Count('offerings', distinct=True)
        )
    
    def offering_count(self, obj):
        """Display count of offerings in this category."""
        return obj.offering_count if hasattr(obj, 'offering_count') else obj.offerings.count()
    offering_count.short_description = 'Offerings'
    offering_count.admin_order_field = 'offering_count'


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'offering_count', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'offering_count')
    ordering = ('name',)
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            offering_count=Count('offerings', distinct=True)
        )
    
    def offering_count(self, obj):
        """Display count of offerings in this language."""
        return obj.offering_count if hasattr(obj, 'offering_count') else obj.offerings.count()
    offering_count.short_description = 'Offerings'
    offering_count.admin_order_field = 'offering_count'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'variation_count', 'created_at', 'updated_at')
    search_fields = ('name', 'address')
    readonly_fields = ('created_at', 'updated_at', 'variation_count')
    ordering = ('name',)
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            variation_count=Count('variations', distinct=True)
        )
    
    def variation_count(self, obj):
        """Display count of variations at this location."""
        return obj.variation_count if hasattr(obj, 'variation_count') else obj.variations.count()
    variation_count.short_description = 'Variations'
    variation_count.admin_order_field = 'variation_count'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'photo_preview', 'profile_url', 'variation_count', 'created_at', 'updated_at')
    search_fields = ('name', 'title', 'bio')
    readonly_fields = ('created_at', 'updated_at', 'variation_count')
    list_filter = ('created_at',)
    ordering = ('name',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'profile_url', 'photo_url')
        }),
        ('Details', {
            'fields': ('bio', 'description')
        }),
        ('Statistics', {
            'fields': ('variation_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            variation_count=Count('variation_teachers', distinct=True)
        )
    
    def photo_preview(self, obj):
        """Display a small preview of the teacher photo."""
        if obj.photo_url:
            return format_html(
                '<img src="{}" style="max-height: 30px; max-width: 30px; border-radius: 50%; object-fit: cover;" />',
                obj.photo_url
            )
        return "No photo"
    photo_preview.short_description = 'Photo'
    
    def variation_count(self, obj):
        """Display count of variations this teacher is associated with."""
        return obj.variation_count if hasattr(obj, 'variation_count') else obj.variation_teachers.count()
    variation_count.short_description = 'Variations'
    variation_count.admin_order_field = 'variation_count'


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('title', 'academy', 'category_list', 'language', 'variation_count', 'is_active', 'image_preview', 'created_at')
    list_filter = ('academy', 'language', 'is_active', 'created_at', 'categories')
    search_fields = ('title', 'course_id', 'description')
    list_select_related = ('academy', 'language')
    readonly_fields = ('created_at', 'updated_at', 'variation_count', 'image_preview')
    autocomplete_fields = ['academy', 'language']
    filter_horizontal = ('categories',)
    actions = ['activate_offerings', 'deactivate_offerings', 'export_selected_csv']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'course_id', 'url', 'academy', 'categories', 'language', 'is_active')
        }),
        ('Content', {
            'fields': ('description', 'program_content', 'remarks')
        }),
        ('Media', {
            'fields': ('image_url', 'thumbnail_url', 'image_preview')
        }),
        ('Statistics', {
            'fields': ('variation_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [VariationInline]
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('categories').annotate(
            variation_count=Count('variations', distinct=True)
        )
    
    def category_list(self, obj):
        """Display comma-separated list of categories."""
        return ", ".join([cat.name for cat in obj.categories.all()])
    category_list.short_description = 'Categories'
    
    def variation_count(self, obj):
        """Display count of variations for this offering."""
        return obj.variation_count if hasattr(obj, 'variation_count') else obj.variations.count()
    variation_count.short_description = 'Variations'
    variation_count.admin_order_field = 'variation_count'
    
    def image_preview(self, obj):
        """Display a preview of the offering image."""
        image_url = obj.get_display_image_url()
        if image_url:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 80px; object-fit: cover;" />',
                image_url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def activate_offerings(self, request, queryset):
        """Bulk activate selected offerings."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} offerings were successfully activated.')
    activate_offerings.short_description = "Activate selected offerings"
    
    def deactivate_offerings(self, request, queryset):
        """Bulk deactivate selected offerings."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} offerings were successfully deactivated.')
    deactivate_offerings.short_description = "Deactivate selected offerings"
    
    def export_selected_csv(self, request, queryset):
        """Export selected offerings to CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="offerings.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Academy', 'Course ID', 'Language', 'Active', 'Variations', 'Created'])
        
        for offering in queryset:
            writer.writerow([
                offering.title,
                offering.academy.name,
                offering.course_id,
                offering.language.name if offering.language else '',
                offering.is_active,
                offering.variations.count(),
                offering.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_selected_csv.short_description = "Export selected offerings to CSV"


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('title_or_offering', 'offering_academy', 'price', 'lesson_dates', 'location', 'teacher_list', 'is_available', 'created_at')
    list_filter = ('offering__academy', 'location', 'is_available', 'created_at', 'start_date')
    search_fields = ('title', 'offering__title', 'price', 'description')
    list_select_related = ('offering', 'offering__academy', 'location')
    readonly_fields = ('created_at', 'updated_at', 'teacher_count')
    autocomplete_fields = ['offering', 'location']
    date_hierarchy = 'start_date'
    actions = ['mark_available', 'mark_unavailable']
    fieldsets = (
        ('Basic Information', {
            'fields': ('offering', 'title', 'price', 'is_available')
        }),
        ('Schedule & Location', {
            'fields': ('lesson_dates', 'start_date', 'end_date', 'location')
        }),
        ('Details', {
            'fields': ('description', 'registration_url')
        }),
        ('Statistics', {
            'fields': ('teacher_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [VariationTeacherInline]
    
    def get_queryset(self, request):
        """Optimize queries with related counts."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            teacher_count=Count('variation_teachers', distinct=True)
        )
    
    def title_or_offering(self, obj):
        """Display variation title or offering title if no variation title."""
        return obj.title or obj.offering.title
    title_or_offering.short_description = 'Title'
    title_or_offering.admin_order_field = 'title'
    
    def offering_academy(self, obj):
        """Display the academy of the related offering."""
        return obj.offering.academy.name
    offering_academy.short_description = 'Academy'
    offering_academy.admin_order_field = 'offering__academy__name'
    
    def teacher_list(self, obj):
        """Display comma-separated list of teachers."""
        teachers = obj.variation_teachers.select_related('teacher').all()
        return ", ".join([vt.teacher.name for vt in teachers])
    teacher_list.short_description = 'Teachers'
    
    def teacher_count(self, obj):
        """Display count of teachers for this variation."""
        return obj.teacher_count if hasattr(obj, 'teacher_count') else obj.variation_teachers.count()
    teacher_count.short_description = 'Teachers'
    teacher_count.admin_order_field = 'teacher_count'
    
    def mark_available(self, request, queryset):
        """Mark selected variations as available."""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} variations were marked as available.')
    mark_available.short_description = "Mark selected variations as available"
    
    def mark_unavailable(self, request, queryset):
        """Mark selected variations as unavailable."""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} variations were marked as unavailable.')
    mark_unavailable.short_description = "Mark selected variations as unavailable"


@admin.register(VariationTeacher)
class VariationTeacherAdmin(admin.ModelAdmin):
    list_display = ('variation', 'teacher', 'role', 'created_at')
    list_filter = ('variation__offering__academy', 'teacher', 'role')
    search_fields = ('variation__title', 'teacher__name', 'role')
    list_select_related = ('variation', 'teacher')
    readonly_fields = ('created_at',)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('text', 'url', 'link_type', 'context', 'created_at')
    list_filter = ('link_type', 'created_at')
    search_fields = ('text', 'url', 'context')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Link Information', {
            'fields': ('text', 'url', 'link_type', 'context')
        }),
        ('Associations', {
            'fields': ('offering', 'variation', 'teacher', 'category', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
