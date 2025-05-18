from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course
from PIL import Image
import os

class Profile(models.Model):
    """
    User profile model that extends the built-in Django User model.
    
    This model stores additional information about users beyond the basic
    authentication data stored in the Django User model.
    
    Attributes:
        user: One-to-one relationship with Django's User model
        avatar: Profile picture for the user
        bio: Short description/biography of the user
        date_of_birth: User's date of birth
        phone_number: Contact phone number
        website: Personal or professional website URL
        address: Physical address
        is_instructor: Boolean indicating if the user is an instructor
        social_linkedin: LinkedIn profile URL
        social_twitter: Twitter profile URL
        social_github: GitHub profile URL
        email_notifications: Whether to send email notifications
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='data:image/jpeg;base64,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', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_instructor = models.BooleanField(default=False)
    
    # Social media profiles
    social_linkedin = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_github = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        """Override the save method to resize the profile picture."""
        super().save(*args, **kwargs)
        
        if self.avatar:
            img_path = self.avatar.path
            if os.path.exists(img_path):
                img = Image.open(img_path)
                
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(img_path)
    
    @property
    def full_name(self):
        """Returns the user's full name or username if not available."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    @property
    def courses_enrolled(self):
        """Returns the number of courses the user is enrolled in."""
        return self.user.enrollments.count()
    
    @property
    def courses_completed(self):
        """Returns the number of courses the user has completed."""
        return self.user.enrollments.filter(completed=True).count()


class Enrollment(models.Model):
    """
    Enrollment model representing a student's enrollment in a course.
    
    This model tracks when a user enrolls in a course, their progress, completion
    status, and related information.
    
    Attributes:
        user: The user who is enrolled in the course
        course: The course in which the user is enrolled
        date_enrolled: Date when the user enrolled in the course
        completed: Boolean indicating if the course has been completed
        completion_date: Date when the course was completed (if applicable)
        progress: Percentage of course completion (0-100)
        last_accessed: Timestamp of when the user last accessed the course
    """    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    completed_lessons = models.ManyToManyField('courses.Lesson', related_name='completed_by', blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0, help_text="Percentage of course completion (0-100)")
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']  # A user can enroll in a course only once
    
    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
    
    def mark_as_completed(self):
        """Mark the enrollment as completed and set the completion date."""
        from django.utils import timezone
        self.completed = True
        self.completion_date = timezone.now()
        self.progress = 100
        self.save()


class LessonProgress(models.Model):
    """
    Lesson progress model to track a user's progress through lessons.
    
    This model stores information about which lessons a user has completed
    within a course they are enrolled in.
    
    Attributes:
        enrollment: The enrollment record this progress is related to
        lesson: The specific lesson
        is_completed: Boolean indicating if the lesson has been completed
        completed_date: When the lesson was completed
        notes: User's personal notes for this lesson
    """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
    
    def __str__(self):
        return f"{self.enrollment.user.username}'s progress on {self.lesson.title}"
    
    def mark_as_completed(self):
        """Mark the lesson as completed and update progress."""
        from django.utils import timezone
        if not self.is_completed:
            self.is_completed = True
            self.completed_date = timezone.now()
            self.save()
            
            # Update overall course progress
            self._update_course_progress()
    
    def _update_course_progress(self):
        """Update the overall course progress based on completed lessons."""
        enrollment = self.enrollment
        total_lessons = enrollment.course.lessons.count()
        if total_lessons > 0:
            completed_lessons = enrollment.lesson_progresses.filter(is_completed=True).count()
            progress = int((completed_lessons / total_lessons) * 100)
            enrollment.progress = progress
            
            # Mark course as completed if all lessons are done
            if progress >= 100:
                enrollment.mark_as_completed()
            else:
                enrollment.save()


# Signal to create a Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a new User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when the User is saved."""
    instance.profile.save()
