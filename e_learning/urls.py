"""
URL configuration for e_learning project.

This module contains the main URL patterns for the e-learning platform.
It includes routes for admin, authentication, courses, quizzes, and forums.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views
from .dashboard_redirects import dashboard_redirect

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Homepage and core views
    path('', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    
    # App URLs
    path('courses/', include('courses.urls')),
    path('users/', include('users.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('forums/', include('forums.urls')),
    path('instructor/', include('instructor.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
