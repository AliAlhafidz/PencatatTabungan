from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Goals
    path('', views.dashboard_view, name='dashboard'),
    path('goals/', views.goals_view, name='goals'),
    path('goals/create/', views.goal_create_view, name='goal_create'),
    path('goals/<int:pk>/', views.goal_detail_view, name='goal_detail'),
    path('goals/<int:pk>/edit/', views.goal_edit_view, name='goal_edit'),
    path('goals/<int:pk>/delete/', views.goal_delete_view, name='goal_delete'),
    
    # Transactions
    path('goals/<int:goal_id>/transactions/create/', views.transaction_create_view, name='transaction_create'),
    path('transactions/<int:pk>/delete/', views.transaction_delete_view, name='transaction_delete'),
    
    # Calculator
    path('calculator/', views.calculator_view, name='calculator'),
    path('calculator/calculate/', views.calculate_plan_htmx, name='calculate_plan'),
    
    # Reminders
    path('reminders/', views.reminders_view, name='reminders'),
    path('reminders/<int:pk>/toggle/', views.reminder_toggle_view, name='reminder_toggle'),
    path('reminders/<int:pk>/delete/', views.reminder_delete_view, name='reminder_delete'),
    
    # Settings & Utilities
    path('settings/', views.settings_view, name='settings'),
    path('settings/seed/', views.seed_dummy_data_view, name='seed_dummy_data'),
    path('settings/reset/', views.reset_all_data_view, name='reset_all_data'),
    
    # PWA Endpoints
    path('manifest.json', views.manifest_view, name='pwa_manifest'),
    path('sw.js', views.service_worker_view, name='pwa_sw'),
]
