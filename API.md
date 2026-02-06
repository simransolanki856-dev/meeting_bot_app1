# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All API endpoints use Django's CSRF token for security. Include the CSRF token in request headers.

## Endpoints

### 1. List Meetings
**GET** `/meetings/`

List all meetings with pagination, search, and filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `search` | string | Search by title or description |
| `meeting_type` | string | Filter by type (team_meeting, interview, client_call, standup, other) |
| `ordering` | string | Order by field (-created_at, meeting_date, etc.) |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/meetings/?search=quarterly&meeting_type=team_meeting"
```

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/meetings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Quarterly Review",
      "meeting_type": "team_meeting",
      "meeting_type_display": "Team Meeting",
      "status": "completed",
      "status_display": "Completed",
      "created_at": "2024-01-15T10:30:00Z",
      "meeting_date": "2024-01-15T09:00:00Z"
    }
  ]
}
```

---

### 2. Create Meeting
**POST** `/meetings/`

Create a new meeting and generate AI summary.

**Request Body:**
```json
{
  "title": "Team Standup",
  "meeting_type": "standup",
  "description": "Daily team standup meeting",
  "meeting_date": "2024-01-15T09:00:00",
  "transcript": "Team discussed project progress...",
  "recording_file": "<file>"
}
```

**Form Data:**
```
title: Team Standup
meeting_type: standup
description: Daily team standup meeting
transcript: Team discussed project progress... (optional if file provided)
recording_file: file.mp3 (optional if transcript provided)
meeting_date: 2024-01-15T09:00:00
```

**Example Request (with transcript):**
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "X-CSRFToken: <csrf_token>" \
  -F "title=Team Standup" \
  -F "meeting_type=standup" \
  -F "transcript=Team discussed project progress..." \
  -F "meeting_date=2024-01-15T09:00:00"
```

**Example Request (with file):**
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "X-CSRFToken: <csrf_token>" \
  -F "title=Team Standup" \
  -F "meeting_type=standup" \
  -F "recording_file=@meeting.mp3" \
  -F "meeting_date=2024-01-15T09:00:00"
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Team Standup",
  "meeting_type": "standup",
  "meeting_type_display": "Standup",
  "description": "Daily team standup meeting",
  "transcript": "Team discussed project progress...",
  "created_at": "2024-01-15T10:30:00Z",
  "meeting_date": "2024-01-15T09:00:00Z",
  "status": "completed",
  "status_display": "Completed",
  "summary": "Team reviewed project milestones and identified blockers.",
  "key_points": [
    "Project on track for Q1 release",
    "Need support on infrastructure setup",
    "Customer feedback incorporated"
  ],
  "decisions": [
    "Allocate 2 engineers to infrastructure",
    "Schedule customer meeting next week"
  ],
  "action_items": [
    {
      "task": "Setup infrastructure",
      "owner": "John Doe",
      "due_date": "2024-01-20"
    },
    {
      "task": "Prepare customer presentation",
      "owner": "Jane Smith",
      "due_date": "2024-01-18"
    }
  ],
  "agenda": [
    {
      "topic": "Project Updates",
      "description": "Reviewed current progress and timeline"
    },
    {
      "topic": "Blockers",
      "description": "Discussed infrastructure challenges"
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "transcript": ["Either a transcript or a recording file must be provided."]
}
```

---

### 3. Get Meeting Details
**GET** `/meetings/{id}/`

Retrieve full details of a specific meeting including AI-generated summary.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | int | Meeting ID |

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/meetings/1/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Team Standup",
  "meeting_type": "standup",
  "meeting_type_display": "Standup",
  "description": "Daily team standup meeting",
  "transcript": "Full transcript here...",
  "created_at": "2024-01-15T10:30:00Z",
  "meeting_date": "2024-01-15T09:00:00Z",
  "status": "completed",
  "status_display": "Completed",
  "summary": "Team reviewed project milestones...",
  "key_points": [...],
  "decisions": [...],
  "action_items": [...],
  "agenda": [...]
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 4. Update Meeting
**PUT** `/meetings/{id}/`

Update meeting details.

**Request Body:**
```json
{
  "title": "Updated Title",
  "meeting_type": "team_meeting",
  "description": "Updated description",
  "meeting_date": "2024-01-15T09:00:00"
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/meetings/1/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <csrf_token>" \
  -d '{
    "title": "Updated Title",
    "meeting_type": "team_meeting"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Title",
  ...
}
```

---

### 5. Delete Meeting
**DELETE** `/meetings/{id}/`

Delete a meeting and all associated data.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | int | Meeting ID |

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/meetings/1/ \
  -H "X-CSRFToken: <csrf_token>"
