"""
Core views for the e-learning platform.

This module contains the main views for the platform, including the home page and search functionality.
"""
from django.shortcuts import render
from django.db.models import Q
from courses.models import Course

def home_view(request):
    """
    Display the home page with featured courses, statistics, and promotional content.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered home page template with context data
    """
    # Get featured courses (limit to 6)
    featured_courses = Course.objects.filter(is_featured=True)[:6]
    
    # Count total courses
    total_courses = Course.objects.count()
    
    # Count total enrolled students (unique users with enrollments)
    from django.contrib.auth.models import User
    from users.models import Enrollment
    from django.db.models import Count
    
    # Count unique users who have at least one enrollment
    total_students = User.objects.filter(enrollments__isnull=False).distinct().count()
    
    # Count total completed courses (certificates earned)
    total_certificates = Enrollment.objects.filter(completed=True).count()
    
    # Context dictionary with data for the template
    context = {
        'featured_courses': featured_courses,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_certificates': total_certificates,
        'page_title': 'Home - Modern Learning for Everyone',
    }
    
    return render(request, 'home.html', context)

def search_view(request):
    """
    Search courses by keyword in title, description, or instructor name.
    
    Args:
        request: The HTTP request object with 'q' parameter
        
    Returns:
        Rendered search results page with matching courses
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search in course title, description, and instructor's name
        results = Course.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(instructor__username__icontains=query)
        ).distinct()
    
    context = {
        'query': query,
        'results': results,
        'result_count': len(results),
        'page_title': f'Search Results for "{query}"',
    }
    
    return render(request, 'search_results.html', context)
