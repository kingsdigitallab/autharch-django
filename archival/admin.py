from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from reversion.admin import VersionAdmin

from .models import (Collection, EditorType, File, Item, Organisation, Person,
                     Place, Publication, PublicationStatus, RecordType,
                     Reference, RevisionEvent, Series, Subject)


class BaseAdmin(VersionAdmin):
    autocomplete_fields = ['references', 'languages', 'publication_status',
                           'subjects', 'persons', 'organisations', 'places']

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
            'fields': ['subjects', 'persons', 'organisations', 'places']
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

    base_file_fieldsets = [
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
    pass


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    pass


@admin.register(EditorType)
class EditorTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    pass


@admin.register(PublicationStatus)
class PublicationStatusAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(RecordType)
class RecordTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ['title', 'unitid']


@admin.register(RevisionEvent)
class RevisionEventAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['title']
