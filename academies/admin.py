from django.contrib import admin
from .models import Academy, Offering


@admin.register(Academy)
class AcademyAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour')
    search_fields = ('name',)


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('name', 'academy', 'description')
    list_filter = ('academy',)
    search_fields = ('name', 'description')
    list_select_related = ('academy',)
