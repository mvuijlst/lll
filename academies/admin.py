from django.contrib import admin
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


@admin.register(Academy)
class AcademyAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'colour', 'has_logo', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_editable = ('sort_order',)
    ordering = ('sort_order', 'name')
    readonly_fields = ('created_at', 'updated_at')
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
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_logo(self, obj):
        """Display whether the academy has a logo uploaded."""
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Has Logo'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'academy', 'created_at')
    list_filter = ('academy',)
    search_fields = ('name',)
    list_select_related = ('academy',)
    readonly_fields = ('created_at',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created_at', 'updated_at')
    search_fields = ('name', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'profile_url', 'created_at', 'updated_at')
    search_fields = ('name', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('title', 'academy', 'category', 'language', 'is_active', 'created_at')
    list_filter = ('academy', 'category', 'language', 'is_active', 'created_at')
    search_fields = ('title', 'course_id', 'description')
    list_select_related = ('academy', 'category', 'language')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'course_id', 'url', 'academy', 'category', 'language', 'is_active')
        }),
        ('Content', {
            'fields': ('description', 'program_content', 'remarks')
        }),
        ('Media', {
            'fields': ('image_url', 'thumbnail_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [VariationInline]


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('title', 'offering', 'price', 'lesson_dates', 'location', 'is_available', 'created_at')
    list_filter = ('offering__academy', 'location', 'is_available', 'created_at')
    search_fields = ('title', 'offering__title', 'price')
    list_select_related = ('offering', 'location')
    readonly_fields = ('created_at', 'updated_at')
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
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
