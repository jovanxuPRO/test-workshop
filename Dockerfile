FROM python:3.13-slim

WORKDIR /app

# Install system deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only, headless)
RUN playwright install chromium --with-deps

# Copy source
COPY main.py .
COPY static/ static/

# Create data dirs
RUN mkdir -p generated_tests

ENV TW_HOST=0.0.0.0
ENV TW_PORT=9000
ENV TW_HEADLESS=true

EXPOSE 9000

CMD ["python", "main.py"]
