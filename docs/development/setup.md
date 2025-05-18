# Setup Guide for Developers

This guide will help you set up the E-Learning Platform development environment.

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- Database (SQLite for development, PostgreSQL for production)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/e-learning.git
cd e-learning
```

### 2. Create and Activate a Virtual Environment

```bash
# Using venv (Python 3.3+)
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///db.sqlite3
# Add other environment variables as needed
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

### 6. Load Sample Data (Optional)

```bash
python manage.py loaddata sample_data/courses.json
python manage.py loaddata sample_data/users.json
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Access the site at http://127.0.0.1:8000/

## Project Structure

```
e_learning/              # Project root
├── courses/             # Course management app
├── users/               # User management app
├── quizzes/             # Quiz functionality
├── forums/              # Discussion forums
├── instructor/          # Instructor-specific features
├── static/              # Static assets
├── media/               # User-uploaded content
├── templates/           # HTML templates
└── e_learning/          # Project configuration
```

## Working with the Database

### Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Database Shell

```bash
python manage.py dbshell
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test courses

# Run a specific test class
python manage.py test courses.tests.TestCoursesModels

# Run with coverage
coverage run manage.py test
coverage report
coverage html  # Generates HTML report
```

## Common Issues

### Static Files Not Loading

Run:
```bash
python manage.py collectstatic
```

### Database Migrations Conflict

If you encounter migration conflicts:
```bash
# Fake the problematic migration
python manage.py migrate app_name migration_name --fake

# Then apply remaining migrations
python manage.py migrate
```
