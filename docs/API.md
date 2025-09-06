# API Documentation

## Overview

The Nuvaru Domain-Centric Learning Platform provides a RESTful API for managing users, documents, knowledge bases, and AI interactions. The API follows REST conventions and uses JSON for data exchange.

## Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://api.nuvaru.ai/api/v1`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

### Getting an Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your-email@example.com&password=your-password"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## Endpoints

### Authentication

#### POST /auth/login
Login with email and password.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

#### POST /auth/logout
Logout user (client-side token invalidation).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### Users

#### GET /users/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "company": "Company Name",
  "role": "Role",
  "department": "Department",
  "is_active": true,
  "is_verified": true,
  "created_at": "2023-01-01T00:00:00Z",
  "last_login": "2023-01-01T00:00:00Z"
}
```

#### PUT /users/me
Update current user information.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "full_name": "Updated Name",
  "company": "Updated Company",
  "role": "Updated Role",
  "department": "Updated Department"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Updated Name",
  "company": "Updated Company",
  "role": "Updated Role",
  "department": "Updated Department"
}
```

#### POST /users/change-password
Change user password.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

#### POST /users/register
Register a new user.

**Request:**
```json
{
  "email": "newuser@example.com",
  "username": "newusername",
  "password": "password123",
  "full_name": "Full Name",
  "company": "Company Name",
  "role": "Role",
  "department": "Department"
}
```

**Response:**
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "username": "newusername",
  "full_name": "Full Name",
  "company": "Company Name",
  "role": "Role",
  "department": "Department",
  "is_active": true,
  "is_verified": false,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Documents

#### GET /documents/
Get user documents.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Document Title",
    "filename": "document.pdf",
    "size": 1024000,
    "content_type": "application/pdf",
    "uploaded_at": "2023-01-01T00:00:00Z",
    "status": "processed"
  }
]
```

#### POST /documents/upload
Upload a new document.

**Headers:** `Authorization: Bearer <token>`

**Request:** Multipart form data with file

**Response:**
```json
{
  "id": "uuid",
  "title": "Document Title",
  "filename": "document.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "uploaded_at": "2023-01-01T00:00:00Z",
  "status": "processing"
}
```

#### GET /documents/{document_id}
Get specific document.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "title": "Document Title",
  "filename": "document.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "uploaded_at": "2023-01-01T00:00:00Z",
  "status": "processed",
  "content": "Extracted text content...",
  "metadata": {
    "pages": 10,
    "language": "en",
    "topics": ["topic1", "topic2"]
  }
}
```

### Knowledge Bases

#### GET /knowledge/
Get user knowledge bases.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Knowledge Base Name",
    "description": "Description",
    "domain": "healthcare",
    "document_count": 150,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

#### POST /knowledge/
Create a new knowledge base.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "New Knowledge Base",
  "description": "Description",
  "domain": "healthcare"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "New Knowledge Base",
  "description": "Description",
  "domain": "healthcare",
  "document_count": 0,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### GET /knowledge/{kb_id}
Get specific knowledge base.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "name": "Knowledge Base Name",
  "description": "Description",
  "domain": "healthcare",
  "document_count": 150,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "documents": [
    {
      "id": "uuid",
      "title": "Document Title",
      "uploaded_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### Learning Engine

#### POST /learning/chat
Chat with the AI assistant.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "message": "What is the treatment for diabetes?",
  "knowledge_base_id": "uuid",
  "context": "patient consultation"
}
```

**Response:**
```json
{
  "response": "Based on the latest medical guidelines...",
  "sources": [
    {
      "document_id": "uuid",
      "title": "Diabetes Treatment Guidelines",
      "relevance_score": 0.95,
      "excerpt": "Treatment includes..."
    }
  ],
  "session_id": "uuid",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

#### POST /learning/feedback
Submit learning feedback.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "session_id": "uuid",
  "response_id": "uuid",
  "rating": 5,
  "feedback": "Very helpful response",
  "correctness": true
}
```

**Response:**
```json
{
  "message": "Feedback submitted successfully"
}
```

#### GET /learning/sessions
Get learning sessions.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "knowledge_base_id": "uuid",
    "started_at": "2023-01-01T00:00:00Z",
    "ended_at": "2023-01-01T01:00:00Z",
    "message_count": 10,
    "satisfaction_score": 4.5
  }
]
```

### Analytics

#### GET /analytics/metrics
Get platform metrics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_documents": 1000,
  "total_knowledge_bases": 25,
  "total_sessions": 500,
  "average_satisfaction": 4.2,
  "active_users": 150
}
```

#### GET /analytics/usage
Get usage statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "daily_queries": 250,
  "weekly_queries": 1750,
  "monthly_queries": 7500,
  "top_domains": [
    {"domain": "healthcare", "queries": 500},
    {"domain": "legal", "queries": 300}
  ]
}
```

#### GET /analytics/performance
Get performance data.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "average_response_time": 1.2,
  "uptime_percentage": 99.9,
  "error_rate": 0.1,
  "throughput": 100
}
```

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "context": {
    "field": "additional context"
  }
}
```

### Common Error Codes

- `AUTHENTICATION_ERROR` (401): Invalid credentials
- `AUTHORIZATION_ERROR` (403): Insufficient permissions
- `VALIDATION_ERROR` (422): Invalid input data
- `NOT_FOUND_ERROR` (404): Resource not found
- `CONFLICT_ERROR` (409): Resource conflict
- `RATE_LIMIT_ERROR` (429): Rate limit exceeded
- `DATABASE_ERROR` (500): Database operation failed
- `LLM_ERROR` (500): LLM operation failed

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default limit**: 100 requests per minute per user
- **Headers**: Rate limit information is included in response headers
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## Pagination

List endpoints support pagination using query parameters:

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100, max: 1000)

Example:
```
GET /documents/?skip=20&limit=10
```

## Webhooks

The platform supports webhooks for real-time notifications:

- Document processing completion
- Knowledge base updates
- Learning session events
- System alerts

Configure webhooks in the user settings or via API.

## SDKs and Libraries

Official SDKs are available for:

- Python
- JavaScript/TypeScript
- Java
- C#

Community libraries are available for other languages.



