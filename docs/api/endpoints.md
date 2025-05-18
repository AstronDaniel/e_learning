# API Endpoints Documentation

This document details all available API endpoints in the E-Learning Platform.

## Authentication Endpoints

### Token Authentication

```
POST /api/v1/auth/token/
```

Obtain an authentication token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string"
}
```

### JWT Authentication

```
POST /api/v1/auth/jwt/create/
```

Obtain JWT tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "refresh": "string",
  "access": "string"
}
```

```
POST /api/v1/auth/jwt/refresh/
```

Refresh JWT access token.

**Request Body:**
```json
{
  "refresh": "string"
}
```

**Response:**
```json
{
  "access": "string"
}
```

## User Endpoints

### User Profile

```
GET /api/v1/users/profile/
```

Get the authenticated user's profile information.

**Response:**
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "is_instructor": "boolean",
  "avatar": "string",
  "bio": "string",
  "date_joined": "datetime"
}
```

```
PUT /api/v1/users/profile/
```

Update user profile.

**Request Body:**
```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "avatar": "file",
  "bio": "string"
}
```

## Course Endpoints

### Course Listing

```
GET /api/v1/courses/
```

List all courses with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `category`: Filter by category
- `search`: Search term in title or description

**Response:**
```json
{
  "data": [
    {
      "id": "integer",
      "title": "string",
      "slug": "string",
      "description": "string",
      "instructor": {
        "id": "integer",
        "username": "string",
        "avatar": "string"
      },
      "thumbnail": "string",
      "category": "string",
      "students_count": "integer",
      "rating": "float",
      "created_at": "datetime"
    }
  ],
  "meta": {
    "page": "integer",
    "total_pages": "integer",
    "total_count": "integer"
  }
}
```

### Course Details

```
GET /api/v1/courses/{id}/
```

Get detailed information about a specific course.

**Response:**
```json
{
  "id": "integer",
  "title": "string",
  "slug": "string",
  "description": "string",
  "instructor": {
    "id": "integer",
    "username": "string",
    "avatar": "string",
    "bio": "string"
  },
  "thumbnail": "string",
  "category": "string",
  "students_count": "integer",
  "rating": "float",
  "created_at": "datetime",
  "is_enrolled": "boolean",
  "sections": [
    {
      "id": "integer",
      "title": "string",
      "order": "integer",
      "lessons": [
        {
          "id": "integer",
          "title": "string",
          "order": "integer",
          "duration": "integer",
          "is_preview": "boolean"
        }
      ]
    }
  ]
}
```

### Course Creation

```
POST /api/v1/courses/
```

Create a new course (instructors only).

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "category": "string",
  "thumbnail": "file",
  "is_published": "boolean"
}
```

## Enrollment Endpoints

### User Enrollments

```
GET /api/v1/enrollments/
```

List enrolled courses for the authenticated user.

**Response:**
```json
[
  {
    "id": "integer",
    "course": {
      "id": "integer",
      "title": "string",
      "thumbnail": "string"
    },
    "date_enrolled": "datetime",
    "completed": "boolean",
    "progress": "float"
  }
]
```

### Enroll in Course

```
POST /api/v1/enrollments/
```

Enroll in a course.

**Request Body:**
```json
{
  "course_id": "integer"
}
```

## Lesson Endpoints

### Lesson Details

```
GET /api/v1/lessons/{id}/
```

Get detailed information about a specific lesson.

**Response:**
```json
{
  "id": "integer",
  "title": "string",
  "content": "string",
  "video_url": "string",
  "attachments": [
    {
      "id": "integer",
      "file": "string",
      "name": "string"
    }
  ],
  "duration": "integer",
  "is_completed": "boolean",
  "next_lesson": "integer",
  "prev_lesson": "integer"
}
```

## Quiz Endpoints

### Quiz Details

```
GET /api/v1/quizzes/{id}/
```

Get detailed information about a quiz.

**Response:**
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "time_limit": "integer",
  "pass_score": "float",
  "attempts_allowed": "integer",
  "attempts_made": "integer",
  "questions_count": "integer"
}
```

### Quiz Questions

```
GET /api/v1/quizzes/{id}/questions/
```

Get questions for a quiz (only when taking the quiz).

**Response:**
```json
[
  {
    "id": "integer",
    "text": "string",
    "type": "string",
    "options": [
      {
        "id": "integer", 
        "text": "string"
      }
    ],
    "points": "integer"
  }
]
```

### Submit Quiz

```
POST /api/v1/quizzes/{id}/submit/
```

Submit answers for a quiz.

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": "integer",
      "option_id": "integer"
    }
  ]
}
```

## Forum Endpoints

### Forum Topics

```
GET /api/v1/courses/{course_id}/forums/
```

List forum topics for a course.

**Response:**
```json
[
  {
    "id": "integer",
    "title": "string",
    "author": {
      "id": "integer",
      "username": "string",
      "avatar": "string"
    },
    "created_at": "datetime",
    "replies_count": "integer",
    "last_activity": "datetime"
  }
]
```

### Forum Topic Details

```
GET /api/v1/forums/{id}/
```

Get detailed information about a forum topic.

**Response:**
```json
{
  "id": "integer",
  "title": "string",
  "content": "string",
  "author": {
    "id": "integer",
    "username": "string",
    "avatar": "string"
  },
  "created_at": "datetime",
  "comments": [
    {
      "id": "integer",
      "content": "string",
      "author": {
        "id": "integer",
        "username": "string",
        "avatar": "string"
      },
      "created_at": "datetime"
    }
  ]
}
```

## Analytics Endpoints (Instructors Only)

### Course Analytics

```
GET /api/v1/instructor/courses/{id}/analytics/
```

Get analytics for a course.

**Response:**
```json
{
  "enrollments": {
    "total": "integer",
    "active": "integer",
    "completed": "integer",
    "history": [
      {
        "date": "string",
        "count": "integer"
      }
    ]
  },
  "content_engagement": {
    "most_viewed_lessons": [
      {
        "id": "integer",
        "title": "string",
        "views": "integer"
      }
    ],
    "quiz_performance": [
      {
        "id": "integer",
        "title": "string",
        "average_score": "float",
        "completion_rate": "float"
      }
    ]
  }
}
```
