from archival.models import (ArchivalRecord, ArchivalRecordSet, Collection,
                             File, Item, Organisation, Reference, Series,
                             Subject)
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter,
                               PolymorphicParentModelAdmin)
from reversion.admin import VersionAdmin


@admin.register(ArchivalRecord)
class ArchivalRecordAdmin(PolymorphicParentModelAdmin, VersionAdmin):
    base_model = Collection
    child_models = [Collection, File, Item, Series]

    list_display = ['archival_level', 'title']
    list_display_links = list_display
    list_filter = [PolymorphicChildModelFilter]

    search_fields = ['title']


@admin.register(ArchivalRecordSet)
class ArchivalRecordSetAdmin(VersionAdmin):
    autocomplete_fields = ['archival_records']
    exclude = ['author']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    list_display = ['title', 'author', 'number_of_records']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user

        super().save_model(request, obj, form, change)


class ArchivalRecordChildAdmin(PolymorphicChildModelAdmin, VersionAdmin):
    autocomplete_fields = ['repository', 'references', 'languages',
                           'publication_status', 'subjects',
                           'persons_as_subjects', 'organisations_as_subjects',
                           'places_as_subjects']

    base_fieldsets = [
        ['Repository', {
            'fields': ['repository']
        }],
        [None, {
            'fields': ['references']
        }],
        ['This is a sample group title', {
            'fields': ['title', ('start_date', 'end_date'), 'creation_dates',
                       'provenance']
        }],
        ['An example of a collapsible group', {
            'classes': ['collapse'],
            'fields': ['languages', 'description', 'notes', 'extent']
        }],
        ['Subjects', {
            'fields': ['subjects', 'persons_as_subjects',
                       'organisations_as_subjects', 'places_as_subjects']
        }],
        [None, {
            'fields': ['related_materials']
        }],
        [None, {
            'fields': ['cataloguer', 'description_date']
        }],
        [None, {
            'fields': ['publication_status', 'rights_declaration']
        }]
    ]

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

    search_fields = ['title']


@admin.register(Collection)
class CollectionAdmin(ArchivalRecordChildAdmin):
    fieldsets = ArchivalRecordChildAdmin.base_fieldsets + [
        [None, {
            'fields': ['administrative_history', 'arrangement']
        }]
    ]


@admin.register(Series)
class SeriesAdmin(ArchivalRecordChildAdmin):
    autocomplete_fields = ArchivalRecordChildAdmin.autocomplete_fields + [
        'parent_collection', 'parent_series'
    ]

    fieldsets = [
        [None, {
            'fields': ['parent_collection', 'parent_series']
        }]
    ] + ArchivalRecordChildAdmin.base_fieldsets + [
        [None, {
            'fields': ['arrangement']
        }]
    ]


@admin.register(File)
class FileAdmin(ArchivalRecordChildAdmin):
    autocomplete_fields = ArchivalRecordChildAdmin.autocomplete_fields + [
        'parent_series', 'parent_file', 'creators', 'record_type',
        'persons_as_relations', 'places_as_relations'
    ]

    base_fieldsets = ArchivalRecordChildAdmin.base_fieldsets + [
        [None, {
            'fields': ['record_type', 'url', 'physical_description']
        }],
        [None, {
            'fields': ['copyright_status', 'publication_permission',
                       'withheld']
        }]
    ]

    fieldsets = [
        [None, {
            'fields': ['parent_series', 'parent_file', 'creators',
                       'persons_as_relations', 'places_as_relations']
        }]
    ] + base_fieldsets


@admin.register(Item)
class ItemAdmin(ArchivalRecordChildAdmin):
    autocomplete_fields = ArchivalRecordChildAdmin.autocomplete_fields + [
        'parent_series', 'parent_file', 'creators', 'record_type',
        'creation_places', 'persons_as_relations', 'places_as_relations'
    ]

    fieldsets = [
        [None, {
            'fields': ['parent_series', 'parent_file', 'creators',
                       'creation_places', 'persons_as_relations',
                       'places_as_relations']
        }]
    ] + FileAdmin.base_fieldsets


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['source']
    search_fields = ['source__title', 'unitid']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['title']
