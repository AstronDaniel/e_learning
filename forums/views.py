from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.text import slugify

from .models import Discussion, Reply, DiscussionTag, DiscussionTagging, Notification
from courses.models import Course
from users.models import Enrollment

# Simple test view that doesn't depend on any models or complex logic
def test_view(request):
    return JsonResponse({"status": "ok", "message": "Forums app is working"})

@login_required
def forums_index(request):
    """View for listing all courses with active forums."""
    # Get courses where the user is enrolled or is the instructor
    user_courses = Course.objects.filter(
        Q(instructor=request.user) | 
        Q(enrollments__user=request.user)
    ).distinct()
    
    # Annotate courses with discussion count
    user_courses = user_courses.annotate(discussion_count=Count('discussions'))
    
    # Get recent discussions across all courses
    recent_discussions = Discussion.objects.filter(
        course__in=user_courses
    ).order_by('-date_posted')[:5]
    
    # Get notification count for the user
    unread_notifications_count = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).count()
    
    context = {
        'courses': user_courses,
        'recent_discussions': recent_discussions,
        'unread_notifications_count': unread_notifications_count,
    }
    
    return render(request, 'forums/forums_index.html', context)

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

@login_required
def discussion_detail(request, course_slug, discussion_slug):
    """View for displaying a discussion and its replies."""
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    
    # Check if user is enrolled or is the instructor
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    if not (is_instructor or is_enrolled):
        messages.error(request, "You must be enrolled in this course to access the forum.")
        return redirect('courses:detail', slug=course_slug)
    
    # Increment view count (only once per session)
    session_key = f'viewed_discussion_{discussion.id}'
    if not request.session.get(session_key, False):
        discussion.increment_view_count()
        request.session[session_key] = True
    
    # Mark notifications related to this discussion as read
    if request.user.is_authenticated:
        Notification.objects.filter(
            user=request.user,
            discussion=discussion,
            is_read=False
        ).update(is_read=True)
    
    # Get replies with parent=None (top-level replies only)
    replies = discussion.replies.filter(parent__isnull=True).select_related('user')
    
    # Form handling for new reply
    if request.method == 'POST' and not discussion.is_closed:
        reply_content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if reply_content:
            # Create the reply
            reply = Reply(
                discussion=discussion,
                user=request.user,
                content=reply_content
            )
            
            # Handle reply to another reply
            if parent_id:
                try:
                    parent_reply = Reply.objects.get(id=parent_id, discussion=discussion)
                    reply.parent = parent_reply
                except Reply.DoesNotExist:
                    pass
            
            reply.save()
            
            # Create notifications
            # Notify discussion author if it's not the same user
            if discussion.user != request.user:
                Notification.objects.create(
                    user=discussion.user,
                    sender=request.user,
                    discussion=discussion,
                    reply=reply,
                    message=f"{request.user.username} replied to your discussion: {discussion.title}",
                    notification_type='reply'
                )
            
            # Notify parent reply author if it's a reply to a reply
            if parent_id and reply.parent and reply.parent.user != request.user:
                Notification.objects.create(
                    user=reply.parent.user,
                    sender=request.user,
                    discussion=discussion,
                    reply=reply,
                    message=f"{request.user.username} replied to your comment in: {discussion.title}",
                    notification_type='reply'
                )
            
            messages.success(request, "Your reply has been posted.")
            
            # Redirect to avoid form resubmission
            return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    context = {
        'course': course,
        'discussion': discussion,
        'replies': replies,
        'is_instructor': is_instructor,
        'can_reply': not discussion.is_closed,
        'tags': DiscussionTagging.objects.filter(discussion=discussion).select_related('tag')
    }
    
    return render(request, 'forums/discussion_detail.html', context)

