# DIY Smart Assistant Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for DIY Assistant
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies for DIY Smart Assistant
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
    uvicorn[standard] \
    gunicorn \
    requests \
    python-multipart \
    beautifulsoup4 \
    openai \
    psycopg2-binary \
    bcrypt \
    passlib \
    sqlalchemy \
    pydantic

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

# Expose port
EXPOSE 8001

# Health check for DIY Assistant API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/test || exit 1

# Run with gunicorn for production performance
CMD ["gunicorn", "main_enhanced:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]