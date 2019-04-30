from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from jargon.models import (EntityRelationType, EntityType,
                           Function, MaintenanceStatus, NamePartType,
                           Publication, PublicationStatus, RecordType,
                           ReferenceSource, Repository, ResourceRelationType)


class BaseJargonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    list_display = ['title']
    search_fields = ['title']


admin.site.register(EntityRelationType, BaseJargonAdmin)
admin.site.register(EntityType, BaseJargonAdmin)
admin.site.register(Function, BaseJargonAdmin)
admin.site.register(MaintenanceStatus, BaseJargonAdmin)
admin.site.register(NamePartType, BaseJargonAdmin)
admin.site.register(Publication, BaseJargonAdmin)
admin.site.register(PublicationStatus, BaseJargonAdmin)
admin.site.register(RecordType, BaseJargonAdmin)
admin.site.register(ReferenceSource, BaseJargonAdmin)
admin.site.register(ResourceRelationType, BaseJargonAdmin)


@admin.register(Repository)
class RepositoryAdmin(BaseJargonAdmin):
    list_display = ['code'] + BaseJargonAdmin.list_display
    search_fields = ['code'] + BaseJargonAdmin.search_fields
