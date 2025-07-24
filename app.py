from flask import Flask, request, jsonify, send_file, after_this_request
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import os
import time     # convertor.py                                          
import sys
import json
import subprocess # Import subprocess module
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration ---
cloudinary.config(
    cloud_name="dfw70yvoj",
    api_key="341129283697132",
    api_secret="RcKassb-vBQhiTXDWE-TZ-nnmYs" # <--- REPLACE THIS WITH YOUR ACTUAL CLOUDINARY API SECRET
)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route("/convert", methods=["POST"])
def convert_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith(".docx"):
        return jsonify({"error": "Only .docx files are allowed for conversion to PDF."}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf_filename = filename.replace(".docx", ".pdf")
    output_path = os.path.join(CONVERTED_FOLDER, pdf_filename)
    
    try:
        file.save(input_path)
        print(f"File saved locally: {input_path}")

        # --- Call converter_worker.py as a subprocess ---
        print(f"Calling converter_worker.py for conversion: {input_path} -> {output_path}")
        
        # Get the path to the Python executable
        python_executable = sys.executable if hasattr(sys, 'executable') else 'python'
        
        # Construct the command to run the worker script
        command = [python_executable, os.path.join(os.path.dirname(__file__), 'converter_worker.py'), input_path, output_path]
        
        try:
            # Run the subprocess. capture_output=True captures stdout/stderr
            # text=True decodes stdout/stderr as text
            # check=True raises CalledProcessError if the command returns a non-zero exit code
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"Subprocess stdout:\n{result.stdout}")
            print(f"Subprocess stderr:\n{result.stderr}")
            print(f"Conversion successful via subprocess. PDF saved at: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during subprocess conversion: {e}")
            print(f"Subprocess stdout (on error):\n{e.stdout}")
            print(f"Subprocess stderr (on error):\n{e.stderr}")
            return jsonify({
                "error": "Local conversion failed via subprocess. Check server logs for details.",
                "details": e.stderr if e.stderr else str(e)
            }), 500
        except FileNotFoundError:
            return jsonify({
                "error": "Python executable or converter_worker.py not found. Check server setup.",
                "details": "Ensure Python is in PATH and converter_worker.py is in the same directory."
            }), 500
        except Exception as e:
            print(f"Unexpected error when running subprocess: {e}")
            return jsonify({
                "error": "An unexpected error occurred during subprocess call.",
                "details": str(e)
            }), 500

        # --- Upload to Cloudinary (copy for your records/storage) ---
        print(f"Uploading {pdf_filename} to Cloudinary...")
        base_filename_no_ext = os.path.splitext(filename)[0]
        cloudinary.uploader.upload(
            output_path, 
            resource_type="raw", 
            folder="converted_docs", 
            public_id=base_filename_no_ext # Use original filename as public_id
        )
        print(f"Uploaded to Cloudinary (for storage) with public_id: {base_filename_no_ext}.pdf")

        # --- Defer deletion of the output file until after the response is sent ---
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"Deferred deletion successful: {output_path}")
            except Exception as e:
                print(f"Error during deferred deletion of {output_path}: {e}")
            return response

        # --- Send the converted PDF file directly to the user ---
        print(f"Sending {pdf_filename} to the user for download.")
        return send_file(output_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        # --- Cleanup: Only delete input file here. Output file deletion is deferred. ---
        if os.path.exists(input_path):
            os.remove(input_path)
            print(f"Deleted temporary input file: {input_path}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
