# Use an official lightweight Python image
FROM python:3.12-slim

# Prevent Python from writing pyc files to disk and ensure unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Git (Required for the GitAgent checkpointing)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
# Assuming a standard requirements.txt. If using uv or poetry, adjust accordingly.
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the core source code into the container
COPY src/ /app/src/

# Execute the pipeline
CMD ["python", "-m", "src.main"]