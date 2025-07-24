📄 DOCX to PDF Converter
Effortless Word to PDF Conversion | Built with Python & Flask

A seamless web application that converts Microsoft Word .docx documents into high-quality .pdf format using local processing. It features a clean frontend UI, robust backend, and secure Cloudinary integration for backup storage.

🚀 Features
✅ DOCX to PDF Conversion
Converts .docx files to .pdf while retaining original formatting.

⚙️ Local Processing
Uses LibreOffice or Microsoft Word for server-side conversion without relying on third-party APIs.

🌐 User-Friendly Interface
A minimal and intuitive frontend for smooth file uploads and downloads.

⬇️ Automatic Downloads
PDFs are downloaded immediately after conversion.

☁️ Cloud Storage
Converted files are backed up securely on Cloudinary with the original filenames.

📱 Responsive Design
Optimized for desktops, tablets, and mobile devices.

🧹 Temporary File Cleanup
Automatically deletes temp files after download and upload.

🧰 Tech Stack
🖥️ Frontend
HTML5, CSS3, JavaScript (ES6+)

🔧 Backend
Python 3.x, Flask, Flask-CORS

docx2pdf for conversion

Cloudinary SDK for secure storage

subprocess for background task handling

gunicorn for production deployment

🧩 External Dependencies
LibreOffice (Linux/macOS) or Microsoft Word (Windows)

📁 Project Structure
pgsql
Copy
Edit
.
├── app.py                 # Flask backend
├── converter_worker.py    # Background conversion process
├── index.html             # Frontend HTML
├── script.js              # JavaScript logic
├── style.css              # CSS styling
├── requirements.txt       # Python dependencies
├── Procfile               # For PaaS deployment
├── .gitignore             # Git exclusions
├── uploads/               # Temp DOCX files
└── converted/             # Temp PDF files
🛠️ Local Development Setup
1. Clone the Repository
bash
Copy
Edit
git clone <your_repository_url>
cd <your_project_directory>
2. Setup Virtual Environment & Install Dependencies
bash
Copy
Edit
python -m venv venv
# Activate (Windows)
.\venv\Scripts\activate
# OR macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
3. Install LibreOffice or Microsoft Word
Linux:

bash
Copy
Edit
sudo apt update
sudo apt install libreoffice-writer fonts-liberation
macOS: Download LibreOffice

Windows: Ensure MS Word is installed and accessible

4. Configure Cloudinary API
Option A: Quick Test (Not for production)
Update app.py:

python
Copy
Edit
api_secret="YOUR_ACTUAL_CLOUDINARY_API_SECRET"
Option B: Recommended (.env setup)
bash
Copy
Edit
# .env
CLOUDINARY_API_SECRET="YOUR_ACTUAL_SECRET"
Add this line in app.py:

python
Copy
Edit
from dotenv import load_dotenv
load_dotenv()
▶️ Run Locally
Start Flask server:

bash
Copy
Edit
python app.py
Open index.html in your browser to start converting files.

🌍 Deployment
⚙️ Backend
Recommended: Render, Heroku, or Dockerized solutions on Google Cloud / AWS

Ensure LibreOffice or MS Word is included in the deployment environment

🌐 Frontend
Host index.html, script.js, and style.css on:

Netlify

Vercel

GitHub Pages

Update backendUrl in script.js to point to your deployed API.

🧪 Troubleshooting
Error	Solution
Cannot read/set properties of null	Check element IDs in index.html, ensure script.js is loaded correctly
Local conversion failed	Ensure LibreOffice/MS Word is installed and in the system PATH
PermissionError [WinError 32]	Use subprocess.run() and proper cleanup via @after_this_request
name 'sys' is not defined	Add import sys to the top of app.py
UI not resetting	Ensure resetUI() exists in the latest script.js and do a hard refresh (Ctrl+Shift+R)

📜 License
This project is licensed under the MIT License.
Feel free to use, modify, and distribute with credit.
