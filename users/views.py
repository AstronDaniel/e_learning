from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from .models import Profile, Enrollment
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomAuthenticationForm

def register(request):
    """View for user registration with role selection."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save()
            
            # Set the role (instructor status) in the profile
            is_instructor = form.cleaned_data.get('role') == 'True'  # Convert string to boolean
            profile = Profile.objects.get(user=user)
            profile.is_instructor = is_instructor
            profile.save()
            
            # Authenticate and log in the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            role_name = "Instructor" if is_instructor else "Student"
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created as {role_name} for {username}! You are now logged in.')
                return redirect('users:dashboard')  # Redirect to dashboard after registration
            else:
                messages.success(request, f'Account created as {role_name} for {username}! You can now log in.')
                return redirect('users:login')
        else:
            # Form is not valid, error messages will be displayed
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view to handle remember me functionality."""
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        
        if not remember_me:
            # Set session expiry to 0 if remember_me is not checked
            self.request.session.set_expiry(0)
            # Set session as modified to force data updates/cookie to be saved
            self.request.session.modified = True
            
        # Call the parent form_valid method to properly authenticate and login
        response = super().form_valid(form)
        
        messages.success(self.request, 'Login successful. Welcome back!')
        return response


@login_required
def profile(request):
    """View for user profile management."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'page_title': 'My Profile'
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def update_avatar(request):
    """View for updating the user's profile avatar via AJAX."""
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile = request.user.profile
        profile.avatar = request.FILES['avatar']
        profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def dashboard(request):
    """View for user dashboard showing enrollments and progress."""
    # Get user's enrollments
    enrollments = Enrollment.objects.filter(user=request.user).order_by('-date_enrolled')
    
    # Calculate some stats
    completed_courses = enrollments.filter(completed=True).count()
    in_progress_courses = enrollments.filter(completed=False).count()
    
    context = {
        'enrollments': enrollments,
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'page_title': 'My Dashboard'
    }
    
    return render(request, 'users/dashboard.html', context)
