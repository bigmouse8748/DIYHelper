# DIY Smart Assistant V2 Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/base.txt requirements/prod.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r prod.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Production environment variables (will be overridden by ECS task definition)
ENV DEBUG=false
ENV PORT=8001
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/v1/health || exit 1

# Run with gunicorn for production performance
CMD ["gunicorn", "app.main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]