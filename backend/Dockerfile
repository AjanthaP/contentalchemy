# Version 0.1.1
# Dockerfile for FastAPI backend (Railway deployment)
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
#RUN apt-get update && apt-get install -y build-essential libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/ ./src/
COPY src/api/ ./src/api/
COPY src/agents/ ./src/agents/
COPY src/core/ ./src/core/

# Expose port for FastAPI
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
