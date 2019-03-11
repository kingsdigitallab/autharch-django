from django.contrib.admin.apps import AdminConfig


class AuthArchAdminConfig(AdminConfig):
    default_site = 'autharch.admin.AuthArchAdminSite'
