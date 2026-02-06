# Deployment Guide

This document shows simple options to deploy the Meeting Bot application.

Prerequisites
- Docker & Docker Compose (for container deployment)
- An environment file `.env` with secrets (do NOT commit this)
- Optional: PostgreSQL for production

1) Local Docker (quick)

Build and run:

```bash
# from project root
docker build -t meeting-bot .
docker run --env-file .env -p 8000:8000 meeting-bot
```

Or with docker-compose (recommended for DB):

```bash
docker-compose up --build
```

Then open http://localhost:8000

2) Heroku (quick PaaS)

- Ensure `Procfile` exists (created)
- Create a Heroku app and set config vars from your `.env` (OPENAI_API_KEY, SECRET_KEY, etc.)

Commands:

```bash
heroku create your-app-name
git push heroku main
heroku config:set DEBUG=False
heroku config:set OPENAI_API_KEY=sk-...
heroku run python manage.py migrate
heroku open
```

3) VPS / Cloud VM (Docker recommended)

- Install Docker on VM
- Copy `.env` and run `docker-compose up -d --build`
- Configure reverse proxy (Nginx) and TLS (Let's Encrypt)

Notes
- For static files in production, either serve via CDN/S3 or use WhiteNoise.
- Configure `ALLOWED_HOSTS` in `.env`.
- Set `DEBUG=False` in production and provide a secure `SECRET_KEY`.

Troubleshooting
- If you get issues with file permissions, ensure `MEDIA_ROOT` volume is writeable.
- Check logs: `docker-compose logs -f web`

Security
- Never commit `.env` with secrets
- Rotate API keys regularly
- Use HTTPS in production

