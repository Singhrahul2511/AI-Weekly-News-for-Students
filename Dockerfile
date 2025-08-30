# Stage 1: Build stage with dependencies
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN pip install --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt


# Stage 2: Final production stage
FROM python:3.11-slim

WORKDIR /usr/src/app

# Copy python packages from builder stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install dependencies from wheels to speed up the process
RUN pip install --no-cache /wheels/*

# NLTK data for fallback summarizer
RUN python -m nltk.downloader punkt

# Copy application code
COPY . .

# Expose port and define start command
# Port will be set by Render via the $PORT environment variable
EXPOSE 8000
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]