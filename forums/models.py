from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

class Discussion(models.Model):
    """
    Discussion model representing a forum thread within a course.
    
    Attributes:
        course: The course this discussion belongs to
        title: The title/subject of the discussion
        slug: URL-friendly version of the title
        user: The user who created the discussion
        content: The main content/body of the discussion
        date_posted: When the discussion was created
        date_updated: When the discussion was last updated
        is_pinned: Whether the discussion is pinned to the top
        is_closed: Whether the discussion is closed for new replies
        views: Count of how many times the discussion has been viewed
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()    
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-date_posted']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forums:discussion_detail', kwargs={'course_slug': self.course.slug, 'discussion_slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    @property
    def comment_count(self):
        """Returns the number of comments in the discussion."""
        return self.comments.count()
    
    @property
    def last_comment(self):
        """Returns the most recent comment in the discussion."""
        return self.comments.order_by('-date_posted').first()


class Comment(models.Model):
    """
    Comment model representing a reply in a discussion thread.
    
    Attributes:
        discussion: The discussion this comment belongs to
        user: The user who posted the comment
        content: The content/body of the comment
        date_posted: When the comment was posted
        date_updated: When the comment was last updated
        parent: Optional reference to parent comment (for nested replies)
        is_solution: Whether this comment has been marked as the solution
    """
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_solution = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['date_posted']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.discussion.title}"
        
    @property
    def is_edited(self):
        """Check if the comment has been edited."""
        time_difference = self.date_updated - self.date_posted
        # Consider as edited if the difference is more than 1 minute
        return time_difference.total_seconds() > 60


class Notification(models.Model):
    """
    Notification model for forum activity alerts.
    
    Attributes:
        user: The user receiving the notification
        discussion: Optional reference to the relevant discussion
        comment: Optional reference to the relevant comment
        content: The notification message
        date_created: When the notification was created
        is_read: Whether the notification has been read
    """
    NOTIFICATION_TYPES = (
        ('comment', 'New Comment'),
        ('reply', 'Reply to Comment'),
        ('mention', 'User Mention'),
        ('solution', 'Solution Marked')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_notifications')
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='comment')
    content = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.content[:30]}..."
    is_closed = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-date_posted']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the URL for the discussion detail view."""
        return reverse('forums:discussion_detail', kwargs={'course_slug': self.course.slug, 'discussion_slug': self.slug})
    
    @property
    def reply_count(self):
        """Get the number of replies to this discussion."""
        return self.replies.count()
    
    @property
    def last_activity(self):
        """Get the timestamp of the most recent activity (post or reply)."""
        if self.replies.exists():
            latest_reply = self.replies.order_by('-date_posted').first()
            return latest_reply.date_posted
        return self.date_posted
    
    def increment_view_count(self):
        """Increment the view count for this discussion."""
        self.views += 1
        self.save(update_fields=['views'])
    
    def has_solution(self):
        """Check if the discussion has any reply marked as solution."""
        return self.replies.filter(is_solution=True).exists()


class Reply(models.Model):
    """
    Reply model representing a response in a discussion thread.
    
    Attributes:
        discussion: The discussion this reply belongs to
        user: The user who posted the reply
        content: The content/body of the reply
        date_posted: When the reply was posted
        date_updated: When the reply was last edited
        is_solution: Whether this reply has been marked as the solution
        parent: Optional parent reply (for nested replies)
    """
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_solution = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name_plural = "Replies"
        ordering = ['date_posted']
    
    def __str__(self):
        return f"Reply by {self.user.username} on {self.discussion.title}"
    
    def mark_as_solution(self):
        """Mark this reply as the solution to the discussion."""
        # First, unmark any existing solutions
        self.discussion.replies.filter(is_solution=True).update(is_solution=False)
        # Then mark this one as solution
        self.is_solution = True
        self.save()
    
    @property
    def is_edited(self):
        """Check if the reply has been edited."""
        time_difference = self.date_updated - self.date_posted
        # Consider edited if more than 1 minute difference between creation and update
        return time_difference.total_seconds() > 60


class Notification(models.Model):
    """
    Notification model for forum activity notifications.
    
    Attributes:
        user: The user receiving the notification
        sender: The user who triggered the notification
        discussion: The related discussion (optional)
        reply: The related reply (optional)
        message: The notification message content
        date_created: When the notification was created
        is_read: Whether the notification has been read
        notification_type: Type of notification (reply, mention, etc.)
    """
    NOTIFICATION_TYPES = (
        ('reply', 'New Reply'),
        ('mention', 'Mention'),
        ('solution', 'Solution Marked'),
        ('course', 'Course Announcement'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
    
    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()


class DiscussionTag(models.Model):
    """
    DiscussionTag model for categorizing discussions with tags.
    
    Attributes:
        name: The name of the tag
        slug: URL-friendly version of the name
        color: Optional CSS color code for the tag
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#3498db", help_text="Hex color code (e.g. #3498db)")
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# Many-to-Many relationship between Discussion and DiscussionTag
class DiscussionTagging(models.Model):
    """
    DiscussionTagging model representing a tag applied to a discussion.
    
    Attributes:
        discussion: The discussion being tagged
        tag: The tag applied to the discussion
        tagged_by: The user who applied the tag
        date_tagged: When the tag was applied
    """
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='taggings')
    tag = models.ForeignKey(DiscussionTag, on_delete=models.CASCADE, related_name='taggings')
    tagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='taggings')
    date_tagged = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['discussion', 'tag']
    
    def __str__(self):
        return f"{self.discussion.title} tagged with {self.tag.name}"
