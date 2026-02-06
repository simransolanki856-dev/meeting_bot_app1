# Meeting Bot Summarizer Web App

A powerful Django-based web application that automatically summarizes meeting recordings or transcripts using AI. Extract key discussion points, decisions, action items, and agenda topics with ease.

## 🌟 Features

- **Easy Upload & Paste**: Support for multiple audio formats (MP3, WAV, MP4, WebM, M4A) or paste transcripts directly
- **AI-Powered Summaries**: Leverages OpenAI GPT, Google Gemini, or HuggingFace for intelligent summarization
- **Structured Output**: Get organized summaries, key points, decisions, action items, and agenda breakdown
- **Audio Transcription**: Automatic speech-to-text conversion using OpenAI Whisper or Google Cloud Speech-to-Text
- **Meeting History**: Search, filter, and manage all your past meeting summaries
- **Download Options**: Export summaries as TXT files (PDF support coming soon)
- **Responsive UI**: Clean, modern interface that works on desktop, tablet, and mobile
- **Secure Storage**: SQLite database with secure file handling
- **Admin Dashboard**: Django admin interface for managing meetings

## 📋 Tech Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - REST API implementation
- **Django CORS Headers** - Cross-Origin Resource Sharing
- **SQLite** - Default database (PostgreSQL ready)

### Frontend
- **HTML5/CSS3** - Markup and styling
- **Bootstrap 5** - Responsive UI framework
- **JavaScript (Vanilla)** - Interactive features
- **jQuery** - DOM manipulation and AJAX

### AI & LLM Integration
- **OpenAI** - GPT models for summarization and Whisper for transcription
- **Google Generative AI** - Gemini models for summarization
- **HuggingFace** - Alternative LLM and summarization models

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool (venv or conda)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd meeting_bot
```

2. **Create and activate virtual environment**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-your-key-here
# GOOGLE_API_KEY=your-key-here
```

5. **Apply database migrations**
```bash
python manage.py migrate
```

6. **Create a superuser (optional, for admin access)**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Home: `http://localhost:8000/`
- Create Meeting: `http://localhost:8000/create/`
- Meeting History: `http://localhost:8000/history/`
- Admin Panel: `http://localhost:8000/admin/`

## 📖 Usage

### Creating a Meeting Summary

1. **Navigate to Create Meeting** page
2. **Enter Meeting Details**:
   - Title (required)
   - Meeting Type (Team Meeting, Interview, Client Call, Standup, Other)
   - Description (optional)
   - Meeting Date (defaults to current time)

3. **Provide Meeting Content** (choose one):
   - **Paste Transcript**: Copy and paste the meeting transcript
   - **Upload Recording**: Upload an audio/video file (MP3, WAV, MP4, WebM, M4A)

4. **Click "Generate Summary"** and wait for processing

5. **View Results** with:
   - Summary overview
   - Key discussion points
   - Decisions made
   - Action items (with owner and due date if available)
   - Agenda/topic breakdown
   - Original transcript

### Accessing Meeting History

1. **Go to Meeting History** page
2. **Search** by meeting title
3. **Filter** by meeting type
4. **View** meeting details
5. **Delete** meetings as needed

## 🔧 API Endpoints

### Meetings API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetings/` | List all meetings |
| POST | `/api/meetings/` | Create a new meeting |
| GET | `/api/meetings/{id}/` | Retrieve meeting details |
| PUT | `/api/meetings/{id}/` | Update a meeting |
| DELETE | `/api/meetings/{id}/` | Delete a meeting |
| POST | `/api/meetings/{id}/regenerate_summary/` | Regenerate summary |
| GET | `/api/meetings/{id}/download_summary/` | Download summary |

### Query Parameters

```bash
# Search by title
GET /api/meetings/?search=quarterly

# Filter by type
GET /api/meetings/?meeting_type=team_meeting

# Pagination
GET /api/meetings/?page=2

# Combine filters
GET /api/meetings/?search=product&meeting_type=team_meeting&page=1
```

## 🔐 Environment Variables

### Required
```env
SECRET_KEY=your-django-secret-key
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1
```

### LLM Configuration
```env
# Choose one: openai, google, huggingface
TRANSCRIPTION_SERVICE=openai

# OpenAI (for GPT-3.5/4 and Whisper)
OPENAI_API_KEY=sk-your-openai-api-key

# Google (for Gemini and Cloud Speech-to-Text)
GOOGLE_API_KEY=your-google-api-key

# HuggingFace
HUGGINGFACE_API_KEY=hf_your-token
```

