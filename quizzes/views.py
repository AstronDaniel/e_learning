from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.urls import reverse

from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer
from courses.models import Course, Lesson
from users.models import Enrollment

@login_required
def quiz_detail(request, quiz_id):
    """Display quiz details before starting."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=quiz.course)
    
    # Get previous attempts
    previous_attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        user=request.user,
        completed_at__isnull=False
    ).order_by('-started_at')
    
    # Check if student has exceeded max attempts
    attempts_left = None
    if quiz.max_attempts > 0:
        attempts_made = previous_attempts.count()
        attempts_left = quiz.max_attempts - attempts_made
        if attempts_left <= 0:
            messages.warning(request, f"You have used all your attempts for this quiz.")
    
    context = {
        'quiz': quiz,
        'previous_attempts': previous_attempts,
        'attempts_left': attempts_left,
        'course': quiz.course,
        'lesson': quiz.lesson,
        'can_attempt': attempts_left is None or attempts_left > 0
    }
    
    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    """Create a new quiz attempt and show the first question."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=quiz.course)
    
    # Check if max attempts reached
    if quiz.max_attempts > 0:
        attempts_made = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=False
        ).count()
        
        if attempts_made >= quiz.max_attempts:
            messages.error(request, "You have reached the maximum number of attempts for this quiz.")
            return redirect('quizzes:detail', quiz_id=quiz.id)
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=request.user
    )
    
    # Get questions - randomize if specified
    questions = list(quiz.questions.all())
    if quiz.randomize_questions:
        import random
        random.shuffle(questions)
    
    # Store questions in session
    request.session[f'quiz_attempt_{attempt.id}'] = {
        'questions': [q.id for q in questions],
        'current_index': 0,
        'answers': {},
        'start_time': timezone.now().isoformat()
    }
    
    # Redirect to first question
    return redirect('quizzes:question', quiz_id=quiz.id, attempt_id=attempt.id, question_index=0)

