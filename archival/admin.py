from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from reversion.admin import VersionAdmin

from .models import (Collection, EditorType, File, Item, Language,
                     Organisation, Person, Place, Publication,
                     PublicationStatus, RecordType, Reference, RevisionEvent,
                     Series, Subject)


class BaseAdmin(VersionAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


@admin.register(Collection)
class CollectionAdmin(BaseAdmin):
    fieldsets = [
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
            'fields': ['administrative_history', 'arrangement',
                       'related_materials']
        }],
        [None, {
            'fields': ['cataloguer', 'description_date']
        }],
        [None, {
            'fields': ['publication_status', 'rights_declaration']
        }]
    ]

    autocomplete_fields = ['references', 'languages', 'publication_status',
                           'subjects', 'persons', 'organisations', 'places']


@admin.register(Series)
class SeriesAdmin(BaseAdmin):
    pass


@admin.register(File)
class FileAdmin(BaseAdmin):
    pass


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    pass


@admin.register(EditorType)
class EditorTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ['title']


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
