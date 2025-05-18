from django.urls import path
from . import views

app_name = 'instructor'

urlpatterns = [
    # Main dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Course management
    path('courses/', views.courses_list, name='courses'),
    path('courses/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:course_slug>/lessons/', views.lessons_list, name='lessons'),
    path('courses/<slug:course_slug>/lessons/add/', views.add_lesson, name='add_lesson'),
    path('courses/<slug:course_slug>/lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('courses/<slug:course_slug>/lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('courses/<slug:course_slug>/lessons/<int:lesson_id>/get/', views.get_lesson_details, name='get_lesson_details'),
    path('courses/<slug:course_slug>/lessons/reorder/', views.reorder_lessons, name='reorder_lessons'),
    path('courses/<slug:course_slug>/students/', views.student_list, name='students'),
    
    # Analytics
    path('analytics/', views.analytics_overview, name='analytics'),
    path('analytics/course/<slug:course_slug>/', views.course_analytics, name='course_analytics'),
    
    # Quiz management
    path('quizzes/', views.quizzes_list, name='quizzes'),
    path('quizzes/<int:quiz_id>/results/', views.quiz_results_overview, name='quiz_results'),
    
    # Forum management
    path('forums/', views.forums_list, name='forums'),
    path('forums/<slug:course_slug>/', views.forum_moderation, name='forum_moderation'),
]
