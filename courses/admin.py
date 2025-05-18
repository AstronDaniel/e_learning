from django.contrib import admin
from .models import Category, Course, Lesson, CourseResource, CourseReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'level', 'is_featured', 'is_published', 'created_at']
    list_filter = ['is_featured', 'is_published', 'level', 'category', 'created_at']
    search_fields = ['title', 'description', 'instructor__username', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['instructor']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_free', 'duration']
    list_filter = ['is_free', 'course']
    search_fields = ['title', 'content', 'course__title']
    raw_id_fields = ['course']
    ordering = ['course', 'order']

@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'resource_type', 'created_at']
    list_filter = ['resource_type', 'created_at']
    search_fields = ['title', 'course__title']
    raw_id_fields = ['course']

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment', 'course__title', 'user__username']
    raw_id_fields = ['course', 'user']
