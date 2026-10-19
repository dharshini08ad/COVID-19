"""Routes for the Meridian Care hospital management application."""
from django.urls import path

from . import views

app_name = 'hms'

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patients, name='patients'),
    path('patients/register/', views.patient_register, name='patient_register'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:patient_id>/discharge/', views.patient_discharge, name='patient_discharge'),
    path('staff/', views.staff, name='staff'),
    path('staff/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:staff_id>/edit/', views.staff_edit, name='staff_edit'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/<int:appointment_id>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:appointment_id>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('beds/', views.beds, name='beds'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.bigdata_export, name='bigdata_export'),
    path('analytics/query/', views.bigdata_query, name='bigdata_query'),
    path('bigdata/', views.bigdata_studio, name='bigdata_studio'),
    path('bigdata/sync/', views.bigdata_sync, name='bigdata_sync'),
    path('bigdata/preview/', views.bigdata_preview, name='bigdata_preview'),
    path('reports/', views.reports, name='reports'),
]