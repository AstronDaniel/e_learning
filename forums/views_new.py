# Basic views for forums app
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q

from .models import Discussion, Reply, DiscussionTag, DiscussionTagging, Notification
from courses.models import Course
from users.models import Enrollment

# Just implement one simple view to test if the import issue is resolved
def test_view(request):
    return JsonResponse({"status": "ok"})

@login_required
def course_discussions(request, course_slug):
    """View for listing all discussions in a course."""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled or is the instructor
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    if not (is_instructor or is_enrolled):
        messages.error(request, "You must be enrolled in this course to access the forum.")
        return redirect('courses:detail', slug=course_slug)
    
    # Get discussions with filters
    discussions = Discussion.objects.filter(course=course)
    
    # Apply filters
    filter_type = request.GET.get('filter')
    if filter_type == 'mine':
        discussions = discussions.filter(user=request.user)
    elif filter_type == 'unsolved':
        discussions = discussions.filter(replies__is_solution=False).distinct()
    elif filter_type == 'unanswered':
        discussions = discussions.filter(replies__isnull=True)
    
    # Apply search query
    search_query = request.GET.get('q')
    if search_query:
        discussions = discussions.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Filter by tag
    tag_slug = request.GET.get('tag')
    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(DiscussionTag, slug=tag_slug)
        discussions = discussions.filter(taggings__tag=active_tag)
    
    # Get all available tags for this course's discussions
    tags = DiscussionTag.objects.filter(
        taggings__discussion__course=course
    ).distinct()
    
    context = {
        'course': course,
        'discussions': discussions,
        'filter_type': filter_type,
        'search_query': search_query,
        'tags': tags,
        'active_tag': active_tag,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'forums/course_discussions.html', context)
