FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Default command (can override in docker-compose)
CMD ["celery", "-A", "email_campaign_system", "worker", "--loglevel=info"]
