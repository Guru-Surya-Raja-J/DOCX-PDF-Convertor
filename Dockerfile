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

# --- CRITICAL CHANGE: Set PYTHONPATH for pyuno ---
# This tells Python where to find the 'uno' module required by unoconv.
# The path might vary slightly based on LibreOffice version, but this is common for Debian.
ENV PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH

# Copy your Python requirements file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application files into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Set environment variables for production (FLASK_APP is needed by Gunicorn)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# --- CMD to test unoconv directly ---
# This CMD will attempt to convert a dummy DOCX to PDF using unoconv on container startup.
# This will generate logs even if the Flask app doesn't start properly.
# We'll temporarily use this to debug unoconv, then revert to Gunicorn.
# --- CRITICAL CHANGE: Reduced Gunicorn workers to 1 (-w 1) ---
CMD ["/bin/bash", "-c", " \
    echo 'This is a test document.' > test.docx && \
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & \
    export DISPLAY=:99 && \
    unoconv -f pdf -o test.pdf test.docx && \
    echo 'unoconv test conversion completed.' && \
    ls -l && \
    gunicorn -w 1 -b 0.0.0.0:5000 app:app \
"]
