#/backend/Dockerfile
FROM python:3.13.12-slim-trixie

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    odbc-postgresql \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to app directory (optional)
WORKDIR /app

# Copy Python dependencies first
COPY requirements_lock.txt .
RUN pip install --no-cache-dir -r requirements_lock.txt

# Copy app folder
COPY . /app/backend

RUN useradd --create-home appuser

USER appuser

EXPOSE 8000

# Start Uvicorn pointing to the app package
CMD [
    "uvicorn",
    "backend.app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--proxy-headers"
    ]