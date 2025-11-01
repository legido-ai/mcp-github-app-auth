FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache \
    gcc \
    g++ \
    git \
    musl-dev \
    libffi-dev \
    openssl-dev

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install dependencies using pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip list > pip-list.txt

# Copy the application code
COPY . .

# Install the current package in development mode
RUN pip install -e .

# Create a non-root user
RUN adduser -D appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 777 /app
# Give the appuser write access to common directories
RUN chmod 777 /tmp && mkdir -p /tmp/quote-agent && chmod 777 /tmp/quote-agent
USER appuser

CMD ["python", "-u", "-m", "mcp_github_app.server"]