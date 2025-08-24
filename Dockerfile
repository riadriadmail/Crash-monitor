FROM selenium/standalone-chrome:latest

# Switch to root user to install Python
USER root

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Switch back to selenium user for security
USER seluser

# Run the application
CMD ["python3", "crash_monitor.py"]
