from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum, F, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

from courses.models import Course, Lesson
from users.models import Enrollment, User, Profile
from quizzes.models import Quiz, QuizAttempt
from forums.models import Discussion, Reply

@login_required
def dashboard(request):
    """Main instructor dashboard view showing overview of all instructor activities."""
    # Check if user is an instructor
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access the instructor dashboard.")
        return redirect('users:dashboard')
    
    # Get courses taught by this instructor
    courses = Course.objects.filter(instructor=request.user).annotate(
        student_count=Count('enrollments'),
        quiz_count=Count('quizzes'),
        discussion_count=Count('discussions')
    )
    
    # Get recent course activity
    recent_enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).order_by('-date_enrolled')[:10]
      # Get quiz statistics
    recent_quiz_attempts = QuizAttempt.objects.filter(
        quiz__course__instructor=request.user,
        score__isnull=False  # Use score instead of completed_at to find completed attempts
    ).order_by('-started_at')[:10]  # Order by started_at instead of completed_at
    
    quiz_performance = QuizAttempt.objects.filter(
        quiz__course__instructor=request.user,
        score__isnull=False  # Use score instead of completed_at to find completed attempts
    ).aggregate(
        avg_score=Avg('score'),
        total_attempts=Count('id')
    )
    
    # Get forum activity
    recent_discussions = Discussion.objects.filter(
        course__instructor=request.user
    ).order_by('-date_posted')[:5]
    
    # Calculate course completion rates
    for course in courses:
        total_students = course.student_count
        if total_students > 0:
            completed_students = Enrollment.objects.filter(
                course=course, completed=True
            ).count()
            course.completion_rate = (completed_students / total_students) * 100
        else:
            course.completion_rate = 0
    
    context = {
        'courses': courses,
        'recent_enrollments': recent_enrollments,
        'recent_quiz_attempts': recent_quiz_attempts,
        'quiz_performance': quiz_performance,
        'recent_discussions': recent_discussions,
        'total_students': Enrollment.objects.filter(course__instructor=request.user).count(),
        'total_courses': courses.count(),
        'total_quizzes': Quiz.objects.filter(course__instructor=request.user).count(),
        'total_discussions': Discussion.objects.filter(course__instructor=request.user).count(),
    }
    
    return render(request, 'instructor/dashboard.html', context)

@login_required
def courses_list(request):
    """View for instructors to manage all their courses."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    # Get all courses with stats
    courses = Course.objects.filter(instructor=request.user).annotate(
        student_count=Count('enrollments'),
        lesson_count=Count('lessons'),
        quiz_count=Count('quizzes')
    ).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter == 'published':
        courses = courses.filter(is_published=True)
    elif status_filter == 'draft':
        courses = courses.filter(is_published=False)
    
    context = {
        'courses': courses,
        'status_filter': status_filter
    }
    
    return render(request, 'instructor/courses_list.html', context)

@login_required
def course_detail(request, course_slug):
    """Detailed view of a course for instructor management."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    quizzes = Quiz.objects.filter(course=course)
    
    # Get enrollment data
    enrollments = Enrollment.objects.filter(course=course)
    enrollment_stats = {
        'total': enrollments.count(),
        'completed': enrollments.filter(completed=True).count(),
        'in_progress': enrollments.filter(completed=False).count(),
    }
    
    # Recent activity
    recent_enrollments = enrollments.order_by('-date_enrolled')[:5]
    recent_completions = enrollments.filter(completed=True).order_by('-completion_date')[:5]
    
    context = {
        'course': course,
        'lessons': lessons,
        'quizzes': quizzes,
        'enrollment_stats': enrollment_stats,
        'recent_enrollments': recent_enrollments,
        'recent_completions': recent_completions,
    }
    
    return render(request, 'instructor/course_detail.html', context)

@login_required
def lessons_list(request, course_slug):
    """View for managing lessons in a specific course."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'lessons': lessons,
    }
    
    return render(request, 'instructor/lessons_list.html', context)

@login_required
def student_list(request, course_slug):
    """View for managing students enrolled in a specific course."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('user')
    
    # Calculate progress for each enrollment
    for enrollment in enrollments:
        total_lessons = course.lessons.count()
        if total_lessons > 0:
            completed_lessons = enrollment.completed_lessons.count()
            enrollment.progress_percent = (completed_lessons / total_lessons) * 100
        else:
            enrollment.progress_percent = 0
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    
    return render(request, 'instructor/student_list.html', context)

