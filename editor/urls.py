from django.urls import path

from . import views


app_name = 'editor'
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('entities/', views.entities_list, name='entities-list'),
    path('entities/<int:entity_id>/', views.entity_edit, name='entity-edit'),
    path('entities/<int:entity_id>/history/', views.entity_history,
         name='entity-history'),
    path('entities/new/', views.entity_create, name='entity-create'),
    path('records/', views.records_list, name='records-list'),
    path('records/<int:record_id>/', views.record_edit, name='record-edit'),
    path('records/<int:record_id>/history/', views.record_history,
         name='record-history'),
]