@login_required
def create_discussion(request, course_slug):
    """View for creating a new discussion."""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled or is the instructor
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    if not (is_instructor or is_enrolled):
        messages.error(request, "You must be enrolled in this course to create discussions.")
        return redirect('courses:detail', slug=course_slug)
    
    # Get available tags
    all_tags = DiscussionTag.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tag_ids = request.POST.getlist('tags')
        
        if title and content:
            # Create the discussion
            slug = slugify(title)
            
            # Check if slug already exists and make it unique if needed
            if Discussion.objects.filter(course=course, slug=slug).exists():
                base_slug = slug
                counter = 1
                while Discussion.objects.filter(course=course, slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
            
            discussion = Discussion.objects.create(
                course=course,
                title=title,
                slug=slug,
                content=content,
                user=request.user
            )
            
            # Add tags
            if tag_ids:
                tags = DiscussionTag.objects.filter(id__in=tag_ids)
                for tag in tags:
                    DiscussionTagging.objects.create(
                        discussion=discussion,
                        tag=tag,
                        tagged_by=request.user
                    )
            
            messages.success(request, "Your discussion has been created.")
            return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion.slug)
        else:
            messages.error(request, "Please provide both a title and content for your discussion.")
    
    context = {
        'course': course,
        'tags': all_tags,
    }
    
    return render(request, 'forums/create_discussion.html', context)

@login_required
def edit_discussion(request, course_slug, discussion_slug):
    """View for editing a discussion."""
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    
    # Check if user is the author or an instructor
    if request.user != discussion.user and request.user != course.instructor:
        messages.error(request, "You don't have permission to edit this discussion.")
        return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    # Get current tags
    current_tags = DiscussionTagging.objects.filter(discussion=discussion).values_list('tag_id', flat=True)
    all_tags = DiscussionTag.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tag_ids = request.POST.getlist('tags')
        
        if title and content:
            discussion.title = title
            discussion.content = content
            
            # Only update slug if title changed
            if slugify(title) != discussion.slug:
                new_slug = slugify(title)
                
                # Check if slug already exists and make it unique if needed
                if Discussion.objects.filter(course=course, slug=new_slug).exclude(id=discussion.id).exists():
                    base_slug = new_slug
                    counter = 1
                    while Discussion.objects.filter(course=course, slug=new_slug).exclude(id=discussion.id).exists():
                        new_slug = f"{base_slug}-{counter}"
                        counter += 1
                
                discussion.slug = new_slug
            
            discussion.save()
            
            # Update tags
            # First remove existing tags
            DiscussionTagging.objects.filter(discussion=discussion).delete()
            
            # Then add new tags
            if tag_ids:
                tags = DiscussionTag.objects.filter(id__in=tag_ids)
                for tag in tags:
                    DiscussionTagging.objects.create(
                        discussion=discussion,
                        tag=tag,
                        tagged_by=request.user
                    )
            
            messages.success(request, "Discussion updated successfully.")
            return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion.slug)
        else:
            messages.error(request, "Please provide both a title and content for your discussion.")
    
    context = {
        'course': course,
        'discussion': discussion,
        'tags': all_tags,
        'current_tags': current_tags,
    }
    
    return render(request, 'forums/edit_discussion.html', context)

@login_required
def delete_discussion(request, course_slug, discussion_slug):
    """View for deleting a discussion."""
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    
    # Check if user is the author or an instructor
    if request.user != discussion.user and request.user != course.instructor:
        messages.error(request, "You don't have permission to delete this discussion.")
        return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    if request.method == 'POST':
        discussion.delete()
        messages.success(request, "Discussion deleted successfully.")
        return redirect('forums:course_discussions', course_slug=course_slug)
    
    context = {
        'course': course,
        'discussion': discussion,
    }
    
    return render(request, 'forums/delete_discussion.html', context)

@login_required
def edit_reply(request, course_slug, discussion_slug, reply_id):
    """View for editing a reply."""
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    reply = get_object_or_404(Reply, id=reply_id, discussion=discussion)
    
    # Check if user is the author or an instructor
    if request.user != reply.user and request.user != course.instructor:
        messages.error(request, "You don't have permission to edit this reply.")
        return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            reply.content = content
            reply.save()
            messages.success(request, "Reply updated successfully.")
        else:
            messages.error(request, "Reply content cannot be empty.")
        
        return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    context = {
        'course': course,
        'discussion': discussion,
        'reply': reply,
    }
    
    return render(request, 'forums/edit_reply.html', context)

