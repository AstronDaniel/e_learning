# Coding Standards

This document outlines the coding standards and style guidelines for the E-Learning Platform project.

## Python Coding Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some project-specific adaptations.

### General Guidelines

- Use 4 spaces for indentation, not tabs
- Maximum line length is 100 characters
- Use UTF-8 as the source file encoding
- Use `snake_case` for variable and function names
- Use `CamelCase` for class names
- Use `UPPER_CASE` for constants

### Imports

Organize imports into these groups separated by a blank line:
1. Standard library imports
2. Django imports
3. Third-party app imports
4. Local application imports

Example:
```python
import os
import json
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Course
from users.models import Profile
```

### Docstrings

Use triple double quotes for docstrings following the Google style:

```python
def function_with_types_in_docstring(param1, param2):
    """Example function with docstring.

    This is an example of a function docstring that conforms
    to the Google Python Style Guide.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: The return value. True for success, False otherwise.

    Raises:
        ValueError: If param1 is negative.
    """
    if param1 < 0:
        raise ValueError("param1 must be positive")
    return True
```

### Models

- Each field should be on its own line with a comment
- Add a docstring explaining the model's purpose
- Use verbose_name and help_text for better admin interface

Example:
```python
class Course(models.Model):
    """
    Represents a course in the e-learning system.
    
    This model stores information about courses offered on the platform.
    """
    title = models.CharField(
        max_length=200, 
        verbose_name=_("Course Title"),
        help_text=_("The title of the course")
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("Instructor")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
    
    def __str__(self):
        return self.title
```

## Django Specific Guidelines

### URLs

- Use named URLs for all paths
- Group URLs by functionality
- Include app_name for namespacing

Example:
```python
from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="list"),
    path("<slug:slug>/", views.course_detail, name="detail"),
    path("<slug:slug>/enroll/", views.course_enroll, name="enroll"),
]
```

### Templates

- Use template inheritance with a base template
- Organize templates in directories matching app names
- Use meaningful block names

Example:
```html
{% extends "base.html" %}

{% block title %}Course List{% endblock %}

{% block content %}
<div class="container">
    <h1>Available Courses</h1>
    {% for course in courses %}
        {% include "courses/includes/course_card.html" %}
    {% empty %}
        <p>No courses available.</p>
    {% endfor %}
</div>
{% endblock %}
```

### Views

- Use class-based views when appropriate
- Keep view logic focused on presentation
- Move complex business logic to services or models

### Forms

- Use form classes instead of processing request.POST directly
- Use model forms when working with models
- Add validation methods as needed

## JavaScript Coding Style

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ES6 features where supported
- Add comments for complex logic

## CSS/SCSS Guidelines

- Use BEM (Block Element Modifier) methodology
- Organize CSS by component
- Use variables for colors, spacing, and other repeated values

## Testing Guidelines

- Write tests for all new features
- Aim for high test coverage
- Use pytest-style assertions when possible
- Use factories for creating test data

## Tools and Enforcement

We use the following tools to enforce code quality:

- **Black** - Code formatting
- **flake8** - Linting
- **isort** - Import sorting
- **pylint** - Static analysis
- **bandit** - Security linting

Configure your editor to use these tools or run them before committing.
