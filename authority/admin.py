import nested_admin
from authority.models import (BiographyHistory, Description, Entity,
                              EntityRelationType, EntityType, Event,
                              FamilyTreeLevel, Function, Identity,
                              LanguageScript, LegalStatus, LocalDescription,
                              Mandate, NameEntry, NamePart, NamePartType,
                              Place, Relation, Resource, ResourceType,
                              Structure)
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from reversion.admin import VersionAdmin


class EventInline(nested_admin.NestedTabularInline):
    model = Event

    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class BiographyHistoryInline(nested_admin.NestedStackedInline):
    model = BiographyHistory

    extra = 1
    inlines = [EventInline]
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class LanguageScriptInline(nested_admin.NestedTabularInline):
    model = LanguageScript

    autocomplete_fields = ['language', 'script']
    extra = 1


class LegalStatusInline(nested_admin.NestedStackedInline):
    model = LegalStatus

    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class LocalDescriptionInline(nested_admin.NestedStackedInline):
    model = LocalDescription

    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class MandateInline(nested_admin.NestedStackedInline):
    model = Mandate

    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class PlaceInline(nested_admin.NestedStackedInline):
    model = Place

    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class StructureInline(nested_admin.NestedTabularInline):
    model = Structure

    autocomplete_fields = ['level']
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


@admin.register(Description)
class DescriptionAdmin(nested_admin.NestedModelAdmin, VersionAdmin):
    autocomplete_fields = ['function']
    inlines = [PlaceInline, LanguageScriptInline, BiographyHistoryInline,
               LocalDescriptionInline, MandateInline, LegalStatusInline,
               StructureInline]
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    list_display = ['entity', 'date_from', 'date_to']


@admin.register(EntityRelationType)
class EntityRelationType(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(FamilyTreeLevel)
class FamilyTreeLevelAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    search_fields = ['title']


class NamePartInline(nested_admin.NestedTabularInline):
    model = NamePart

    autocomplete_fields = ['name_part_type']
    extra = 2


class NameEntryInline(nested_admin.NestedTabularInline):
    model = NameEntry

    autocomplete_fields = ['language', 'script']
    extra = 1
    inlines = [NamePartInline]


@admin.register(Identity)
class IdentityAdmin(nested_admin.NestedModelAdmin, VersionAdmin):
    # autocomplete_fields = ['entity']
    inlines = [NameEntryInline]
    list_display = ['entity', 'authorised_form', 'date_from', 'date_to']


# @admin.register(NameEntry)
# class NameEntryAdmin(VersionAdmin):
#     inlines = [NamePartInline]
#     list_display = ['identity', 'authorised_form', 'language', 'script']


# @admin.register(NamePart)
# class NamePartAdmin(VersionAdmin):
#     list_display = ['name_entry', 'name_part_type', 'part']


class DescriptionInline(nested_admin.NestedTabularInline):
    model = Description

    autocomplete_fields = DescriptionAdmin.autocomplete_fields
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    inlines = DescriptionAdmin.inlines


class IdentityInline(nested_admin.NestedTabularInline):
    model = Identity

    extra = 1
    inlines = [NameEntryInline]


class RelationInline(nested_admin.NestedStackedInline):
    model = Relation

    autocomplete_fields = ['relation_type']
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class ResourceInline(nested_admin.NestedStackedInline):
    model = Resource

    autocomplete_fields = ['resource_type']
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


@admin.register(Entity)
class Entity(nested_admin.NestedModelAdmin, VersionAdmin):
    autocomplete_fields = ['entity_type']
    inlines = [IdentityInline, DescriptionInline,
               RelationInline, ResourceInline]
    list_display = ['entity_type']


@admin.register(NamePartType)
class NamePartTypeAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    search_fields = ['title']
