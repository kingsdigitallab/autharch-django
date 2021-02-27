import adminactions.actions as actions
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import site
from django.urls import include, path, re_path
from kdl_ldap.signal_handlers import \
    register_signal_handlers as kdl_ldap_register_signal_hadlers
from kdl_wagtail.core.api import api_router
from rest_framework.documentation import include_docs_urls


admin.autodiscover()

kdl_ldap_register_signal_hadlers()

site.add_action(actions.merge)

urlpatterns = [
    path('_nested_admin/', include('nested_admin.urls')),
    path('admin/', admin.site.urls),
    path('adminactions/', include('adminactions.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('wagtail/', include('wagtail.admin.urls')),

    path('documents/', include('wagtail.documents.urls')),

    path('editor/', include('editor.urls')),
    path('geonames/', include('geonames_place.urls')),
    path('vocabularies/', include('controlled_vocabulary.urls')),

    path('api/_docs/', include_docs_urls(
        title='AuthArch API Documentation', permission_classes=[])),
    path('api/archival/', include('archival.urls')),
    path('api/authority/', include('authority.urls')),
    path('api/jargon/', include('jargon.urls')),
    path('api/media/', include('media.urls')),
    path('api/wagtail/', api_router.urls),

    path('', include('wagtail.core.urls'))
]

# -----------------------------------------------------------------------------
# Django Debug Toolbar URLS
# -----------------------------------------------------------------------------
try:
    if settings.DEBUG:
        import debug_toolbar
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Static file DEBUGGING
# -----------------------------------------------------------------------------
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import os.path

    image_dir = os.path.join(settings.MEDIA_ROOT, 'ar_transcription_images')
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL + 'ar_transcription_images/',
                          document_root=image_dir)
