from django.contrib import admin
from scm.models import EditorType, RevisionEvent


@admin.register(EditorType)
class EditorTypeAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(RevisionEvent)
class RevisionEventAdmin(admin.ModelAdmin):
    search_fields = ['title']
