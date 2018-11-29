from archival.models import (Collection, File, Item, Organisation,
                             Reference, Series, Subject)
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from reversion.admin import VersionAdmin


class BaseAdmin(VersionAdmin):
    autocomplete_fields = ['references', 'languages', 'publication_status',
                           'subjects', 'persons_as_subjects',
                           'organisations_as_subjects', 'places_as_subjects']

    base_fieldsets = [
        [None, {
            'fields': ['repository', 'repository_code']
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
class CollectionAdmin(BaseAdmin):
    fieldsets = BaseAdmin.base_fieldsets + [
        [None, {
            'fields': ['administrative_history', 'arrangement']
        }]
    ]


@admin.register(Series)
class SeriesAdmin(BaseAdmin):
    autocomplete_fields = BaseAdmin.autocomplete_fields + [
        'collection', 'parent'
    ]

    fieldsets = [
        [None, {
            'fields': ['collection', 'parent']
        }]
    ] + BaseAdmin.base_fieldsets + [
        [None, {
            'fields': ['arrangement']
        }]
    ]


@admin.register(File)
class FileAdmin(BaseAdmin):
    autocomplete_fields = BaseAdmin.autocomplete_fields + [
        'series', 'parent', 'creators', 'record_type', 'persons_as_relations',
        'places_as_relations'
    ]

    base_fieldsets = BaseAdmin.base_fieldsets + [
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
            'fields': ['series', 'parent', 'creators', 'persons_as_relations',
                       'places_as_relations']
        }]
    ] + base_fieldsets


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    autocomplete_fields = BaseAdmin.autocomplete_fields + [
        'f', 'creators', 'record_type', 'creation_places',
        'persons_as_relations', 'places_as_relations'
    ]

    fieldsets = [
        [None, {
            'fields': ['f', 'creators', 'creation_places',
                       'persons_as_relations', 'places_as_relations']
        }]
    ] + FileAdmin.base_fieldsets


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ['title', 'unitid']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['title']
