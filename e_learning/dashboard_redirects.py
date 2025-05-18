from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def dashboard_redirect(request):
    """
    Redirects users to the appropriate dashboard based on their role.
    Instructors go to the instructor dashboard, students to the student dashboard.
    """
    # Check if user has a profile and is an instructor
    if hasattr(request.user, 'profile') and request.user.profile.is_instructor:
        print("Instructor dashboard")
        return redirect('instructor:dashboard')
    else:
        print("Student dashboard")
        return redirect('users:dashboard')
