from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from media.models import File, Image, Media
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter,
                               PolymorphicParentModelAdmin)
from reversion.admin import VersionAdmin


@admin.register(Media)
class MediaAdmin(PolymorphicParentModelAdmin, VersionAdmin):
    child_models = [File, Image]

    list_display = ['title', 'mime_type']
    list_filter = [PolymorphicChildModelFilter]

    readonly_fields = ['mime_type']
    search_fields = ['title', 'mime_type']


class MediaChildAdmin(PolymorphicChildModelAdmin, VersionAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    list_display = MediaAdmin.list_display
    readonly_fields = MediaAdmin.readonly_fields
    search_fields = MediaAdmin.search_fields + ['resource']
    show_in_index = True


@admin.register(File)
class FileAdmin(MediaChildAdmin):
    search_fields = MediaAdmin.search_fields + ['resource']


@admin.register(Image)
class ImageAdmin(MediaChildAdmin):
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="100px" />'.format(
            obj.resource.url))

    thumbnail.short_description = 'Image'

    list_display = ['thumbnail'] + MediaAdmin.list_display
    readonly_fields = MediaChildAdmin.readonly_fields + ['thumbnail']
