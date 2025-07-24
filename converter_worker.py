# converter_worker.py
import sys
import os
import subprocess # Import subprocess for direct unoconv call

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python converter_worker.py <input_docx_path> <output_pdf_path>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        # --- CRITICAL CHANGE: Use unoconv directly via subprocess ---
        # unoconv is a command-line utility that converts documents using LibreOffice.
        # It's generally more reliable in headless environments than docx2pdf's direct calls.
        # Ensure LibreOffice is running (handled by Dockerfile's CMD) and DISPLAY is set.
        
        # Build the unoconv command
        # unoconv -f pdf: converts to PDF format
        # -o <output_path>: specifies the output file path
        # <input_path>: the input file
        command = ["unoconv", "-f", "pdf", "-o", output_path, input_path]
        
        # Run the unoconv command
        # capture_output=True: captures stdout and stderr
        # text=True: deacodes stdout/stderr as text
        # check=True: raises CalledProcessError if unoconv returns a non-zero exit code
        # timeout: added to prevent hanging for very long conversions
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=300)
        
        print(f"unoconv stdout:\n{result.stdout}")
        print(f"unoconv stderr:\n{result.stderr}")
        print(f"Conversion successful: {input_path} -> {output_path}")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        # If unoconv fails, capture its error output
        print(f"Conversion failed for {input_path} via unoconv: {e}", file=sys.stderr)
        print(f"unoconv stdout (on error):\n{e.stdout}", file=sys.stderr)
        print(f"unoconv stderr (on error):\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"Conversion timed out for {input_path} via unoconv.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred in converter_worker.py: {e}", file=sys.stderr)
        sys.exit(1)
