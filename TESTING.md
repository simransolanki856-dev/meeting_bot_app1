# Testing Guide

## Unit Tests

Run the test suite:

```bash
python manage.py test
```

Run tests for specific app:

```bash
python manage.py test meeting
```

Run tests with verbosity:

```bash
python manage.py test --verbosity=2
```

Run a specific test:

```bash
python manage.py test meeting.tests.MeetingModelTest
```

## Test Coverage

Generate coverage report:

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Manual Testing

### Test 1: Create Meeting with Transcript

1. Navigate to `http://localhost:8000/create/`
2. Enter meeting details:
   - Title: "Team Standup"
   - Type: "Standup"
   - Date: Today
3. Paste a sample transcript in the transcript tab
4. Click "Generate Summary"
5. Verify summary is generated

**Expected Result**: Meeting created with AI-generated summary

---

### Test 2: Upload Audio File

1. Navigate to `http://localhost:8000/create/`
2. Enter meeting details
3. Click "Upload Recording" tab
4. Upload an MP3, WAV, or MP4 file
5. Click "Generate Summary"
6. Wait for transcription and summary generation

**Expected Result**: Audio transcribed and summary generated

---

### Test 3: Search Meetings

1. Navigate to `http://localhost:8000/history/`
2. Create several meetings with different titles
3. In search box, type a partial title
4. Click "Search"
5. Verify results are filtered

**Expected Result**: Only matching meetings shown

---

### Test 4: Filter by Meeting Type

1. Navigate to `http://localhost:8000/history/`
2. Select "Team Meeting" from filter dropdown
3. Verify only team meetings are shown
4. Try other filters

**Expected Result**: Meetings filtered correctly by type

---

### Test 5: Download Summary

1. Create a meeting with summary
2. Navigate to meeting details
3. Click "Download TXT" button
4. Verify file downloads with proper formatting

**Expected Result**: Summary text file downloads

---

### Test 6: Delete Meeting

1. Navigate to meeting history
2. Click delete button on a meeting
3. Confirm deletion
4. Verify meeting is removed from list

**Expected Result**: Meeting deleted successfully

---

### Test 7: Regenerate Summary

1. Navigate to an existing meeting
2. Click "Regenerate Summary" (if available)
3. Verify new summary is generated

**Expected Result**: Summary updated with new AI output

---

## API Testing

### Using cURL

**Create Meeting:**
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -F "title=Test Meeting" \
  -F "meeting_type=team_meeting" \
  -F "transcript=Sample transcript for testing" \
  -F "meeting_date=2024-01-15T10:00:00"
```

**List Meetings:**
```bash
curl http://localhost:8000/api/meetings/
```

**Get Specific Meeting:**
```bash
curl http://localhost:8000/api/meetings/1/
```

**Delete Meeting:**
```bash
curl -X DELETE http://localhost:8000/api/meetings/1/ \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN"
```

### Using Postman

1. Import API collection (create in Postman)
2. Set base URL: `http://localhost:8000`
3. Add CSRF token to headers
4. Test endpoints

### Using Python Requests

```python
import requests

BASE_URL = 'http://localhost:8000/api'

# Get CSRF token
session = requests.Session()
home = session.get('http://localhost:8000/')
csrf_token = home.cookies['csrftoken']

# Create meeting
headers = {'X-CSRFToken': csrf_token}
data = {
    'title': 'Test Meeting',
    'meeting_type': 'team_meeting',
    'transcript': 'Sample transcript'
}
response = session.post(f'{BASE_URL}/meetings/', json=data, headers=headers)
print(response.json())

# List meetings
response = session.get(f'{BASE_URL}/meetings/')
print(response.json())
```

---

## Performance Testing

### Load Testing with Locust

Install Locust:
```bash
pip install locust
```