@login_required
def question_view(request, quiz_id, attempt_id, question_index):
    """Display a specific question in the quiz attempt."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, quiz=quiz, completed_at__isnull=True)
    
    # Get session data
    session_key = f'quiz_attempt_{attempt.id}'
    if session_key not in request.session:
        messages.error(request, "Your quiz session has expired.")
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    quiz_session = request.session[session_key]
    questions_ids = quiz_session['questions']
    
    # Validate question index
    if question_index < 0 or question_index >= len(questions_ids):
        messages.error(request, "Invalid question index.")
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    # Get current question
    question_id = questions_ids[question_index]
    question = get_object_or_404(Question, id=question_id)
    
    # Check for time limit
    if quiz.time_limit > 0:
        start_time = timezone.datetime.fromisoformat(quiz_session['start_time'])
        time_elapsed = (timezone.now() - start_time).total_seconds() / 60  # minutes
        
        if time_elapsed > quiz.time_limit:
            messages.warning(request, "Time's up! Your answers have been automatically submitted.")
            return submit_quiz(request, quiz_id)
        
        time_left = max(0, quiz.time_limit - time_elapsed)
    else:
        time_left = None
    
    # Get previous answer if exists
    user_answer = quiz_session['answers'].get(str(question.id), {})
    
    context = {
        'quiz': quiz,
        'attempt': attempt,
        'question': question,
        'question_index': question_index,
        'total_questions': len(questions_ids),
        'time_left': time_left,
        'user_answer': user_answer,
        'is_first': question_index == 0,
        'is_last': question_index == len(questions_ids) - 1,
        'course': quiz.course,
        'next_index': min(question_index + 1, len(questions_ids) - 1),
        'prev_index': max(0, question_index - 1)
    }
    
    # Update current index in session
    quiz_session['current_index'] = question_index
    request.session[session_key] = quiz_session
    request.session.modified = True
    
    return render(request, 'quizzes/question.html', context)

@login_required
def save_answer(request, quiz_id, attempt_id, question_index):
    """Save the answer to a question without submitting the entire quiz."""
    if request.method != 'POST':
        return redirect('quizzes:question', quiz_id=quiz_id, attempt_id=attempt_id, question_index=question_index)
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, quiz=quiz, completed_at__isnull=True)
    
    # Get session data
    session_key = f'quiz_attempt_{attempt.id}'
    if session_key not in request.session:
        messages.error(request, "Your quiz session has expired.")
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    quiz_session = request.session[session_key]
    questions_ids = quiz_session['questions']
    
    # Validate question index
    if question_index < 0 or question_index >= len(questions_ids):
        messages.error(request, "Invalid question index.")
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    # Get current question
    question_id = questions_ids[question_index]
    question = get_object_or_404(Question, id=question_id)
    
    # Save answer based on question type
    answer_data = {}
    
    if question.question_type in ['multiple_choice', 'true_false']:
        # Handle multiple choice questions
        choice_ids = request.POST.getlist('choice')
        answer_data = {'choice_ids': choice_ids}
    else:
        # Handle text-based questions
        text_answer = request.POST.get('text_answer', '')
        answer_data = {'text_answer': text_answer}
    
    # Save answer to session
    quiz_session['answers'][str(question.id)] = answer_data
    request.session[session_key] = quiz_session
    request.session.modified = True
    
    # Determine where to redirect
    next_action = request.POST.get('next_action', 'next')
    
    if next_action == 'prev':
        new_index = max(0, question_index - 1)
    elif next_action == 'next':
        new_index = min(question_index + 1, len(questions_ids) - 1)
    else:  # Question number clicked
        try:
            new_index = int(next_action)
            if new_index < 0 or new_index >= len(questions_ids):
                new_index = question_index
        except ValueError:
            new_index = question_index
    
    return redirect('quizzes:question', quiz_id=quiz.id, attempt_id=attempt.id, question_index=new_index)

@login_required
@transaction.atomic
def submit_quiz(request, quiz_id):
    """Submit the entire quiz and calculate results."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Find the active attempt for this quiz
    try:
        attempt = QuizAttempt.objects.get(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=True
        )
    except QuizAttempt.DoesNotExist:
        messages.error(request, "No active quiz attempt found.")
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    # Get session data
    session_key = f'quiz_attempt_{attempt.id}'
    if session_key not in request.session:
        messages.error(request, "Your quiz session has expired.")
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    quiz_session = request.session[session_key]
    
    # Mark attempt as completed
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # Process and save all answers
    for question_id_str, answer_data in quiz_session['answers'].items():
        question_id = int(question_id_str)
        question = get_object_or_404(Question, id=question_id)
        
        student_answer = StudentAnswer(
            attempt=attempt,
            question=question
        )
        
        if question.question_type in ['multiple_choice', 'true_false']:
            # Handle multiple choice questions
            student_answer.save()  # Save first to allow many-to-many relationship
            
            choice_ids = answer_data.get('choice_ids', [])
            if choice_ids:
                choices = Choice.objects.filter(id__in=choice_ids, question=question)
                student_answer.selected_choices.set(choices)
        else:
            # Handle text-based questions
            student_answer.text_answer = answer_data.get('text_answer', '')
            student_answer.save()
        
        # Check answer correctness
        student_answer.check_answer()
    
    # Calculate score
    attempt.calculate_score()
    
    # Clean up session
    del request.session[session_key]
    
    # Redirect to results
    return redirect('quizzes:result', quiz_id=quiz.id, attempt_id=attempt.id)

