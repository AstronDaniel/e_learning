# API Authentication

This document outlines the authentication methods available for the E-Learning Platform API.

## Authentication Methods

The API supports three authentication methods:

1. Session Authentication (for browser-based applications)
2. Token Authentication (for mobile or single-page applications)
3. JWT Authentication (for secure, stateless authentication)

## Session Authentication

Session authentication is primarily used for browser-based applications where the API is used within the same site as the Django application.

When a user logs in through the web interface, Django's session mechanism authenticates subsequent API requests automatically using cookies.

```
# Example of accessing the API from the same site using session authentication
# No additional headers needed if the user is already logged in
```

## Token Authentication

Token authentication is suitable for mobile applications, command-line tools, or single-page applications. To use token authentication:

### Obtaining a Token

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

### Using the Token

Include the token in the `Authorization` header for all subsequent requests:

```
GET /api/v1/courses/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Token Lifecycle

- Tokens do not expire automatically by default (can be configured)
- To invalidate a token, the user must log out explicitly
- Administrators can invalidate tokens from the admin panel

## JWT Authentication

JWT (JSON Web Token) authentication provides a stateless, secure method of authentication with built-in expiration.

### Obtaining JWT Tokens

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

### Using JWT Tokens

Include the access token in the `Authorization` header for all requests:

```
GET /api/v1/courses/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Refreshing JWT Tokens

Access tokens expire after 5 minutes by default. Use the refresh token to obtain a new access token:

```
POST /api/v1/auth/jwt/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Verification

To verify if a token is still valid:

```
POST /api/v1/auth/jwt/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

A 200 OK response indicates a valid token. Any other response means the token is invalid.

## Permission Levels

API endpoints enforce various permission levels:

1. **Public** - Accessible without authentication
2. **Authenticated** - Requires a valid authenticated user
3. **Student** - Requires authenticated user with student role
4. **Instructor** - Requires authenticated user with instructor role
5. **Owner** - Requires the user who created the resource
6. **Admin** - Requires admin privileges

Each endpoint specifies its permission requirements in the API documentation.

## Error Responses

Authentication errors return appropriate HTTP status codes:

- `401 Unauthorized` - No valid authentication credentials provided
- `403 Forbidden` - Authentication successful but insufficient permissions

Example error response:

```json
{
  "error": {
    "code": "authentication_failed",
    "message": "Invalid token",
    "details": "The provided token is expired or invalid"
  }
}
```

## Security Best Practices

1. **Always use HTTPS** for API requests to protect authentication credentials
2. **Store tokens securely** in your client application
3. **Implement token refresh logic** for JWT authentication
4. **Set appropriate token expiration** for your application's security needs
5. **Log out properly** to invalidate tokens when sessions end
