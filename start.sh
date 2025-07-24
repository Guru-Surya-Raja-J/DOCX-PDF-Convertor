#!/bin/bash

# Start Xvfb (virtual display server) in the background
# :99 is a common display number
# -screen 0 1024x768x24 sets screen 0 to 1024x768 resolution with 24-bit color depth
# > /dev/null 2>&1 redirects stdout and stderr to null to keep logs clean
# & runs the command in the background
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Set the DISPLAY environment variable so LibreOffice knows which virtual display to use
export DISPLAY=:99

# Start LibreOffice in headless mode in the background
# --headless: runs without a graphical user interface
# --invisible: makes it invisible (no splash screen)
# --nocrashreport: disables crash reporter
# --nodefault: doesn't open a new empty document
# --nofirststartwizard: disables the first start wizard
# --nologo: disables the splash screen
# --norestore: doesn't restore previous session
# & runs the command in the background
libreoffice --headless --invisible --nocrashreport --nodefault --nofirststartwizard --nologo --norestore &

# Give LibreOffice a moment to fully start up and initialize
# This is crucial to prevent docx2pdf from failing if LibreOffice isn't ready
sleep 5

# Start Gunicorn (your Flask application server)
# -w 4: 4 worker processes
# -b 0.0.0.0:5000: binds to all network interfaces on port 5000
# app:app: your Flask app instance
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
