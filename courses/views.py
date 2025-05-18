from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.contrib import messages
from .models import Course, Category, Lesson
from users.models import Enrollment
from django.views import View
from django import forms
from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

class CourseListView(ListView):
    """View for listing all available courses."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        """Filter to show only published courses."""
        return Course.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        return context

class CoursesByCategoryView(ListView):
    """View for listing courses by category."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        """Filter courses by the specified category slug."""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Course.objects.filter(category=self.category, is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.category
        return context

class CourseDetailView(DetailView):
    """View for displaying course details."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['lessons'] = course.lessons.all().order_by('order')
        
        # Check if user is enrolled
        if self.request.user.is_authenticated:
            context['is_enrolled'] = course.enrollments.filter(user=self.request.user).exists()
        
        return context

class LessonDetailView(LoginRequiredMixin, DetailView):
    """View for displaying lesson content to enrolled students."""
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    
    def get_object(self):
        """Get the lesson object by course slug and lesson ID."""
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'], course=course)
        return lesson
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        course = lesson.course
        
        # Get previous and next lessons
        all_lessons = list(course.lessons.order_by('order'))
        current_idx = all_lessons.index(lesson)
        
        context['course'] = course
        context['prev_lesson'] = all_lessons[current_idx - 1] if current_idx > 0 else None
        context['next_lesson'] = all_lessons[current_idx + 1] if current_idx < len(all_lessons) - 1 else None
        
        return context


class EnrollCourseView(LoginRequiredMixin, View):
    """View for handling course enrollment."""
    
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        # Check if already enrolled
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.warning(request, f'You are already enrolled in {course.title}.')
        else:
            # Create new enrollment
            enrollment = Enrollment(
                user=request.user,
                course=course,
                date_enrolled=timezone.now()
            )
            enrollment.save()
            messages.success(request, f'Successfully enrolled in {course.title}!')
        
        return redirect('courses:detail', slug=course.slug)


class ReviewForm(forms.Form):
    """Form for submitting course reviews."""
    rating = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(widget=forms.Textarea, required=True)


class ReviewCourseView(LoginRequiredMixin, FormView):
    """View for handling course reviews."""
    form_class = ReviewForm
    
    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.kwargs['slug']})
    
    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        # Check if user is enrolled
        if not Enrollment.objects.filter(user=self.request.user, course=course).exists():
            messages.error(self.request, 'You must be enrolled in this course to review it.')
            return redirect('courses:detail', slug=course.slug)
        
        # Check if user has already reviewed
        if course.reviews.filter(user=self.request.user).exists():
            messages.warning(self.request, 'You have already reviewed this course.')
            return redirect('courses:detail', slug=course.slug)
        
        # Create the review
        course.reviews.create(
            user=self.request.user,
            rating=form.cleaned_data['rating'],
            comment=form.cleaned_data['comment'],
            created_at=timezone.now()
        )
        
        messages.success(self.request, 'Thank you for your review!')
        return super().form_valid(form)


class MarkLessonCompleteView(LoginRequiredMixin, View):
    """View for marking lessons as complete/incomplete."""
    
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'], course=course)
        
        # Check if user is enrolled
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        if 'mark_complete' in request.POST:
            # Add to completed lessons
            enrollment.completed_lessons.add(lesson)
            messages.success(request, f"Lesson '{lesson.title}' marked as complete!")
            
            # Check if all lessons are completed
            all_lessons = course.lessons.all()
            if set(enrollment.completed_lessons.all()) == set(all_lessons):
                enrollment.completed = True
                enrollment.completion_date = timezone.now()
                enrollment.save()
                messages.success(request, f"Congratulations! You've completed the course!")
        
        elif 'mark_incomplete' in request.POST:
            # Remove from completed lessons
            enrollment.completed_lessons.remove(lesson)
            
            # If course was marked as completed, mark it incomplete
            if enrollment.completed:
                enrollment.completed = False
                enrollment.completion_date = None
                enrollment.save()
            
            messages.success(request, f"Lesson '{lesson.title}' marked as incomplete.")
        
        # Stay on the same page
        return redirect('courses:lesson', course_slug=course.slug, lesson_id=lesson.id)


class SaveLessonNoteView(LoginRequiredMixin, View):
    """View for saving notes for a specific lesson."""
    
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'], course=course)
        
        # Check if user is enrolled
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        # Get the note content
        note_content = request.POST.get('note_content', '')
        
        # Create or update the note
        from courses.models import LessonNote
        note, created = LessonNote.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'content': note_content}
        )
        
        messages.success(request, "Your notes have been saved.")
        return redirect('courses:lesson', course_slug=course.slug, lesson_id=lesson.id)


class CourseCertificateView(LoginRequiredMixin, View):
    """View for handling course certificates."""
    
    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        # Check if user is enrolled and has completed the course
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course, completed=True)
        
        context = {
            'course': course,
            'enrollment': enrollment
        }
        
        return render(request, 'courses/course_certificate.html', context)

class InstructorCoursesView(LoginRequiredMixin, ListView):
    """View for instructors to manage their courses."""
    model = Course
    template_name = 'courses/instructor_courses.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        """Filter to show only the instructor's courses."""
        return Course.objects.filter(instructor=self.request.user)
    

class CreateCourseView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for instructors to create new courses."""
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['title', 'category', 'description', 'image', 'level', 'duration', 'prerequisites', 'syllabus', 'is_published']
    
    def form_valid(self, form):
        # Set the instructor to the current user
        form.instance.instructor = self.request.user
        
        # Generate slug from title
        form.instance.slug = slugify(form.instance.title)
        
        # Save the form
        response = super().form_valid(form)
        
        # Add success message
        messages.success(self.request, f"Course '{form.instance.title}' created successfully!")
        
        return response
    
    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.object.slug})
    
    def test_func(self):
        # Check if the user is an instructor
        return hasattr(self.request.user, 'profile') and self.request.user.profile.is_instructor

@login_required
@require_POST
def create_category(request):
    """View for creating a new category via AJAX."""
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description', '')
        icon = data.get('icon', '')
        
        # Create the new category
        category = Category.objects.create(
            name=name,
            description=description,
            icon=icon
        )
        
        # Return success response with the new category data
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            }
        })
    except Exception as e:
        # Return error response
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
