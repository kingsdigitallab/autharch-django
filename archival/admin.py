from archival.models import (
    ArchivalRecord, ArchivalRecordImage, ArchivalRecordSet,
    ArchivalRecordTranscription, Collection, File, Item, OriginLocation,
    Reference, Series, Project)
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter,
                               PolymorphicParentModelAdmin)
from reversion.admin import VersionAdmin


class ArchivalRecordImageInline(admin.TabularInline):
    model = ArchivalRecordImage


class ArchivalRecordTranscriptionInline(admin.TabularInline):
    model = ArchivalRecordTranscription


class OriginLocationInline(admin.TabularInline):
    model = OriginLocation


@admin.register(ArchivalRecord)
class ArchivalRecordAdmin(PolymorphicParentModelAdmin, VersionAdmin):
    base_model = Collection
    child_models = [Collection, File, Item, Series]

    list_display = ['archival_level', 'title']
    list_display_links = list_display
    list_filter = [PolymorphicChildModelFilter, 'repository',
                   'publication_status', 'description_date', 'project',
                   ('languages', admin.RelatedOnlyFieldListFilter)]

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
    autocomplete_fields = ['project', 'repository', 'references', 'languages',
                           'publication_status', 'subjects',
                           'persons_as_subjects', 'organisations_as_subjects',
                           'places_as_subjects', 'media', 'related_entities']
    inlines = [OriginLocationInline, ArchivalRecordImageInline,
               ArchivalRecordTranscriptionInline]

    base_fieldsets = [
        ['Repository', {
            'fields': ['repository']
        }],
        [None, {
            'fields': ['references']
        }],
        ['This is a sample group title', {
            'fields': ['title', ('start_date', 'end_date'),
                       'provenance']
        }],
        ['Media', {
            'classes': ['collapse'],
            'fields': ['media', 'caption']
        }],
        ['An example of a collapsible group', {
            'classes': ['collapse'],
            'fields': ['physical_location', 'languages', 'description',
                       'publication_description', 'notes', 'extent']
        }],
        ['Enhanced Dating', {
            'classes': ['collapse'],
            'fields': ['creation_dates', 'creation_dates_notes',
                       'aquisition_dates', 'aquisition_dates_notes']
        }],
        ['Connection information', {
            'classes': ['collapse'],
            'fields': ['connection_a', 'connection_b', 'connection_c',
                       'related_entities']
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
            'fields': ['rcin', 'publication_status', 'rights_declaration',
                       'sources']
        }],
        ['Project', {
            'fields': ['project']
        }],
    ]

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

    search_fields = ['title']
    show_in_index = True


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
        'parent_file', 'creators', 'record_type',
        'creation_places', 'persons_as_relations', 'places_as_relations'
    ]

    base_fieldsets = ArchivalRecordChildAdmin.base_fieldsets + [
        [None, {
            'fields': ['record_type', 'url', 'physical_description',
                       'creation_places']
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

    list_filter = [('creators', admin.RelatedOnlyFieldListFilter)]


@admin.register(Item)
class ItemAdmin(ArchivalRecordChildAdmin):
    autocomplete_fields = ArchivalRecordChildAdmin.autocomplete_fields + [
        'parent_series', 'parent_file', 'creators', 'record_type',
        'creation_places', 'persons_as_relations', 'places_as_relations'
    ]

    fieldsets = [
        [None, {
            'fields': ['parent_series', 'parent_file', 'creators',
                       'persons_as_relations',
                       'places_as_relations']
        }]
    ] + FileAdmin.base_fieldsets


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['source']
    search_fields = ['source__title', 'unitid']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