```

**Response (204 No Content):**
```
(empty response)
```

---

### 6. Regenerate Summary
**POST** `/meetings/{id}/regenerate_summary/`

Regenerate AI summary for an existing meeting.

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/meetings/1/regenerate_summary/ \
  -H "X-CSRFToken: <csrf_token>"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Team Standup",
  "summary": "Regenerated summary...",
  "key_points": [...],
  "decisions": [...],
  "action_items": [...],
  "agenda": [...]
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "No transcript available for this meeting"
}
```

---

### 7. Download Summary
**GET** `/meetings/{id}/download_summary/`

Download meeting summary as text.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/meetings/1/download_summary/
```

**Response (200 OK):**
```json
{
  "content": "MEETING SUMMARY REPORT\n\nMeeting Title: Team Standup\n..."
}
```

The content can be saved as a .txt file on the client side.

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Internal server error |

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message here"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message"],
  "another_field": ["Another error"]
}
```

---

## Data Models

### Meeting Object
```json
{
  "id": 1,
  "title": "string",
  "meeting_type": "team_meeting|interview|client_call|standup|other",
  "meeting_type_display": "string",
  "description": "string or null",
  "transcript": "string or null",
  "recording_file": "string (file path) or null",
  "transcript_file": "string (file path) or null",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "meeting_date": "ISO 8601 datetime",
  "status": "pending|processing|completed|failed",
  "status_display": "string",
  "processing_error": "string or null",
  "summary_json": {
    "summary": "string",
    "key_points": ["string"],
    "decisions": ["string"],
    "action_items": [
      {
        "task": "string",
        "owner": "string or null",
        "due_date": "string or null"
      }
    ],
    "agenda": [
      {
        "topic": "string",
        "description": "string or null"
      }
    ]
  }
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. Rate limiting can be added using `django-ratelimit` or `djangorestframework-throttling`.

---

## Pagination

Default page size is 10 items. Customize in settings.py:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10  # Change this value
}
```

---

## CORS Configuration

CORS is enabled for the following origins (configurable in .env):

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Example cURL Workflows

### 1. Create and Retrieve a Meeting

```bash
# Create meeting
curl -X POST http://localhost:8000/api/meetings/ \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -F "title=Product Review" \
  -F "meeting_type=team_meeting" \
  -F "transcript=Product features discussed..." \
  -F "meeting_date=2024-01-15T10:00:00"

# Response includes "id": 5

# Get meeting details
curl -X GET http://localhost:8000/api/meetings/5/
```

### 2. Search and Filter Meetings

```bash
# Search by title
curl -X GET "http://localhost:8000/api/meetings/?search=product"

# Filter by type
curl -X GET "http://localhost:8000/api/meetings/?meeting_type=client_call"

# Combine filters
curl -X GET "http://localhost:8000/api/meetings/?search=product&meeting_type=client_call&page=1"
```

### 3. Update and Delete

```bash
# Update meeting
curl -X PUT http://localhost:8000/api/meetings/5/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d '{"title": "Updated Product Review"}'

# Delete meeting
curl -X DELETE http://localhost:8000/api/meetings/5/ \
  -H "X-CSRFToken: $CSRF_TOKEN"
```

---

## SDKs and Clients

### JavaScript/TypeScript

```javascript
const API_BASE = 'http://localhost:8000/api';

async function createMeeting(meetingData) {
  const formData = new FormData();
  formData.append('title', meetingData.title);
  formData.append('meeting_type', meetingData.meeting_type);
  formData.append('transcript', meetingData.transcript);

  const response = await fetch(`${API_BASE}/meetings/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: formData
  });

  return response.json();
}
```

### Python

```python
import requests

API_BASE = 'http://localhost:8000/api'

def create_meeting(title, meeting_type, transcript):
    data = {
        'title': title,
        'meeting_type': meeting_type,
        'transcript': transcript
    }
    response = requests.post(f'{API_BASE}/meetings/', json=data)
    return response.json()

def get_meetings(search=None):
    params = {}
    if search:
        params['search'] = search
    response = requests.get(f'{API_BASE}/meetings/', params=params)
    return response.json()
```

---

## Webhook Events (Future Feature)

Webhooks are not yet implemented but planned for future releases.

---

## API Changelog

### Version 1.0.0 (Current)
- Initial API release
- CRUD operations for meetings
- AI summary generation
- File upload support

### Planned Features
- Batch operations
- Webhooks
- Advanced analytics
- Real-time updates via WebSocket

---

For more help, check the [README.md](README.md) or create an issue on GitHub.
