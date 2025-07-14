# backend.dockerfile
# ------------------
# This Dockerfile sets up the environment for running the FastAPI backend service for LLM vulnerability scanning.

# Use the official lightweight Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Set the timezone to America/Toronto
ENV TZ=America/Toronto
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi uvicorn[standard] httpx

# Copy the application code into the container
COPY . .

# Expose port 5000 for the FastAPI service
EXPOSE 5000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# Example usage:
# docker run --rm -p 5000:5000 [image-name]