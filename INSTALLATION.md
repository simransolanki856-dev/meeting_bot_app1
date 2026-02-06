# Installation & Setup Guide

## System Requirements

- **Python**: 3.8 or higher
- **pip**: Package manager for Python
- **Virtual Environment**: Recommended (venv or conda)
- **Disk Space**: ~500MB
- **RAM**: 2GB minimum

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd meeting_bot
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Django 4.2.7
- Django REST Framework
- CORS headers support
- LLM integration libraries (OpenAI, Google, HuggingFace)
- Database and utility packages

### 4. Configure Environment Variables

**Copy the example .env file:**
```bash
cp .env.example .env
```

**Edit .env and add your configuration:**
```env
# Django
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# LLM Service
TRANSCRIPTION_SERVICE=openai
OPENAI_API_KEY=sk-your-api-key
```

### 5. Run Migrations

```bash
python manage.py migrate
```

Or use the setup script:
```bash
python setup.py
```

### 6. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account:
- Username: `admin`
- Email: `admin@example.com`
- Password: (set your password)

### 7. Run Development Server

```bash
python manage.py runserver
```

You should see output like:
```
Starting development server at http://127.0.0.1:8000/
```

### 8. Access the Application

Open your browser and navigate to:
- **Home Page**: http://localhost:8000/
- **Create Meeting**: http://localhost:8000/create/
- **Meeting History**: http://localhost:8000/history/
- **Admin Panel**: http://localhost:8000/admin/ (if superuser created)

## API Keys Setup

### OpenAI Setup

1. **Get API Key**:
   - Visit https://platform.openai.com/api-keys
   - Sign up or log in
   - Create a new API key
   - Copy the key

2. **Add to .env**:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   TRANSCRIPTION_SERVICE=openai
   ```

3. **Verify** by checking the LLM service usage in app

### Google Gemini Setup

1. **Get API Key**:
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key

2. **Add to .env**:
   ```env
   GOOGLE_API_KEY=your-google-key
   TRANSCRIPTION_SERVICE=google
   ```

### HuggingFace Setup

1. **Get API Key**:
   - Visit https://huggingface.co/settings/tokens
   - Create a new token
   - Copy the token

2. **Add to .env**:
   ```env
   HUGGINGFACE_API_KEY=hf_your-token
   TRANSCRIPTION_SERVICE=huggingface
   ```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution**: Install Django
```bash
pip install django==4.2.7
```

### Issue: "ModuleNotFoundError: No module named 'decouple'"

**Solution**: Install python-decouple
```bash
pip install python-decouple
```

### Issue: "Database error: no such table"

**Solution**: Run migrations
```bash
python manage.py migrate
python manage.py migrate --run-syncdb
```

### Issue: "Static files not loading"

**Solution**: Collect static files
```bash
python manage.py collectstatic --clear --noinput
```

### Issue: "Port 8000 is already in use"

**Solution**: Use a different port
```bash
python manage.py runserver 8001
```

Then access at http://localhost:8001/

### Issue: "CORS error in browser console"

**Solution**: Check CORS_ALLOWED_ORIGINS in settings.py:
```python
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
```

### Issue: "API key not working"

**Solution**:
1. Verify API key is correct
2. Check `.env` file is loaded
3. Ensure API has proper permissions
4. Check API quota/billing

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Access Django shell
python manage.py shell

# Create/reset database
python manage.py flush

# Check for issues
python manage.py check

# Show URLs
python manage.py show_urls
```

## Production Deployment

### Using Gunicorn

1. **Install Gunicorn**:
```bash
pip install gunicorn
```

2. **Create wsgi.py** (already exists at `meeting_bot/wsgi.py`)

3. **Run with Gunicorn**:
```bash
gunicorn meeting_bot.wsgi:application --bind 0.0.0.0:8000
```

### Heroku Deployment

1. **Install Heroku CLI**
2. **Create Procfile**:
```
web: gunicorn meeting_bot.wsgi
release: python manage.py migrate
```

3. **Deploy**:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "meeting_bot.wsgi:application", "--bind", "0.0.0.0:8000"]
```

2. **Build and run**:
```bash
docker build -t meeting-bot .
docker run -p 8000:8000 meeting-bot
```

## Development Tips

### Enable Debug Mode
```python
# In .env
DEBUG=True
```

### Use Django Extensions
```bash
pip install django-extensions
```

Then in `INSTALLED_APPS`:
```python
'django_extensions',
```

### Database Visualization
```bash
python manage.py graph_models -a -o models.png
```

### Auto-reload on Changes
```bash
python manage.py runserver --reload
```

## Next Steps

1. Create your first meeting
2. Test with sample transcript
3. Configure your preferred LLM service
4. Explore the admin panel
5. Customize templates as needed

## Need Help?

- Check [README.md](README.md) for feature documentation
- Review [API Documentation](API.md) for endpoint details
- Check existing GitHub issues
- Create a new issue with detailed description

---

Happy coding! 🚀
