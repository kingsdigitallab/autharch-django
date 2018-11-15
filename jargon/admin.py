from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from jargon.models import (EntityRelationType, EntityType, FamilyTreeLevel,
                           Function, MaintenanceStatus, NamePartType,
                           Publication, PublicationStatus, RecordType,
                           ResourceType)
from geonames_place.models import Place


class BaseJargonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    list_diplay = ['title']
    search_fields = ['title']


admin.site.register(EntityRelationType, BaseJargonAdmin)
admin.site.register(EntityType, BaseJargonAdmin)
admin.site.register(FamilyTreeLevel, BaseJargonAdmin)
admin.site.register(Function, BaseJargonAdmin)
admin.site.register(MaintenanceStatus, BaseJargonAdmin)
admin.site.register(NamePartType, BaseJargonAdmin)
admin.site.register(Publication, BaseJargonAdmin)
admin.site.register(PublicationStatus, BaseJargonAdmin)
admin.site.register(RecordType, BaseJargonAdmin)
admin.site.register(ResourceType, BaseJargonAdmin)

admin.site.unregister(Place)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['class_description', 'country', 'feature_class']
    list_display = ['address', 'class_description', 'country']
    list_filter = ['class_description', 'country']
    search_fields = ['address', 'country__name', 'country__code']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term)

        if len(queryset) < 10 and len(search_term) > 3:
            Place.create_or_update_from_geonames(search_term)
            queryset, use_distinct = super().get_search_results(
                request, queryset, search_term)

        return queryset, use_distinct