@login_required
def quiz_result(request, quiz_id, attempt_id):
    """Display quiz results after submission."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, quiz=quiz, completed_at__isnull=False)
    
    # Get all questions and answers
    questions = quiz.questions.all()
    answers = attempt.answers.all()
    
    # Organize answers by question
    question_answers = {}
    for answer in answers:
        question_answers[answer.question.id] = answer
    
    # Calculate stats
    total_questions = questions.count()
    correct_answers = attempt.answers.filter(is_correct=True).count()
    incorrect_answers = attempt.answers.filter(is_correct=False).count()
    unanswered = total_questions - (correct_answers + incorrect_answers)
    
    context = {
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'question_answers': question_answers,
        'course': quiz.course,
        'lesson': quiz.lesson,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'unanswered': unanswered,
        'show_answers': quiz.show_correct_answers
    }
    
    return render(request, 'quizzes/quiz_result.html', context)

@login_required
def select_course_for_quiz(request):
    """View for instructors to select which course to create a quiz for."""
    # Check if user is an instructor
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor:
        return HttpResponseForbidden("You must be an instructor to create quizzes.")
    
    # Get courses where the user is the instructor
    instructor_courses = Course.objects.filter(instructor=request.user).order_by('-created_at')
    
    context = {
        'courses': instructor_courses
    }
    
    return render(request, 'quizzes/select_course.html', context)

@login_required
def create_quiz(request, course_slug):
    """Create a new quiz for a course."""
    # Check if user is the course instructor
    course = get_object_or_404(Course, slug=course_slug)
    if request.user != course.instructor:
        return HttpResponseForbidden("You must be the course instructor to create quizzes.")
    
    lessons = Lesson.objects.filter(course=course)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        time_limit = request.POST.get('time_limit')
        passing_score = request.POST.get('passing_score')
        max_attempts = request.POST.get('max_attempts')
        lesson_id = request.POST.get('lesson')
        
        # Basic validation
        if not title:
            messages.error(request, "Quiz title is required.")
        else:            # Create the quiz
            quiz = Quiz(
                course=course,
                title=title,
                description=description,
                time_limit=int(time_limit) if time_limit else 0,
                pass_score=float(passing_score) if passing_score else 70,
                max_attempts=int(max_attempts) if max_attempts else 0
            )
            
            # Associate with lesson if specified
            if lesson_id:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    quiz.lesson = lesson
                except Lesson.DoesNotExist:
                    pass
                
            quiz.save()
            
            messages.success(request, f"Quiz '{title}' created successfully. Add questions to complete it.")
            return redirect('quizzes:add_question', quiz_id=quiz.id)
    
    context = {
        'course': course,
        'lessons': lessons
    }
    
    return render(request, 'quizzes/create_quiz.html', context)

@login_required
def edit_quiz(request, quiz_id):
    """Edit an existing quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the course instructor
    if request.user != quiz.course.instructor:
        return HttpResponseForbidden("You must be the course instructor to edit this quiz.")
    
    lessons = Lesson.objects.filter(course=quiz.course)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        time_limit = request.POST.get('time_limit')
        passing_score = request.POST.get('passing_score')
        max_attempts = request.POST.get('max_attempts')
        lesson_id = request.POST.get('lesson')
        
        # Basic validation
        if not title:
            messages.error(request, "Quiz title is required.")
        else:
            # Update the quiz
            quiz.title = title
            quiz.description = description
            quiz.time_limit = int(time_limit) if time_limit else None
            quiz.passing_score = float(passing_score) if passing_score else 70
            quiz.max_attempts = int(max_attempts) if max_attempts else 0
            
            # Update lesson association
            if lesson_id:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    quiz.lesson = lesson
                except Lesson.DoesNotExist:
                    quiz.lesson = None
            else:
                quiz.lesson = None
                
            quiz.save()
            
            messages.success(request, f"Quiz '{title}' updated successfully.")
            return redirect('quizzes:detail', quiz_id=quiz.id)
    
    context = {
        'quiz': quiz,
        'course': quiz.course,
        'lessons': lessons
    }
    
    return render(request, 'quizzes/edit_quiz.html', context)

@login_required
def add_question(request, quiz_id):
    """Add a new question to a quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the course instructor
    if request.user != quiz.course.instructor:
        return HttpResponseForbidden("You must be the course instructor to add questions.")
    
    existing_questions = Question.objects.filter(quiz=quiz).order_by('order')
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        points = request.POST.get('points', 1)
        explanation = request.POST.get('explanation', '')
        
        if not question_text:
            messages.error(request, "Question text is required.")
        else:
            with transaction.atomic():
                # Create the question
                question = Question(
                    quiz=quiz,
                    text=question_text,
                    question_type=question_type,
                    points=float(points) if points else 1,
                    explanation=explanation,
                    order=existing_questions.count() + 1
                )
                question.save()
                
                # For multiple choice or true/false, process choices
                if question_type in ['multiple_choice', 'true_false']:
                    choice_texts = request.POST.getlist('choice_text')
                    is_correct_values = request.POST.getlist('is_correct')
                    
                    for i, choice_text in enumerate(choice_texts):
                        if choice_text.strip():
                            is_correct = str(i) in is_correct_values
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=is_correct
                            )
                
                messages.success(request, "Question added successfully.")
                
                # Check if "Save and Add Another" button was clicked
                if 'save_and_add' in request.POST:
                    return redirect('quizzes:add_question', quiz_id=quiz.id)
                else:
                    return redirect('quizzes:detail', quiz_id=quiz.id)
    
    context = {
        'quiz': quiz,
        'course': quiz.course,
        'existing_questions': existing_questions
    }
    
    return render(request, 'quizzes/add_question.html', context)

@login_required
def edit_question(request, quiz_id, question_id):
    """Edit an existing question."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    # Check if user is the course instructor
    if request.user != quiz.course.instructor:
        return HttpResponseForbidden("You must be the course instructor to edit questions.")
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        points = request.POST.get('points', 1)
        explanation = request.POST.get('explanation', '')
        
        if not question_text:
            messages.error(request, "Question text is required.")
        else:
            with transaction.atomic():
                # Update the question
                question.text = question_text
                question.points = float(points) if points else 1
                question.explanation = explanation
                question.save()
                
                # For multiple choice or true/false, update choices
                if question_type in ['multiple_choice', 'true_false']:
                    # First delete existing choices
                    question.choices.all().delete()
                    
                    # Then create new ones
                    choice_texts = request.POST.getlist('choice_text')
                    is_correct_values = request.POST.getlist('is_correct')
                    
                    for i, choice_text in enumerate(choice_texts):
                        if choice_text.strip():
                            is_correct = str(i) in is_correct_values
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=is_correct
                            )
                
                messages.success(request, "Question updated successfully.")
                return redirect('quizzes:detail', quiz_id=quiz.id)
    
    context = {
        'quiz': quiz,
        'question': question,
        'course': quiz.course,
        'choices': question.choices.all() if question.question_type in ['multiple_choice', 'true_false'] else None
    }
    
    return render(request, 'quizzes/edit_question.html', context)

