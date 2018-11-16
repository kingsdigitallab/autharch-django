from django.contrib.admin.apps import AdminConfig


class GppAdminConfig(AdminConfig):
    default_site = 'gpp.admin.GppAdminSite'
