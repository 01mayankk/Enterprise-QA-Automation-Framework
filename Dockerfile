# Use python slim base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and Google Chrome repository keys
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome repository and install Google Chrome Stable
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set workspace directory inside the container
WORKDIR /usr/src/app

# Copy dependency definition and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project modules and directories into the container
COPY . .

# Create log, reports, and screenshots directories to avoid permission errors
RUN mkdir -p logs reports screenshots

# Execute pytest headless suite by default
CMD ["pytest", "-v", "--headless", "--html=reports/report.html", "--self-contained-html"]