@login_required
def quiz_results(request, quiz_id, attempt_id):
    """View detailed results for a specific quiz attempt."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, quiz=quiz)
    
    # Check permissions - must be the user who took the quiz or the instructor
    if request.user != attempt.user and request.user != quiz.course.instructor:
        return HttpResponseForbidden("You don't have permission to view these results.")
    
    # Get student answers
    student_answers = StudentAnswer.objects.filter(attempt=attempt).select_related('question')
    
    context = {
        'quiz': quiz,
        'attempt': attempt,
        'student_answers': student_answers,
        'course': quiz.course,
        'is_instructor': request.user == quiz.course.instructor
    }
    
    return render(request, 'quizzes/quiz_results.html', context)

@login_required
def quiz_attempts(request, quiz_id):
    """View attempts for a specific quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the course instructor or the student who took the quiz
    is_instructor = request.user == quiz.course.instructor
    
    if is_instructor:
        # Instructors can view all attempts
        attempts = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False).order_by('-started_at')
    else:
        # Students can only view their own attempts
        # Check if user is enrolled in the course
        enrollment = get_object_or_404(Enrollment, user=request.user, course=quiz.course)
        attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user, completed_at__isnull=False).order_by('-started_at')
    
    context = {
        'quiz': quiz,
        'course': quiz.course,
        'attempts': attempts,
        'is_instructor': is_instructor
    }
    
    return render(request, 'quizzes/quiz_attempts.html', context)

@login_required
def quiz_attempts_list(request):
    """View a list of the current user's quiz attempts."""
    # Get all attempts for this user
    attempts = QuizAttempt.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).select_related('quiz', 'quiz__course').order_by('-started_at')
    
    context = {
        'attempts': attempts
    }
    
    return render(request, 'quizzes/attempts_list.html', context)

@login_required
def course_quizzes(request, course_slug):
    """View all quizzes for a specific course."""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get all quizzes for this course
    quizzes = Quiz.objects.filter(course=course)
    
    # Get attempt information for each quiz
    for quiz in quizzes:
        quiz.user_attempts = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=False
        ).order_by('-started_at')
        
        quiz.best_score = quiz.user_attempts.order_by('-score').first()
        quiz.attempts_left = None
        
        if quiz.max_attempts > 0:
            quiz.attempts_left = quiz.max_attempts - quiz.user_attempts.count()
    
    context = {
        'course': course,
        'quizzes': quizzes
    }
    
    return render(request, 'quizzes/course_quizzes.html', context)

@login_required
def delete_quiz(request, quiz_id):
    """Delete a quiz and all its associated questions and attempts."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the course instructor
    if request.user != quiz.course.instructor:
        return HttpResponseForbidden("You must be the course instructor to delete this quiz.")
    
    # Store course for redirection after deletion
    course = quiz.course
    quiz_title = quiz.title
    
    if request.method == 'POST':
        # Delete the quiz - this will cascade delete questions and attempts
        quiz.delete()
        
        messages.success(request, f"Quiz '{quiz_title}' has been deleted successfully.")
        return redirect('instructor:quizzes')
    
    # If not a POST request, redirect to quiz detail page
    return redirect('quizzes:detail', quiz_id=quiz.id)
