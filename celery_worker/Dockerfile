# Use the same lightweight base image for the Celery worker
FROM python:3.12-slim AS worker_base

# Set the working directory for the Celery worker
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies for the Celery worker
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build the Celery worker
FROM worker_base AS worker

# Copy the entire application for the Celery worker
COPY . .

# Command to run the Celery worker
CMD ["celery", "-A", "api.celery", "worker", "--loglevel=info"]
