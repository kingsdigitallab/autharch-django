from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views


app_name = 'editor'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('account/login/',
         auth_views.LoginView.as_view(
             template_name='editor/login.html'
         ), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/password_reset/',
         auth_views.PasswordResetView.as_view(
             email_template_name='editor/password_reset_email.html',
             subject_template_name='editor/password_reset_subject.txt',
             success_url=reverse_lazy('editor:password_reset_done'),
             template_name='editor/password_reset_form.html'),
         name='password_reset'),
    path('account/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='editor/password_reset_done.html'),
         name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             success_url=reverse_lazy('editor:password_reset_complete'),
             template_name='editor/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('account/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='editor/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/new_user/', views.user_create, name='user-create'),
    path('dashboard/reset-password/<int:user_id>/', views.password_reset,
         name='reset-password'),
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
