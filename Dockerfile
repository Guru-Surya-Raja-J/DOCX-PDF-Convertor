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

# Copy all your application files into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Set environment variables for production (FLASK_APP is needed by Gunicorn)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# --- CRITICAL CHANGE: CMD to test LibreOffice directly ---
# This CMD will attempt to convert a dummy DOCX to PDF on container startup.
# This will generate logs even if the Flask app doesn't start properly.
# We'll temporarily use this to debug LibreOffice, then revert to Gunicorn.
CMD ["/bin/bash", "-c", " \
    echo 'This is a test document.' > test.docx && \
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & \
    export DISPLAY=:99 && \
    libreoffice --headless --invisible --nocrashreport --nodefault --nofirststartwizard --nologo --norestore --convert-to pdf test.docx --outdir . && \
    echo 'LibreOffice test conversion completed.' && \
    ls -l && \
    gunicorn -w 4 -b 0.0.0.0:5000 app:app \
"]
