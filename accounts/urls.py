from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/login/', views.login_view, name='login'),
    path('api/log-click/', views.log_click, name='log_click'),
    
    # Admin routes
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/api/credentials/', views.view_credentials, name='view_credentials'),
    path('admin/api/recharges/', views.view_recharges, name='view_recharges'),
    path('admin/api/clicks/', views.view_clicks, name='view_clicks'),
    path('admin/export/all/', views.export_all_data, name='export_all'),
]