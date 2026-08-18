FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /srv/app
USER appuser

EXPOSE 8000

# Apply migrations, then serve with gunicorn.
CMD ["sh", "-c", "flask --app wsgi db upgrade && gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app"]
