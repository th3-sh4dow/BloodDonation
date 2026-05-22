"""
URL configuration for bloodbank project.
Django serves both the REST API and the frontend HTML pages.

Routes:
  /api/...        → REST API
  /admin/         → Django admin
  /               → index.html
  /login/         → login.html
  /register/      → register.html
  /dashboard/     → dashboard.html
  /find-blood/    → find-blood.html
  /request-blood/ → request-blood.html
  /admin-panel/   → admin-panel.html
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # REST API
    path('api/', include('api.urls')),

    # Frontend pages — Django renders HTML from client/ folder
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('find-blood/', TemplateView.as_view(template_name='find-blood.html'), name='find-blood'),
    path('request-blood/', TemplateView.as_view(template_name='request-blood.html'), name='request-blood'),
    path('admin-panel/', TemplateView.as_view(template_name='admin-panel.html'), name='admin-panel'),
]
