# Use a base image that includes Python and is Debian 11 (bullseye)
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Install LibreOffice and other necessary system dependencies for headless conversion
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice-writer \
        fonts-liberation \
        unoconv \
        xvfb \
        libfontconfig1 \
        libice6 \
        libsm6 \
        libxrender1 \
        libxtst6 \
        xauth \
        default-jre \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy your Python requirements file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the start.sh script and make it executable
COPY start.sh .
RUN chmod +x start.sh

# Copy all your application files into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Set environment variables for production (FLASK_APP is needed by Gunicorn)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# --- CRITICAL CHANGE: Use start.sh as the entry point ---
CMD ["./start.sh"]

