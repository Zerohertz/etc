#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import List, Union

try:
    from PIL import Image
except ImportError:
    print("Pillow not found. Install with: pip install Pillow")
    sys.exit(1)


def png_to_pdf(
    png_files: Union[str, List[str]], output_file: str = None, fit_page: bool = True
) -> bool:
    """
    Convert PNG images to PDF

    Args:
        png_files: Path to PNG file or list of PNG files
        output_file: Output PDF file path
        fit_page: Whether to fit images to page size

    Returns:
        bool: True if successful, False otherwise
    """
    if isinstance(png_files, str):
        png_files = [png_files]

    # Validate input files
    valid_files = []
    for png_file in png_files:
        png_path = Path(png_file)
        if not png_path.exists():
            print(f"Warning: PNG file '{png_path}' not found")
            continue
        if png_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
            print(f"Warning: '{png_path}' is not a PNG/JPG file")
            continue
        valid_files.append(png_path)

    if not valid_files:
        print("Error: No valid image files found")
        return False

    # Generate output filename if not provided
    if output_file is None:
        if len(valid_files) == 1:
            output_file = valid_files[0].with_suffix(".pdf")
        else:
            output_file = Path(valid_files[0].parent) / "combined.pdf"
    else:
        output_file = Path(output_file)

    try:
        images = []

        for png_file in valid_files:
            with Image.open(png_file) as img:
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img.copy())

        if not images:
            print("Error: No images loaded")
            return False

        # Save as PDF
        if len(images) == 1:
            images[0].save(output_file, "PDF")
        else:
            images[0].save(output_file, "PDF", save_all=True, append_images=images[1:])

        print(f"PDF created: {output_file}")
        print(f"Images converted: {len(images)}")
        return True

    except Exception as e:
        print(f"Error converting to PDF: {e}")
        return False


def collect_png_files(directory: Union[str, Path]) -> List[Path]:
    """
    Collect all PNG files from a directory

    Args:
        directory: Directory path

    Returns:
        List of PNG file paths
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []

    png_files = []
    for ext in ["*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]:
        png_files.extend(directory.glob(ext))

    return sorted(png_files)


def main():
    parser = argparse.ArgumentParser(description="Convert PNG images to PDF")
    parser.add_argument("input", nargs="+", help="Input PNG files or directory")
    parser.add_argument("-o", "--output", help="Output PDF file")
    parser.add_argument(
        "--fit-page",
        action="store_true",
        default=True,
        help="Fit images to page size (default: True)",
    )
    parser.add_argument(
        "--no-fit",
        dest="fit_page",
        action="store_false",
        help="Don't fit images to page size",
    )

    args = parser.parse_args()

    # Collect input files
    input_files = []
    for input_path in args.input:
        path = Path(input_path)
        if path.is_file():
            input_files.append(str(path))
        elif path.is_dir():
            dir_files = collect_png_files(path)
            input_files.extend(str(f) for f in dir_files)
            print(f"Found {len(dir_files)} image files in {path}")
        else:
            print(f"Warning: '{path}' is not a file or directory")

    if not input_files:
        print("Error: No input files specified")
        sys.exit(1)

    success = png_to_pdf(input_files, args.output, args.fit_page)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
