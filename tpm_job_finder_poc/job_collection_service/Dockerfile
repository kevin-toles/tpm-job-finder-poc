# Job Collection Service Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create storage directory
RUN mkdir -p /app/job_storage

# Set environment variables
ENV JOB_COLLECTION_STORAGE_PATH=/app/job_storage
ENV JOB_COLLECTION_ENABLE_REMOTEOK=true
ENV JOB_COLLECTION_MAX_JOBS_PER_SOURCE=50
ENV JOB_COLLECTION_TIMEOUT_SECONDS=30

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -m tpm_job_finder_poc.job_collection_service.main health

# Default command (API server)
CMD ["python", "-m", "tpm_job_finder_poc.job_collection_service.main", "serve", "--host", "0.0.0.0", "--port", "8000"]

# Alternative commands:
# CMD ["python", "-m", "tpm_job_finder_poc.job_collection_service.main", "collect", "Technical Project Manager"]
# CMD ["python", "-m", "tpm_job_finder_poc.job_collection_service.main", "sources"]