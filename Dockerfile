# Use a base image that includes Python and is Debian 11 (bullseye)
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Install LibreOffice and other necessary system dependencies for headless conversion
# LibreOffice is required by docx2pdf for conversion
# unoconv is essential for docx2pdf to interface with LibreOffice
# libreoffice-writer is the component for .docx
# fonts-liberation for better font rendering
# xvfb is a virtual framebuffer, often needed for headless GUI apps like LibreOffice
# libfontconfig1, libice6, libsm6, libxrender1, libxtst6 are common dependencies for LibreOffice
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

# Command to run the application using Gunicorn (a production-ready WSGI server)
# Use a specific display number for xvfb-run (e.g., :99) instead of --auto-display
CMD ["xvfb-run", "-a", "-s", "-screen 0 1024x768x24", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
