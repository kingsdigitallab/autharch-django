from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from jargon.models import MaintenanceStatus, Publication, PublicationStatus


class BaseJargonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    list_diplay = ['title']
    search_fields = ['title']


admin.site.register(MaintenanceStatus, BaseJargonAdmin)
admin.site.register(Publication, BaseJargonAdmin)
admin.site.register(PublicationStatus, BaseJargonAdmin)
