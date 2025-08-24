# ----------------------------
# Dockerfile for Selenium + Chrome on Render
# ----------------------------
FROM python:3.11-slim

# System deps Chrome needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip gnupg ca-certificates \
    fonts-liberation libasound2 libnspr4 libnss3 libx11-6 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 \
    libxrender1 libxtst6 libxkbcommon0 libatk-bridge2.0-0 libgtk-3-0 \
    libdrm2 libgbm1 libatspi2.0-0 libu2f-udev xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (stable)
RUN mkdir -p /usr/share/keyrings && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
      | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# (Optional) Install a matching ChromeDriver into the image
# webdriver-manager can also handle this at runtime (your script uses it).
RUN CHROME_MAJOR=$(google-chrome --version | sed 's/.* \([0-9]*\)\..*/\1/') && \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}") && \
    curl -Lo /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && rm /tmp/chromedriver.zip

ENV CHROME_BIN=/usr/bin/google-chrome \
    CHROMEDRIVER=/usr/local/bin/chromedriver \
    DISPLAY=:99 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Run as a non-root user for safety
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Start your script
CMD ["python", "crash_predictor.py"]