Create `locustfile.py`:
```python
from locust import HttpUser, task, between

class MeetingBotUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_meetings(self):
        self.client.get("/api/meetings/")

    @task
    def get_meeting_details(self):
        self.client.get("/api/meetings/1/")
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

Access Locust UI at: http://localhost:8089

---

## Stress Testing

Test with large files:
- 50MB+ audio files
- Very long transcripts (10,000+ words)
- Rapid API requests

Monitor:
- CPU usage
- Memory consumption
- Response times
- Error rates

---

## Security Testing

### CSRF Protection
- Verify CSRF token required for POST/PUT/DELETE
- Test without token (should fail)

### SQL Injection
- Try SQL injection in search: `'; DROP TABLE--`
- Verify Django ORM prevents injection

### XSS Prevention
- Try XSS in meeting title: `<script>alert('test')</script>`
- Verify properly escaped in HTML

### File Upload Security
- Try uploading executable files
- Verify only allowed extensions accepted
- Test file size limits

---

## Browser Testing

### Desktop
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Mobile
- iOS Safari
- Android Chrome
- Responsive design verification

### Test Checklist
- [ ] Navigation works on all devices
- [ ] Forms display properly
- [ ] Buttons are clickable
- [ ] File uploads work
- [ ] Responsive at 320px, 768px, 1024px widths

---

## Django Admin Testing

1. Login to admin: http://localhost:8000/admin/
2. Verify meeting model is listed
3. Create meeting from admin
4. Edit meeting details
5. Delete meeting
6. Verify filters work (by type, status, date)
7. Search by title

---

## Error Handling Testing

### Test Invalid Input
- Empty title
- Invalid meeting type
- Invalid file format
- File size too large
- Missing transcript/file

### Test Missing Resources
- Access non-existent meeting (should 404)
- Delete already deleted meeting
- Update non-existent meeting

### Test Server Errors
- Disable API key, try to generate summary (should fail gracefully)
- Fill database, test behavior
- Simulate network timeout

---

## Accessibility Testing

Check:
- Color contrast (WCAG AA)
- Keyboard navigation
- Screen reader compatibility
- Form labels present
- Alt text on images
- ARIA attributes where needed

Use tools:
```bash
pip install axe-selenium-python
```

---

## Documentation Testing

1. Follow README setup instructions
2. Follow API documentation examples
3. Verify all links work
4. Check code examples execute
5. Verify environment setup instructions

---

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions://setup-python@v2
        with:
          python-version: 3.11
      
      - uses: actions://checkout@v2
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python manage.py test
      
      - name: Run linting
        run: flake8 meeting --max-line-length=100
```

---

## Test Automation

### Run all tests automatically

```bash
#!/bin/bash
python manage.py test
python manage.py check
flake8 meeting --max-line-length=100
coverage run --source='.' manage.py test
coverage report --fail-under=80
```

---

## Known Limitations

1. No real-time transcription (asynchronous job recommended)
2. No actual Google Meet/Zoom integration yet
3. LLM quality depends on API provider
4. Large files may take significant time to process

---

## Reporting Issues

When testing, if you find an issue:

1. Note the exact steps to reproduce
2. Record actual vs expected behavior
3. Check browser console for errors
4. Check Django logs (`python manage.py runserver` output)
5. Create GitHub issue with details

---

## Test Data

Sample transcripts for testing:

### Short Transcript
```
John: Good morning everyone. Let's start today's standup.
Mary: I finished the user authentication module.
Bob: I'm working on the payment integration. Should be done by Friday.
John: Great! Any blockers?
Mary: I need clarification on the API specs.
John: I'll send them to you this afternoon.
```

### Medium Transcript
```
[Meeting started at 10:00 AM]
Sarah: Let's review the Q1 roadmap...
[10-15 minute discussion about project milestones]
Tom: We should prioritize the mobile app...
[Discussion about resource allocation]
Sarah: Alright, let's wrap up...
[Meeting ended at 10:45 AM]
```

---

Happy testing! 🧪
