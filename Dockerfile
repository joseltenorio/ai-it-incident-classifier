# Dockerfile

# Use a slim Python image to keep the runtime container lightweight.
FROM python:3.12-slim

# Prevent Python from writing .pyc files and force unbuffered logs.
# Unbuffered logs are useful because Cloud Run captures stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cloud Run injects PORT at runtime. We provide a default for local Docker runs.
ENV PORT=8080

# Create the application working directory.
WORKDIR /app

# Install system dependencies required by some Python packages at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to improve Docker layer caching.
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY app ./app

# Expose the default Cloud Run port.
EXPOSE 8080

# Cloud Run requires the container to listen on 0.0.0.0 and the configured PORT.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]