### Optional
```env
# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (optional file storage)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
```

## 📊 Database Models

### Meeting Model
```python
- title (CharField): Meeting title
- meeting_type (CharField): Type of meeting
- description (TextField): Optional description
- transcript (TextField): Meeting transcript
- recording_file (FileField): Uploaded audio/video
- summary_json (JSONField): AI-generated summary
- status (CharField): pending, processing, completed, failed
- created_at (DateTimeField): Creation timestamp
- updated_at (DateTimeField): Last update timestamp
- meeting_date (DateTimeField): When the meeting occurred
```

## 🎨 UI Pages

### Page 1: Create Meeting
- Meeting title input
- Meeting type dropdown
- Paste transcript tab
- Upload recording tab
- File drag-and-drop support
- Loading animation
- Error handling

### Page 2: Meeting Summary Result
- Structured tabs for different sections
- Summary overview card
- Key points list
- Decisions list
- Action items table
- Agenda breakdown
- Download options
- Delete functionality

### Page 3: Meeting History Dashboard
- Searchable meeting list
- Filter by meeting type
- Status badges
- Pagination
- Quick actions (view/delete)
- Empty state messaging

## 🔄 Workflow

```
Upload/Paste → Validate → Extract Transcript (if audio) → Generate Summary → Display Results → Download/Share
```

## 📝 Summary Format

The AI generates a structured JSON with:
```json
{
  "summary": "2-3 sentence overview of the meeting",
  "key_points": ["point 1", "point 2", "point 3"],
  "decisions": ["decision 1", "decision 2"],
  "action_items": [
    {
      "task": "Complete report",
      "owner": "John Doe",
      "due_date": "2024-01-15"
    }
  ],
  "agenda": [
    {
      "topic": "Project Updates",
      "description": "Reviewed progress on current projects"
    }
  ]
}
```

## 🚀 Deployment

### Heroku
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-key
git push heroku main
heroku run python manage.py migrate
```

### AWS/Azure/DigitalOcean
1. Install dependencies
2. Run migrations: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Set environment variables in your hosting platform
5. Run with Gunicorn: `gunicorn meeting_bot.wsgi:application`

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "meeting_bot.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📱 Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## ⚠️ Important Notes

1. **API Keys**: Never commit API keys to version control. Use environment variables.
2. **CSRF Token**: All POST/PUT/DELETE requests require CSRF token (automatically handled by Django).
3. **File Size**: Maximum upload size is 100MB (configurable in settings).
4. **Audio Formats**: Supported: MP3, WAV, MP4, WebM, M4A
5. **Transcription**: Large files may take time to transcribe. Transcription time depends on file length.

## 🐛 Troubleshooting

### Issue: "Module not found" errors
```bash
pip install -r requirements.txt
```

### Issue: Database errors
```bash
python manage.py migrate
python manage.py migrate --run-syncdb
```

### Issue: Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Issue: API Key errors
- Verify .env file exists and is correctly configured
- Check API key validity
- Ensure API has necessary permissions

## 📞 Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Email: [support-email]

## 🎯 Future Enhancements

- [ ] PDF export with formatting
- [ ] Real-time meeting join capability (Google Meet/Zoom integration)
- [ ] Multi-language support
- [ ] Meeting templates
- [ ] Team collaboration features
- [ ] Email notifications
- [ ] Slack/Teams integration
- [ ] Custom summarization templates
- [ ] Advanced analytics
- [ ] User authentication and profiles

## 📊 Project Structure

```
meeting_bot/
├── meeting_bot/              # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
├── meeting/                  # Main app
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── serializers.py       # DRF serializers
│   ├── llm_service.py       # LLM integration
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # App URLs
│   ├── templates/           # HTML templates
│   │   └── meeting/
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── create_meeting.html
│   │       ├── meeting_result.html
│   │       └── meeting_history.html
│   └── static/              # Static files
│       └── meeting/
│           ├── css/
│           │   └── style.css
│           └── js/
│               ├── main.js
│               ├── create_meeting.js
│               ├── meeting_result.js
│               └── meeting_history.js
├── media/                    # User uploads
├── manage.py                # Django management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

---

**Happy summarizing! 🎉**
