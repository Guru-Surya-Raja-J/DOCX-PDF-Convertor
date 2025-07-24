# converter_worker.py
import sys
import os
from docx2pdf import convert

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python converter_worker.py <input_docx_path> <output_pdf_path>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        convert(input_path, output_path)
        print(f"Conversion successful: {input_path} -> {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Conversion failed for {input_path}: {e}", file=sys.stderr)
        sys.exit(1)