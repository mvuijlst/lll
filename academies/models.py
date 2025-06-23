from django.db import models
from django.utils import timezone
from django.core.files.storage import default_storage
import os


class Academy(models.Model):
    """Represents a UGent Academy with basic information and metadata."""
    name = models.CharField(max_length=200, unique=True, help_text="Name of the academy")
    base_url = models.URLField(blank=True, help_text="Base URL of the academy website")
    program_url = models.URLField(blank=True, help_text="URL to the academy's program page")
    colour = models.CharField(max_length=7, blank=True, help_text="Hex color code (e.g., #FF5733)")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order in which this academy appears")
    description = models.TextField(blank=True, help_text="Short description of the academy")
    introduction = models.TextField(blank=True, help_text="Introduction text from academy homepage (may contain HTML)")
    logo = models.ImageField(upload_to='academy_logos/', blank=True, null=True, help_text="Academy logo image")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def primary_color(self):
        """Get the primary color or fallback to default UGent blue."""
        return self.colour if self.colour else '#1e3a8a'
    
    @property
    def light_color(self):
        """Get a lighter version of the academy color for backgrounds."""
        if not self.colour:
            return '#e0f2fe'
        
        # Convert hex to RGB and create a lighter version
        hex_color = self.colour.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Create a light version (increase values towards 255)
            r_light = min(255, r + (255 - r) * 0.8)
            g_light = min(255, g + (255 - g) * 0.8)
            b_light = min(255, b + (255 - b) * 0.8)
            
            return f'#{int(r_light):02x}{int(g_light):02x}{int(b_light):02x}'
        
        return '#e0f2fe'  # Fallback light blue
    
    @property 
    def contrast_color(self):
        """Get appropriate text color (black or white) for the academy color."""
        if not self.colour:
            return '#ffffff'
            
        hex_color = self.colour.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
              # Calculate luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return '#000000' if luminance > 0.5 else '#ffffff'
        
        return '#ffffff'
    
    class Meta:
        verbose_name_plural = "Academies"
        ordering = ['sort_order', 'name']


class Category(models.Model):
    """Categories for grouping offerings within academies."""
    name = models.CharField(max_length=200)
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='categories')
    url = models.URLField(blank=True, help_text="URL to the category page")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.academy.name})"
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['name', 'academy']
        ordering = ['academy__name', 'name']


class Language(models.Model):
    """Languages in which offerings are taught."""
    name = models.CharField(max_length=100, unique=True, help_text="Language name (e.g., Nederlands, English)")
    code = models.CharField(max_length=10, blank=True, help_text="Language code (e.g., nl, en)")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Location(models.Model):
    """Physical locations where offerings take place."""
    name = models.CharField(max_length=200, unique=True, help_text="Location name")
    url = models.URLField(blank=True, help_text="URL with location details")
    address = models.TextField(blank=True, help_text="Physical address")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Teacher(models.Model):
    """Teachers/instructors for offerings."""
    name = models.CharField(max_length=200, unique=True, help_text="Full name of the teacher")
    profile_url = models.URLField(blank=True, help_text="URL to teacher's profile page")
    title = models.CharField(max_length=100, blank=True, help_text="Academic title (e.g., Prof. dr.)")
    bio = models.TextField(blank=True, help_text="Teacher biography")
    photo_url = models.URLField(blank=True, help_text="URL to teacher's photo")
    description = models.TextField(blank=True, help_text="Teacher description from profile page (can contain HTML)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Offering(models.Model):
    """Main course/offering entity with all basic information."""
    url = models.URLField(unique=True, help_text="Original URL of the offering")
    title = models.CharField(max_length=300, help_text="Full title of the offering")
    course_id = models.CharField(max_length=50, blank=True, help_text="Course identifier")
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='offerings')
    # Keep the old field for backward compatibility during migration, but make it nullable
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='single_category_offerings')
    # Add the new many-to-many relationship
    categories = models.ManyToManyField(Category, blank=True, related_name='offerings')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='offerings')
    description = models.TextField(blank=True, help_text="Course description (can contain HTML)")
    program_content = models.TextField(blank=True, help_text="Detailed program content (can contain HTML)")
    remarks = models.TextField(blank=True, help_text="Additional remarks (can contain HTML)")
    image_url = models.URLField(blank=True, help_text="Main course image URL")
    thumbnail_url = models.URLField(blank=True, help_text="Thumbnail image URL")
    is_active = models.BooleanField(default=True, help_text="Whether the offering is currently active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.academy.name})"
    
    class Meta:
        ordering = ['academy__name', 'title']


class Variation(models.Model):
    """Specific instances/sessions of an offering with dates, prices, and locations."""
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name='variations')
    title = models.CharField(max_length=300, blank=True, help_text="Specific title for this variation")
    price = models.CharField(max_length=100, blank=True, help_text="Price as text (e.g., '€ 370,50')")
    lesson_dates = models.CharField(max_length=200, blank=True, help_text="Date range as text")
    start_date = models.DateTimeField(null=True, blank=True, help_text="Parsed start date")
    end_date = models.DateTimeField(null=True, blank=True, help_text="Parsed end date")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='variations')
    description = models.TextField(blank=True, help_text="Variation-specific description (can contain HTML)")
    registration_url = models.URLField(blank=True, help_text="Registration link")
    is_available = models.BooleanField(default=True, help_text="Whether registration is available")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        variation_title = self.title or self.offering.title
        date_info = f" ({self.lesson_dates})" if self.lesson_dates else ""
        return f"{variation_title}{date_info}"
    
    class Meta:
        ordering = ['offering__title', 'start_date']


class VariationTeacher(models.Model):
    """Many-to-many relationship between variations and teachers."""
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, related_name='variation_teachers')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='variation_teachers')
    role = models.CharField(max_length=100, blank=True, help_text="Role of teacher in this variation")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.teacher.name} - {self.variation}"
    
    class Meta:
        unique_together = ['variation', 'teacher']
        ordering = ['variation', 'teacher__name']


class Link(models.Model):
    """Links associated with offerings and variations."""
    LINK_TYPES = [
        ('registration', 'Registration'),
        ('information', 'Information'),
        ('category', 'Category'),
        ('teacher', 'Teacher Profile'),
        ('location', 'Location'),
        ('external', 'External Resource'),
        ('other', 'Other'),
    ]
    
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, null=True, blank=True, related_name='links')
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, null=True, blank=True, related_name='links')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='links')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='links')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='links')
    
    url = models.URLField(help_text="The actual link URL")
    text = models.CharField(max_length=200, help_text="Display text for the link")
    link_type = models.CharField(max_length=20, choices=LINK_TYPES, default='other', help_text="Type of link")
    context = models.CharField(max_length=100, blank=True, help_text="Context where this link appears")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.text} -> {self.url}"
    
    class Meta:
        ordering = ['link_type', 'text']