@login_required
def delete_reply(request, course_slug, discussion_slug, reply_id):
    """View for deleting a reply."""
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    reply = get_object_or_404(Reply, id=reply_id, discussion=discussion)
    
    # Check if user is the author or an instructor
    if request.user != reply.user and request.user != course.instructor:
        messages.error(request, "You don't have permission to delete this reply.")
        return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    if request.method == 'POST':
        reply.delete()
        messages.success(request, "Reply deleted successfully.")
        return redirect('forums:discussion_detail', course_slug=course_slug, discussion_slug=discussion_slug)
    
    context = {
        'course': course,
        'discussion': discussion,
        'reply': reply,
    }
    
    return render(request, 'forums/delete_reply.html', context)

@login_required
def mark_solution(request, course_slug, discussion_slug, reply_id):
    """View for marking a reply as the solution."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    reply = get_object_or_404(Reply, id=reply_id, discussion=discussion)
    
    # Only discussion author or course instructor can mark solutions
    if request.user != discussion.user and request.user != course.instructor:
        return JsonResponse({'error': 'You don\'t have permission to mark solutions'}, status=403)
    
    # If this reply is already a solution, unmark it
    if reply.is_solution:
        reply.is_solution = False
        reply.save()
        return JsonResponse({'status': 'unmarked', 'message': 'Solution unmarked'})
    
    # Otherwise, unmark any existing solutions and mark this one
    discussion.replies.filter(is_solution=True).update(is_solution=False)
    reply.is_solution = True
    reply.save()
    
    # Create notification for reply author if it's not the same user
    if reply.user != request.user:
        Notification.objects.create(
            user=reply.user,
            sender=request.user,
            discussion=discussion,
            reply=reply,
            message=f"Your reply was marked as the solution in: {discussion.title}",
            notification_type='solution'
        )
    
    return JsonResponse({'status': 'marked', 'message': 'Solution marked successfully'})

@login_required
def toggle_closed(request, course_slug, discussion_slug):
    """View for toggling the closed status of a discussion."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    
    # Only discussion author or course instructor can close/open discussions
    if request.user != discussion.user and request.user != course.instructor:
        return JsonResponse({'error': 'You don\'t have permission to close/open this discussion'}, status=403)
    
    discussion.is_closed = not discussion.is_closed
    discussion.save()
    
    status = 'closed' if discussion.is_closed else 'opened'
    return JsonResponse({
        'status': status, 
        'message': f'Discussion {status} successfully'
    })

@login_required
def toggle_pinned(request, course_slug, discussion_slug):
    """View for toggling the pinned status of a discussion."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    course = get_object_or_404(Course, slug=course_slug)
    discussion = get_object_or_404(Discussion, course=course, slug=discussion_slug)
    
    # Only course instructor can pin/unpin discussions
    if request.user != course.instructor:
        return JsonResponse({'error': 'Only instructors can pin/unpin discussions'}, status=403)
    
    discussion.is_pinned = not discussion.is_pinned
    discussion.save()
    
    status = 'pinned' if discussion.is_pinned else 'unpinned'
    return JsonResponse({
        'status': status, 
        'message': f'Discussion {status} successfully'
    })

@login_required
def notifications(request):
    """View for displaying forum notifications."""
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark all as read if requested
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        notifications.update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('forums:notifications')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    
    return render(request, 'forums/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """View for marking a notification as read."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Notification marked as read'
    })

@login_required
def create_tag(request):
    """View for creating a new discussion tag. Admin or instructor only."""
    if not request.user.is_staff and not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        messages.error(request, "Only instructors can create tags.")
        return redirect('forums:notifications')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color', '#3498db')
        
        if name:
            slug = slugify(name)
            
            # Check if tag already exists
            if DiscussionTag.objects.filter(slug=slug).exists():
                messages.error(request, f"A tag with the name '{name}' already exists.")
            else:
                DiscussionTag.objects.create(
                    name=name,
                    slug=slug,
                    color=color
                )
                messages.success(request, f"Tag '{name}' created successfully.")
                
                # Redirect back to referrer or to notifications
                return redirect(request.META.get('HTTP_REFERER', 'forums:notifications'))
        else:
            messages.error(request, "Tag name cannot be empty.")
    
    context = {
        'tags': DiscussionTag.objects.all()
    }
    
    return render(request, 'forums/create_tag.html', context)
