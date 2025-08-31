#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. Install with: pip install PyMuPDF")
    sys.exit(1)


def pdf_to_png(pdf_path, output_dir=None, dpi=150):
    """
    Convert PDF to PNG images

    Args:
        pdf_path: Path to input PDF file
        output_dir: Output directory (default: same as PDF)
        dpi: Resolution in DPI (default: 150)
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"Error: PDF file '{pdf_path}' not found")
        return False

    if output_dir is None:
        output_dir = pdf_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        base_name = pdf_path.stem

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Calculate zoom factor for desired DPI
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            # Generate output filename
            if len(doc) == 1:
                output_file = output_dir / f"{base_name}.png"
            else:
                output_file = output_dir / f"{base_name}_page_{page_num + 1:03d}.png"

            pix.save(output_file)
            print(f"Saved: {output_file}")

        doc.close()
        print(f"Conversion completed: {len(doc)} pages converted")
        return True

    except Exception as e:
        print(f"Error converting PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to PNG images")
    parser.add_argument("pdf_file", help="Input PDF file")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument(
        "-d", "--dpi", type=int, default=150, help="Resolution in DPI (default: 150)"
    )

    args = parser.parse_args()

    success = pdf_to_png(args.pdf_file, args.output, args.dpi)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
