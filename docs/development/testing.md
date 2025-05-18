# Testing Guidelines

This document provides guidelines for testing the E-Learning Platform.

## Testing Strategy

Our testing strategy follows a pyramid approach:

1. **Unit Tests**: Test individual functions and methods in isolation
2. **Integration Tests**: Test interactions between components
3. **Functional Tests**: Test complete features from a user's perspective
4. **End-to-End Tests**: Test the entire system from start to finish

## Test Types

### Unit Tests

Unit tests focus on testing individual functions, methods, or classes in isolation. These tests should be fast, reliable, and comprehensive.

Example of a unit test:

```python
from django.test import TestCase
from courses.models import Course

class CourseModelTest(TestCase):
    """Test suite for Course model."""
    
    def setUp(self):
        self.course = Course.objects.create(
            title="Test Course",
            description="This is a test course",
            category="Programming"
        )
    
    def test_course_title(self):
        """Test that the course title is correct."""
        self.assertEqual(self.course.title, "Test Course")
    
    def test_course_str(self):
        """Test the string representation of the course."""
        self.assertEqual(str(self.course), "Test Course")
```

### Integration Tests

Integration tests verify that different components work together correctly. These tests focus on the interaction points between components.

Example of an integration test:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from courses.models import Course
from users.models import Enrollment

class EnrollmentIntegrationTest(TestCase):
    """Test enrollment functionality between users and courses."""
    
    def setUp(self):
        # Create a user and a course
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="This is a test course",
            category="Programming"
        )
    
    def test_user_enrollment(self):
        """Test that a user can enroll in a course."""
        # Create an enrollment
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )
        
        # Check if the enrollment was created correctly
        self.assertTrue(Enrollment.objects.filter(
            user=self.user, 
            course=self.course
        ).exists())
        
        # Check if the relationship is maintained in both directions
        self.assertIn(self.course, self.user.enrolled_courses.all())
        self.assertIn(self.user, self.course.enrolled_students.all())
```

### Functional Tests

Functional tests verify that features work correctly from a user's perspective. These tests interact with the application through views and forms.

Example of a functional test:

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from courses.models import Course

class CourseEnrollmentFunctionalTest(TestCase):
    """Test the course enrollment feature from a user perspective."""
    
    def setUp(self):
        # Create a user and a course
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="This is a test course",
            category="Programming"
        )
    
    def test_enrollment_workflow(self):
        """Test the complete enrollment workflow."""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")
        
        # Access the course detail page
        response = self.client.get(
            reverse("courses:detail", kwargs={"pk": self.course.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Submit the enrollment form
        response = self.client.post(
            reverse("courses:enroll", kwargs={"pk": self.course.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirected after success
        
        # Verify enrollment was created
        self.assertTrue(
            self.user.enrollment_set.filter(course=self.course).exists()
        )
```

### End-to-End Tests

End-to-end tests simulate real user scenarios across the entire application. We use Selenium for these tests.

Example of an end-to-end test:

```python
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from courses.models import Course

class StudentEnrollmentTest(StaticLiveServerTestCase):
    """Full end-to-end test for the student enrollment process."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="This is a test course",
            category="Programming"
        )
    
    def test_student_enrollment(self):
        """Test student login and course enrollment."""
        # Open the login page
        self.selenium.get(f"{self.live_server_url}/login/")
        
        # Fill in the login form
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("testuser")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("testpass123")
        
        # Submit the form
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Navigate to the course detail page
        self.selenium.get(
            f"{self.live_server_url}{reverse('courses:detail', kwargs={'pk': self.course.pk})}"
        )
        
        # Click the enroll button
        self.selenium.find_element(By.ID, "enroll-button").click()
        
        # Wait for redirection and check for success message
        success_message = self.selenium.find_element(By.CLASS_NAME, "alert-success")
        self.assertIn("enrolled successfully", success_message.text)
```

## Testing Tools

### Django Test Client

The Django Test Client is used for simulating HTTP requests in functional tests.

### Factory Boy

We use Factory Boy to create test data with less boilerplate.

Example:
```python
import factory
from django.contrib.auth.models import User
from courses.models import Course

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password")

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    
    title = factory.Sequence(lambda n: f"Course {n}")
    description = "Course description"
    instructor = factory.SubFactory(UserFactory)
```

### Coverage.py

We use Coverage.py to measure test coverage.

Running tests with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML report
```

## Continuous Integration

All tests run automatically on every pull request using GitHub Actions. The workflow includes:

1. Running all tests
2. Measuring test coverage
3. Checking code style with flake8 and black
4. Security scanning with bandit

## Writing Effective Tests

### Best Practices

1. **Isolation**: Tests should not depend on each other
2. **Speed**: Tests should run quickly to enable fast feedback
3. **Determinism**: Tests should always produce the same result
4. **Coverage**: Aim for high test coverage but focus on critical paths
5. **Readability**: Tests serve as documentation, make them clear

### Anti-patterns to Avoid

1. **Testing implementation details**: Focus on behavior, not implementation
2. **Brittle tests**: Tests that break when implementation changes
3. **Slow tests**: Tests that take too long to run
4. **Testing trivial code**: Focus on complex logic and business rules
