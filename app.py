# app.py
from flask import Flask, request, jsonify, send_file, after_this_request
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import os
import sys
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration ---
cloudinary.config(
    cloud_name="dfw70yvoj",
    api_key="341129283697132",
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# --- Health Check Endpoint (remains the same) ---
@app.route("/health", methods=["GET"])
def health_check():
    print("Health check endpoint hit!")
    sys.stdout.flush()
    try:
        result = subprocess.run(["libreoffice", "--version"], capture_output=True, text=True, check=True, timeout=10)
        print(f"LibreOffice --version output: {result.stdout.strip()}")
        sys.stdout.flush()
        return jsonify({
            "status": "ok",
            "message": "Backend is running and LibreOffice appears accessible.",
            "libreoffice_version": result.stdout.strip().split('\n')[0]
        }), 200
    except FileNotFoundError:
        print("Health check failed: LibreOffice command not found.")
        sys.stdout.flush()
        return jsonify({"status": "error", "message": "LibreOffice command not found."}), 500
    except subprocess.CalledProcessError as e:
        print(f"Health check failed: LibreOffice exited with error. Stderr: {e.stderr}")
        sys.stdout.flush()
        return jsonify({"status": "error", "message": f"LibreOffice command failed: {e.stderr}"}), 500
    except Exception as e:
        print(f"Health check failed: Unexpected error - {e}")
        sys.stdout.flush()
        return jsonify({"status": "error", "message": f"Health check failed: {str(e)}"}), 500

@app.route("/convert", methods=["POST"])
def convert_file():
    print("Convert endpoint hit!")
    sys.stdout.flush()
    if 'file' not in request.files:
        print("Error: No file provided.")
        sys.stdout.flush()
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith(".docx"):
        print("Error: Invalid file type.")
        sys.stdout.flush()
        return jsonify({"error": "Only .docx files are allowed for conversion to PDF."}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf_filename = filename.replace(".docx", ".pdf")
    output_path = os.path.join(CONVERTED_FOLDER, pdf_filename)
    
    try:
        file.save(input_path)
        print(f"File saved locally: {input_path}")
        sys.stdout.flush()

        print(f"Calling converter_worker.py for conversion: {input_path} -> {output_path}")
        sys.stdout.flush()
        
        python_executable = sys.executable if hasattr(sys, 'executable') else 'python'
        
        command = [python_executable, os.path.join(os.path.dirname(__file__), 'converter_worker.py'), input_path, output_path]
        
        env_vars = os.environ.copy()
        env_vars["DISPLAY"] = ":99"
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=300, env=env_vars)
            print(f"Subprocess stdout:\n{result.stdout}")
            print(f"Subprocess stderr:\n{result.stderr}")
            print(f"Conversion successful via subprocess. PDF saved at: {output_path}")
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            print(f"Error during subprocess conversion: {e}")
            print(f"Subprocess stdout (on error):\n{e.stdout}")
            print(f"Subprocess stderr (on error):\n{e.stderr}")
            sys.stdout.flush()
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({
                "error": "Local conversion failed. Check server logs for details. (Possibly LibreOffice/unoconv issue)",
                "details": e.stderr if e.stderr else str(e)
            }), 500
        except FileNotFoundError:
            print("Error: Python executable or converter_worker.py not found in subprocess.")
            sys.stdout.flush()
            return jsonify({
                "error": "Python executable or converter_worker.py not found. Check server setup.",
                "details": "Ensure Python is in PATH and converter_worker.py is in the same directory."
            }), 500
        except subprocess.TimeoutExpired:
            print("Error: Subprocess timed out.")
            sys.stdout.flush()
            return jsonify({
                "error": "Conversion process timed out. File might be too large or LibreOffice is slow to start.",
                "details": "Subprocess exceeded 300 seconds timeout."
            }), 504
        except Exception as e:
            print(f"Unexpected error when running subprocess: {e}")
            sys.stdout.flush()
            return jsonify({
                "error": "An unexpected error occurred during subprocess call.",
                "details": str(e)
            }), 500

        print(f"Uploading {pdf_filename} to Cloudinary...")
        sys.stdout.flush()
        base_filename_no_ext = os.path.splitext(filename)[0]
        cloudinary.uploader.upload(
            output_path, 
            resource_type="raw", 
            folder="converted_docs", 
            public_id=base_filename_no_ext
        )
        print(f"Uploaded to Cloudinary (for storage) with public_id: {base_filename_no_ext}.pdf")
        sys.stdout.flush()

        @after_this_request
        def remove_output_file(response):
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"Deferred deletion successful: {output_path}")
                    sys.stdout.flush()
            except Exception as e:
                print(f"Error during deferred deletion of {output_path}: {e}")
                sys.stdout.flush()
            return response

        print(f"Sending {pdf_filename} to the user for download.")
        sys.stdout.flush()
        return send_file(output_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')

    except Exception as e:
        print(f"An unexpected error occurred in convert_file: {e}")
        sys.stdout.flush()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
            print(f"Deleted temporary input file: {input_path}")
            sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