@login_required
def analytics_overview(request):
    """View showing analytics across all courses."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    # Get all courses taught by this instructor
    courses = Course.objects.filter(instructor=request.user)
    
    # Overall enrollment stats
    total_enrollments = Enrollment.objects.filter(course__in=courses).count()
    completed_enrollments = Enrollment.objects.filter(course__in=courses, completed=True).count()
    
    # Calculate average course rating
    avg_rating = courses.aggregate(avg=Avg('reviews__rating'))['avg'] or 0
    
    # Get enrollment trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    enrollments_by_day = (
        Enrollment.objects.filter(course__in=courses, date_enrolled__gte=thirty_days_ago)
        .extra({'date': "date(date_enrolled)"})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    context = {
        'courses': courses,
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'completion_rate': (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0,
        'avg_rating': avg_rating,
        'enrollments_by_day': enrollments_by_day,
    }
    
    return render(request, 'instructor/analytics_overview.html', context)

@login_required
def course_analytics(request, course_slug):
    """View showing detailed analytics for a specific course."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
    # Enrollment stats
    enrollments = Enrollment.objects.filter(course=course)
    total_enrollments = enrollments.count()
    completed_enrollments = enrollments.filter(completed=True).count()
    
    # Calculate lesson completion rates
    lessons = Lesson.objects.filter(course=course)
    lesson_stats = []
    
    for lesson in lessons:
        completions = lesson.completed_by.count()
        completion_rate = (completions / total_enrollments * 100) if total_enrollments > 0 else 0
        lesson_stats.append({
            'lesson': lesson,
            'completions': completions,
            'completion_rate': completion_rate
        })
    
    # Quiz performance stats
    quizzes = Quiz.objects.filter(course=course)
    quiz_stats = []
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False)
        avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0
        passing_count = attempts.filter(score__gte=quiz.pass_score).count()
        passing_rate = (passing_count / attempts.count() * 100) if attempts.count() > 0 else 0
        
        quiz_stats.append({
            'quiz': quiz,
            'attempts': attempts.count(),
            'avg_score': avg_score,
            'passing_rate': passing_rate
        })
    
    context = {
        'course': course,
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'completion_rate': (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0,
        'lesson_stats': lesson_stats,
        'quiz_stats': quiz_stats,
    }
    
    return render(request, 'instructor/course_analytics.html', context)

@login_required
def quizzes_list(request):
    """View for instructors to manage all their quizzes."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    # Get courses and their quizzes
    courses = Course.objects.filter(instructor=request.user).prefetch_related('quizzes')
    
    # Organize quizzes by course
    courses_with_quizzes = []
    for course in courses:
        quizzes = Quiz.objects.filter(course=course).annotate(
            attempt_count=Count('attempts'),
            avg_score=Avg('attempts__score')
        )
        
        courses_with_quizzes.append({
            'course': course,
            'quizzes': quizzes
        })
    
    context = {
        'courses_with_quizzes': courses_with_quizzes,
    }
    
    return render(request, 'instructor/quizzes_list.html', context)

@login_required
def quiz_results_overview(request, quiz_id):
    """View for seeing detailed results of a specific quiz."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, course__instructor=request.user)
    attempts = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False).select_related('user')
    
    # Calculate quiz statistics
    stats = {
        'total_attempts': attempts.count(),
        'avg_score': attempts.aggregate(avg=Avg('score'))['avg'] or 0,
        'passing_count': attempts.filter(score__gte=quiz.passing_score).count(),
    }
    
    if stats['total_attempts'] > 0:
        stats['passing_rate'] = (stats['passing_count'] / stats['total_attempts']) * 100
    else:
        stats['passing_rate'] = 0
    
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'stats': stats,
        'course': quiz.course,
    }
    
    return render(request, 'instructor/quiz_results.html', context)

