# Use a base image that includes Python and is Debian 11 (bullseye)
FROM python:3.9-slim-bullseye # <--- CHANGED FROM buster TO bullseye

# Set the working directory inside the container
WORKDIR /app

# Install LibreOffice and other necessary system dependencies
# LibreOffice is required by docx2pdf for conversion
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice-writer \
        fonts-liberation \
        unoconv \
    # Clean up apt cache to keep image size small
    && rm -rf /var/lib/apt/lists/*

# Copy your Python requirements file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application files into the container
# This includes app.py, converter_worker.py, index.html, script.js, style.css
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Set environment variables for production (FLASK_APP is needed by Gunicorn)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Command to run the application using Gunicorn (a production-ready WSGI server)
# -w 4: Run with 4 worker processes (adjust based on server resources)
# -b 0.0.0.0:5000: Bind to all network interfaces on port 5000
# app:app: Specifies your Flask application instance (app.py:app)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
