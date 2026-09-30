# Dockerfile for National Airfare Price Index (APIx)
# Optimized for Render.com free tier deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries + OS deps
RUN playwright install chromium --with-deps

# Copy application code
COPY . .

# Initialize DB and seed baseline data at build time
RUN python reseed_live_only.py

# Render uses $PORT env var
EXPOSE ${PORT:-8000}

# Launch both FastAPI + Streamlit
CMD ["python", "start.py"]
