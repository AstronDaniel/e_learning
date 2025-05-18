from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import uuid
from django.utils import timezone

class Category(models.Model):
    """
    Course category model for organizing courses by subject matter.
    
    Attributes:
        name: The name of the category
        slug: URL-friendly version of the name
        description: Optional detailed description of the category
        icon: Font awesome icon class for visual representation
        is_active: Boolean indicating if the category is active
        created_at: Timestamp when the category was created
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class (e.g., fa-book)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('courses:category', kwargs={'slug': self.slug})


class Course(models.Model):
    """
    Course model representing a course in the e-learning platform.
    
    Attributes:
        title: The title of the course
        slug: URL-friendly version of the title
        description: Detailed description of the course
        instructor: User who created/instructs the course
        category: Category to which the course belongs
        image: Course cover image
        price: Cost of the course (0 for free courses)
        level: Difficulty level of the course
        duration: Estimated duration to complete the course (in hours)
        prerequisites: Optional prerequisites for taking the course
        syllabus: Detailed syllabus/outline of the course
        is_featured: Boolean indicating if the course is featured
        is_published: Boolean indicating if the course is published and visible
        created_at: Timestamp when the course was created
        updated_at: Timestamp when the course was last updated
    """
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all_levels', 'All Levels')
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    image = models.ImageField(upload_to='courses/%Y/%m/', blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all_levels')
    duration = models.PositiveIntegerField(help_text="Estimated duration in hours")
    prerequisites = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # If slug already exists, append a unique identifier
            if Course.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})
    
    @property
    def enrollment_count(self):
        """Returns the number of students enrolled in the course"""
        return self.enrollments.count()
    
    @property
    def rating_average(self):
        """Calculate the average rating for the course"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_level_badge_class(self):
        """Returns CSS class for the level badge based on the level"""
        level_classes = {
            'beginner': 'bg-success',
            'intermediate': 'bg-warning',
            'advanced': 'bg-danger',
            'all_levels': 'bg-info'
        }
        return level_classes.get(self.level, 'bg-secondary')
    
    @property
    def unanswered_discussions_count(self):
        """Returns the number of discussions in the course that have no replies"""
        return self.discussions.filter(replies__isnull=True).count()


class Lesson(models.Model):
    """
    Lesson model representing a single lesson within a course.
    
    Attributes:
        course: The course to which the lesson belongs
        title: The title of the lesson
        content: The content/body of the lesson
        order: Order position in the course
        video_url: Optional URL to a video for the lesson
        duration: Duration of the lesson in minutes
        is_free: Boolean indicating if the lesson is free (preview)
        created_at: Timestamp when the lesson was created
        updated_at: Timestamp when the lesson was last updated
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=0)
    is_free = models.BooleanField(default=False, help_text="Is this a preview lesson?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    def get_absolute_url(self):
        return reverse('courses:lesson', kwargs={'course_slug': self.course.slug, 'lesson_id': self.id})
        
    def get_youtube_embed_url(self):
        """
        Converts a regular YouTube URL to an embeddable URL.
        Handles both youtube.com/watch?v= and youtu.be/ formats.
        
        Returns:
            A YouTube embed URL or None if the URL is not a YouTube URL
        """
        import re
        if not self.video_url:
            return None
            
        # Handle youtu.be format
        youtube_short_pattern = re.compile(r'youtu\.be\/([a-zA-Z0-9_-]+)')
        match = youtube_short_pattern.search(self.video_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
            
        # Handle youtube.com/watch?v= format
        youtube_long_pattern = re.compile(r'youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)')
        match = youtube_long_pattern.search(self.video_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
            
        # Return the original URL if it's not a YouTube URL
        return self.video_url


class CourseResource(models.Model):
    """
    Course resource model for files and materials associated with a course.
    
    Attributes:
        course: The course to which the resource belongs
        title: The title of the resource
        file: The actual file resource
        url: Optional external URL if the resource is not a file
        resource_type: Type of the resource (PDF, Video, etc.)
        created_at: Timestamp when the resource was created
    """
    RESOURCE_TYPE_CHOICES = (
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('link', 'External Link'),
        ('other', 'Other')
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_resources/%Y/%m/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, default='document')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def clean(self):
        """Validate that at least one of file or URL is provided"""
        from django.core.exceptions import ValidationError
        if not self.file and not self.url:
            raise ValidationError("Either a file or a URL must be provided.")


class CourseReview(models.Model):
    """
    Course review model for student reviews and ratings of courses.
    
    Attributes:
        course: The course being reviewed
        user: The user who wrote the review
        rating: Numeric rating from 1-5
        comment: Review text content
        created_at: Timestamp when the review was created
        updated_at: Timestamp when the review was last updated
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'user']  # One review per user per course
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.course.title}"
