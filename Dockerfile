# Base image with Python 3.11
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
  redis-server \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the application port
EXPOSE 8000

# Start Redis server
RUN mkdir -p /var/run/redis
RUN chmod 777 /var/run/redis

# Command to run Celery and Gunicorn
CMD bash -c "redis-server --daemonize yes && celery -A dependencies worker --loglevel=INFO & fastapi run --workers 4 main.py"
