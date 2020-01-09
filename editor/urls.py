from django.urls import path

from . import views


app_name = 'editor'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('entities/', views.EntityListView.as_view(), name='entities-list'),
    path('entities/<int:entity_id>/', views.entity_edit, name='entity-edit'),
    path('entities/<int:entity_id>/delete/', views.entity_delete,
         name='entity-delete'),
    path('entities/<int:entity_id>/history/', views.entity_history,
         name='entity-history'),
    path('entities/new/', views.entity_create, name='entity-create'),
    path('records/', views.RecordListView.as_view(), name='records-list'),
    path('records/<int:record_id>/', views.record_edit, name='record-edit'),
    path('records/<int:record_id>/', views.record_delete,
         name='record-delete'),
    path('records/<int:record_id>/history/', views.record_history,
         name='record-history'),
    path('revert/', views.revert, name='revert'),
]
