FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN apt-get update && apt-get install -y certbot && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic

EXPOSE 5555 5556
CMD ["gunicorn", "-c", "app/gunicorn_conf.py", "app.main:app"]

