FROM selenium/standalone-chrome:latest

# Switch to root user to install Python and set up permissions
USER root

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create a directory with proper permissions for logging
RUN mkdir -p /app && chmod 777 /app
RUN mkdir -p /tmp/logs && chmod 777 /tmp/logs

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for the application
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Run the application
CMD ["python3", "crash_monitor.py"]
