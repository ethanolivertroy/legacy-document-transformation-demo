#!/usr/bin/env python3
"""
run-markitdown.py - Convert documents to markdown using Microsoft MarkItDown

Usage: python run-markitdown.py <input_dir> <output_dir>

MarkItDown is Microsoft's tool for converting documents to markdown,
optimized for LLM consumption. It handles Office documents, PDFs,
images, and even audio files.

GitHub: https://github.com/microsoft/markitdown
"""

import sys
import os
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    print("Error: markitdown not installed")
    print("Install with: pip install 'markitdown[all]'")
    sys.exit(1)


def convert_documents(input_dir: str, output_dir: str) -> None:
    """Convert all supported documents in input_dir to markdown."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=== MarkItDown Conversion ===")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print("")

    # Initialize MarkItDown
    md = MarkItDown()

    # Supported extensions
    extensions = [".docx", ".pdf", ".pptx", ".xlsx", ".html", ".txt"]

    converted = 0
    for ext in extensions:
        for file in input_path.glob(f"*{ext}"):
            print(f"Converting: {file.name}")
            try:
                result = md.convert(str(file))
                output_file = output_path / f"{file.stem}.md"
                output_file.write_text(result.text_content, encoding="utf-8")
                print(f"  -> {output_file}")
                converted += 1
            except Exception as e:
                print(f"  Error: {e}")

    print("")
    print(f"MarkItDown conversion complete!")
    print(f"Files created: {converted}")


if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "docs/sample"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/markitdown/markdown"

    convert_documents(input_dir, output_dir)
