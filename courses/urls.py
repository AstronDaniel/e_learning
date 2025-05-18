"""
URL patterns for the courses app.

This module contains URL patterns for course listing, details,
enrollment, and other course-related views.
"""
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course list view
    path('', views.CourseListView.as_view(), name='list'),
    
    # Instructor course management - these need to be BEFORE the detail view
    path('create/', views.CreateCourseView.as_view(), name='create'),
    path('create-category/', views.create_category, name='create_category'),
    path('my-courses/', views.InstructorCoursesView.as_view(), name='my_courses'),
    
    # Category view
    path('category/<slug:slug>/', views.CoursesByCategoryView.as_view(), name='category'),
    
    # Course detail view - this should be AFTER more specific paths
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    
    # Lesson views
    path('<slug:course_slug>/lessons/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson'),
    path('<slug:course_slug>/lessons/<int:lesson_id>/complete/', views.MarkLessonCompleteView.as_view(), name='mark_complete'),
    path('<slug:course_slug>/lessons/<int:lesson_id>/notes/', views.SaveLessonNoteView.as_view(), name='save_note'),
    
    # Enrollment and completion
    path('<slug:slug>/enroll/', views.EnrollCourseView.as_view(), name='enroll'),
    path('<slug:slug>/review/', views.ReviewCourseView.as_view(), name='review'),
    path('<slug:slug>/certificate/', views.CourseCertificateView.as_view(), name='certificate'),
]