@login_required
def forums_list(request):
    """View for instructors to manage forums across all their courses."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    # Get all courses taught by this instructor
    courses = Course.objects.filter(instructor=request.user)
    
    # Get forum stats for each course
    courses_with_forums = []
    for course in courses:
        discussions = Discussion.objects.filter(course=course)
        stats = {
            'total_discussions': discussions.count(),
            'total_replies': Reply.objects.filter(discussion__course=course).count(),
            'unanswered': discussions.annotate(reply_count=Count('replies')).filter(reply_count=0).count(),
            'pinned': discussions.filter(is_pinned=True).count(),
        }
        
        courses_with_forums.append({
            'course': course,
            'stats': stats,
            'recent_discussions': discussions.order_by('-date_posted')[:3]
        })
    
    context = {
        'courses_with_forums': courses_with_forums,
    }
    
    return render(request, 'instructor/forums_list.html', context)

@login_required
def forum_moderation(request, course_slug):
    """View for moderating forums in a specific course."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    discussions = Discussion.objects.filter(course=course).annotate(
        reply_count=Count('replies')
    ).order_by('-is_pinned', '-date_posted')
    
    # Filter discussions if requested
    filter_type = request.GET.get('filter')
    if filter_type == 'unanswered':
        discussions = discussions.filter(reply_count=0)
    elif filter_type == 'pinned':
        discussions = discussions.filter(is_pinned=True)
    elif filter_type == 'closed':
        discussions = discussions.filter(is_closed=True)
    
    context = {
        'course': course,
        'discussions': discussions,
        'filter_type': filter_type,
    }
    
    return render(request, 'instructor/forum_moderation.html', context)

@login_required
def add_lesson(request, course_slug):
    """View for adding a new lesson to a course."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        order = request.POST.get('order')
        video_url = request.POST.get('video_url')
        duration = request.POST.get('duration')
        is_free = request.POST.get('is_free') == 'on'
        
        # Create lesson
        lesson = Lesson.objects.create(
            course=course,
            title=title,
            content=content,
            order=int(order) if order else 1,
            video_url=video_url,
            duration=int(duration) if duration else 0,
            is_free=is_free
        )
        
        messages.success(request, f"Lesson '{title}' has been added successfully!")
        return redirect('instructor:lessons', course_slug=course_slug)
    
    # Get the next available order number
    next_order = Lesson.objects.filter(course=course).count() + 1
    
    context = {
        'course': course,
        'next_order': next_order
    }
    
    return render(request, 'instructor/add_lesson.html', context)

@login_required
def edit_lesson(request, course_slug, lesson_id):
    """View for editing an existing lesson."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        order = request.POST.get('order')
        video_url = request.POST.get('video_url')
        duration = request.POST.get('duration')
        is_free = request.POST.get('is_free') == 'on'
        
        # Update lesson
        lesson.title = title
        lesson.content = content
        lesson.order = int(order) if order else 1
        lesson.video_url = video_url
        lesson.duration = int(duration) if duration else 0
        lesson.is_free = is_free
        lesson.save()
        
        messages.success(request, f"Lesson '{title}' has been updated successfully!")
        return redirect('instructor:lessons', course_slug=course_slug)
    
    context = {
        'course': course,
        'lesson': lesson
    }
    
    return render(request, 'instructor/edit_lesson.html', context)

@login_required
def delete_lesson(request, course_slug, lesson_id):
    """View for deleting a lesson."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('users:dashboard')
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        
        # Reorder remaining lessons to ensure continuity
        remaining_lessons = Lesson.objects.filter(course=course).order_by('order')
        for i, l in enumerate(remaining_lessons, 1):
            if l.order != i:
                l.order = i
                l.save()
        
        messages.success(request, f"Lesson '{lesson_title}' has been deleted successfully!")
    
    return redirect('instructor:lessons', course_slug=course_slug)

@login_required
def get_lesson_details(request, course_slug, lesson_id):
    """View for getting lesson details via AJAX for editing."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Return lesson data as JSON
    data = {
        'success': True,
        'lesson': {
            'id': lesson.id,
            'title': lesson.title,
            'content': lesson.content,
            'order': lesson.order,
            'video_url': lesson.video_url or '',
            'duration': lesson.duration,
            'is_free': lesson.is_free
        }
    }
    
    return JsonResponse(data)

@login_required
def reorder_lessons(request, course_slug):
    """View for reordering lessons via AJAX."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            orders = data.get('orders', [])
            
            # Update each lesson order
            for item in orders:
                lesson_id = item.get('lesson_id')
                new_order = item.get('order')
                
                lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
                lesson.order = new_order
                lesson.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
