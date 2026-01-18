FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by Pathway
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libsodium-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    pathway[xpack-llm] \
    google-generativeai \
    python-dotenv \
    requests

# Copy application files
COPY main.py .
COPY news_connector.py .

# Expose port for the API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "main.py"]
