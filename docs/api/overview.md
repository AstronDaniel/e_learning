# API Overview

The E-Learning Platform provides a RESTful API for integrating with other systems and building custom interfaces.

## API Base URL

- Development: `http://localhost:8000/api/v1/`
- Production: `https://your-domain.com/api/v1/`

## Authentication

### Token Authentication

The API uses token-based authentication. To obtain a token:

```
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

Include this token in subsequent requests:

```
GET /api/v1/courses/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### JWT Authentication (Optional)

JWT authentication is also available:

```
POST /api/v1/auth/jwt/create/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Include the access token in subsequent requests:

```
GET /api/v1/courses/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Rate Limiting

API endpoints are rate-limited to:
- 100 requests per hour for authenticated users
- 20 requests per hour for anonymous users

## Available Endpoints

### User Management

- `GET /api/v1/users/profile/` - Retrieve authenticated user profile
- `PUT /api/v1/users/profile/` - Update user profile
- `GET /api/v1/users/{id}/` - Get user information (instructors only)

### Courses

- `GET /api/v1/courses/` - List available courses
- `GET /api/v1/courses/{id}/` - Get course details
- `POST /api/v1/courses/` - Create new course (instructors only)
- `PUT /api/v1/courses/{id}/` - Update course (owner or admin only)
- `DELETE /api/v1/courses/{id}/` - Delete course (owner or admin only)

### Enrollments

- `GET /api/v1/enrollments/` - List user's enrollments
- `POST /api/v1/enrollments/` - Enroll in a course
- `DELETE /api/v1/enrollments/{id}/` - Unenroll from a course
- `GET /api/v1/courses/{id}/enrollments/` - List course enrollments (instructors only)

### Lessons

- `GET /api/v1/courses/{course_id}/lessons/` - List lessons in a course
- `GET /api/v1/lessons/{id}/` - Get lesson details
- `POST /api/v1/courses/{course_id}/lessons/` - Create new lesson (instructors only)
- `PUT /api/v1/lessons/{id}/` - Update lesson (owner or admin only)
- `DELETE /api/v1/lessons/{id}/` - Delete lesson (owner or admin only)

### Quizzes

- `GET /api/v1/courses/{course_id}/quizzes/` - List quizzes in a course
- `GET /api/v1/quizzes/{id}/` - Get quiz details
- `POST /api/v1/courses/{course_id}/quizzes/` - Create new quiz (instructors only)
- `POST /api/v1/quizzes/{id}/submit/` - Submit quiz answers
- `GET /api/v1/quizzes/{id}/results/` - Get quiz results

### Forums

- `GET /api/v1/courses/{course_id}/forums/` - List forum topics in a course
- `POST /api/v1/courses/{course_id}/forums/` - Create new forum topic
- `GET /api/v1/forums/{id}/comments/` - List comments in a forum topic
- `POST /api/v1/forums/{id}/comments/` - Add a comment to a forum topic

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "data": {
    // Response data here
  },
  "meta": {
    "status_code": 200,
    "page": 1,
    "total_pages": 5,
    "total_count": 100
  }
}
```

## Error Handling

Errors return appropriate HTTP status codes with a consistent format:

```json
{
  "error": {
    "code": "invalid_input",
    "message": "The provided data was invalid",
    "details": {
      "field_name": [
        "This field is required"
      ]
    }
  }
}
```

Common error codes:
- `401` - Authentication failure
- `403` - Permission denied
- `404` - Resource not found
- `422` - Validation error
- `429` - Rate limit exceeded
