from django.contrib import admin
from jargon.models import MaintenanceStatus, PublicationStatus


class BaseJargonAdmin(admin.ModelAdmin):
    list_diplay = ['title']
    search_fields = ['title']


admin.site.register(MaintenanceStatus, BaseJargonAdmin)
admin.site.register(PublicationStatus, BaseJargonAdmin)
