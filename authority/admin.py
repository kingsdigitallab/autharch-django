import nested_admin
from authority.models import (BiographyHistory, Control, Description, Entity,
                              Event, Identity, LanguageScript, LegalStatus,
                              LocalDescription, Mandate, NameEntry, NamePart,
                              Place, Relation, Resource, Source)
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from reversion.admin import VersionAdmin


class EventInline(nested_admin.NestedStackedInline):
    model = Event

    autocomplete_fields = ['place']
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class BiographyHistoryInline(nested_admin.NestedStackedInline):
    model = BiographyHistory

    extra = 0
    inlines = [EventInline]
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class LanguageScriptInline(nested_admin.NestedTabularInline):
    model = LanguageScript

    autocomplete_fields = ['language', 'script']
    extra = 0


class LegalStatusInline(nested_admin.NestedStackedInline):
    model = LegalStatus

    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class LocalDescriptionInline(nested_admin.NestedStackedInline):
    model = LocalDescription

    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class MandateInline(nested_admin.NestedStackedInline):
    model = Mandate

    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class PlaceInline(nested_admin.NestedStackedInline):
    model = Place

    autocomplete_fields = ['place']
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class NamePartInline(nested_admin.NestedTabularInline):
    model = NamePart

    autocomplete_fields = ['name_part_type']
    extra = 2


class NameEntryInline(nested_admin.NestedTabularInline):
    model = NameEntry

    autocomplete_fields = ['language', 'script']
    extra = 0
    inlines = [NamePartInline]


class SourceInline(nested_admin.NestedStackedInline):
    model = Source

    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class ControlInline(nested_admin.NestedStackedInline):
    model = Control

    autocomplete_fields = ['language', 'script',
                           'maintenance_status', 'publication_status']
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    inlines = [SourceInline]


class DescriptionInline(nested_admin.NestedStackedInline):
    model = Description

    autocomplete_fields = ['function']
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    inlines = [PlaceInline, LanguageScriptInline, BiographyHistoryInline,
               LocalDescriptionInline, MandateInline, LegalStatusInline]


class RelationInline(nested_admin.NestedStackedInline):
    model = Relation
    fk_name = 'identity'

    autocomplete_fields = ['place', 'relation_type', 'related_entity']
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class ResourceInline(nested_admin.NestedStackedInline):
    model = Resource

    autocomplete_fields = ['relation_type']
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class IdentityInline(nested_admin.NestedTabularInline):
    model = Identity

    extra = 0
    inlines = [NameEntryInline, DescriptionInline,
               RelationInline, ResourceInline]


@admin.register(Entity)
class Entity(nested_admin.NestedModelAdmin, VersionAdmin):
    autocomplete_fields = ['project', 'entity_type']
    inlines = [IdentityInline, ControlInline]
    list_display = ['display_name', 'project', 'entity_type']
    search_fields = ['identities__name_entries__display_name']
    list_filter = ['project']
