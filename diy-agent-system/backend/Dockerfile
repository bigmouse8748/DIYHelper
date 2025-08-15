# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install uvicorn[standard] requests python-multipart

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p uploads

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/api/test')" || exit 1

# Run the application with the enhanced main file (includes authentication)
# Use main_enhanced for auth features, or main_simple for basic version
CMD ["uvicorn", "main_enhanced:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1", "--log-level", "info"]