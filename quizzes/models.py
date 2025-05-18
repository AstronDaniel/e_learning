from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Lesson
import uuid
from django.utils import timezone

class Quiz(models.Model):
    """
    Quiz model representing a quiz or assessment for a course.
    
    Attributes:
        title: The title of the quiz
        description: A brief description of the quiz
        course: The course to which this quiz belongs
        lesson: Optional specific lesson this quiz is associated with
        time_limit: Optional time limit in minutes
        pass_score: Minimum percentage score needed to pass
        max_attempts: Maximum number of attempts allowed (0 for unlimited)
        is_active: Whether this quiz is currently active
        show_correct_answers: Whether to show correct answers after submission
        randomize_questions: Whether to randomize question order
        created_at: Timestamp when the quiz was created
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name='quizzes', null=True, blank=True)
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes (0 for no limit)", default=0)
    pass_score = models.PositiveSmallIntegerField(default=70, help_text="Minimum percentage score needed to pass")
    max_attempts = models.PositiveSmallIntegerField(default=0, help_text="Maximum attempts allowed (0 for unlimited)")
    is_active = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return self.title
    
    @property
    def question_count(self):
        """Returns the number of questions in this quiz."""
        return self.questions.count()
    
    @property
    def total_points(self):
        """Returns the total possible points for this quiz."""
        return sum(question.points for question in self.questions.all())
    
    def get_absolute_url(self):
        """Get the URL for the quiz detail view."""
        from django.urls import reverse
        return reverse('quizzes:detail', kwargs={'quiz_id': self.id})


class Question(models.Model):
    """
    Question model representing a question in a quiz.
    
    Attributes:
        quiz: The quiz to which this question belongs
        text: The question text
        points: Points awarded for a correct answer
        question_type: Type of question (multiple choice, true/false, etc.)
        explanation: Optional explanation of the answer
        order: Display order in the quiz
    """
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay')
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    points = models.PositiveSmallIntegerField(default=1)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.text[:50]}..."
    
    def is_correct(self, selected_choices):
        """Check if selected choices are correct."""
        if self.question_type == 'multiple_choice':
            correct_choices = self.choices.filter(is_correct=True)
            if len(correct_choices) == 1:  # Single answer
                return selected_choices[0] == correct_choices[0].id
            else:  # Multiple answers allowed
                correct_ids = set(c.id for c in correct_choices)
                return set(int(c) for c in selected_choices) == correct_ids
        elif self.question_type == 'true_false':
            correct_choice = self.choices.get(is_correct=True)
            return selected_choices[0] == correct_choice.id
        return False  # For other question types


class Choice(models.Model):
    """
    Choice model representing a possible answer for a question.
    
    Attributes:
        question: The question to which this choice belongs
        text: The choice text
        is_correct: Whether this choice is a correct answer
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.text[:50]}..."


class QuizAttempt(models.Model):
    """
    QuizAttempt model representing a student's attempt at a quiz.
    
    Attributes:
        quiz: The quiz being attempted
        user: The student attempting the quiz
        started_at: When the attempt was started
        completed_at: When the attempt was completed
        score: The score achieved (percentage)
        passed: Whether the student passed the quiz
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username}'s attempt at {self.quiz.title}"
    
    def calculate_score(self):
        """Calculate the score for this attempt."""
        if not self.completed_at:
            return None
            
        answered_questions = self.answers.values('question').distinct().count()
        total_questions = self.quiz.questions.count()
        
        if answered_questions == 0 or total_questions == 0:
            return 0
            
        correct_answers = self.answers.filter(is_correct=True).count()
        score = (correct_answers / total_questions) * 100
        
        # Update score and pass status
        self.score = score
        self.passed = score >= self.quiz.pass_score
        self.save()
        
        return score


class StudentAnswer(models.Model):
    """
    StudentAnswer model representing a student's answer to a question.
    
    Attributes:
        attempt: The quiz attempt this answer belongs to
        question: The question being answered
        selected_choices: The choices selected by the student
        text_answer: Student's text answer for short answer and essay questions
        is_correct: Whether the answer is correct
    """
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"Answer to {self.question} by {self.attempt.user.username}"
    
    def check_answer(self):
        """Check if the answer is correct and update the is_correct field."""
        question_type = self.question.question_type
        
        if question_type in ['multiple_choice', 'true_false']:
            selected_ids = [choice.id for choice in self.selected_choices.all()]
            self.is_correct = self.question.is_correct(selected_ids)
            
        elif question_type == 'short_answer':
            # Simple exact match for short answers
            correct_choices = self.question.choices.filter(is_correct=True)
            if correct_choices.exists():
                correct_answer = correct_choices.first().text.strip().lower()
                self.is_correct = self.text_answer.strip().lower() == correct_answer
                
        else:  # Essay questions require manual grading
            self.is_correct = None
            
        self.save()
        return self.is_correct
