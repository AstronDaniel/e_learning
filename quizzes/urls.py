"""
URL patterns for the quizzes app.

This module contains URL patterns for quiz listing, taking quizzes,
viewing results, and other quiz-related views.
"""
from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    # Quiz views
    path('<int:quiz_id>/', views.quiz_detail, name='detail'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start'),
    path('<int:quiz_id>/submit/', views.submit_quiz, name='submit'),
    path('<int:quiz_id>/result/<int:attempt_id>/', views.quiz_result, name='result'),
    path('course/<slug:course_slug>/quizzes/', views.course_quizzes, name='course_quizzes'),
    path('<int:quiz_id>/attempts/', views.quiz_attempts, name='attempts'),
    path('<int:quiz_id>/attempt/<int:attempt_id>/question/<int:question_index>/', views.question_view, name='question'),
    path('<int:quiz_id>/attempt/<int:attempt_id>/question/<int:question_index>/save/', views.save_answer, name='save_answer'),
    
    # Instructor quiz management
    path('create/', views.select_course_for_quiz, name='select_course'),  # New URL for course selection
    path('create/<slug:course_slug>/', views.create_quiz, name='create'),
    path('<int:quiz_id>/edit/', views.edit_quiz, name='edit'),
    path('<int:quiz_id>/delete/', views.delete_quiz, name='delete'),  # New URL for quiz deletion
    path('<int:quiz_id>/questions/add/', views.add_question, name='add_question'),
    path('<int:quiz_id>/questions/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('<int:quiz_id>/results/<int:attempt_id>/', views.quiz_results, name='results'),
    
    # Quiz attempts history
    path('attempts/', views.quiz_attempts_list, name='attempts'),
]
