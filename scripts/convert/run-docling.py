#!/usr/bin/env python3
"""
run-docling.py - Convert documents to markdown using IBM Docling

Usage: python run-docling.py <input_dir> <output_dir>

Docling is IBM's document understanding library that excels at:
- Complex document layouts (multi-column, nested tables)
- Preserving document structure and hierarchy
- Extracting figures and tables with context
- Deep PDF understanding including OCR

GitHub: https://github.com/DS4SD/docling
"""

import sys
import os
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
except ImportError:
    print("Error: docling not installed")
    print("Install with: pip install docling")
    sys.exit(1)


def convert_documents(input_dir: str, output_dir: str) -> None:
    """Convert all supported documents in input_dir to markdown."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=== Docling Conversion ===")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print("")

    # Initialize Docling converter
    converter = DocumentConverter()

    # Supported extensions
    extensions = [".docx", ".pdf", ".pptx", ".html"]

    converted = 0
    for ext in extensions:
        for file in input_path.glob(f"*{ext}"):
            print(f"Converting: {file.name}")
            try:
                result = converter.convert(str(file))
                markdown_content = result.document.export_to_markdown()

                output_file = output_path / f"{file.stem}.md"
                output_file.write_text(markdown_content, encoding="utf-8")
                print(f"  -> {output_file}")
                converted += 1

                # Also export to JSON for structured data
                json_output = output_path.parent / "json"
                json_output.mkdir(parents=True, exist_ok=True)
                json_file = json_output / f"{file.stem}.json"

                # Export document structure as JSON
                import json
                doc_dict = result.document.export_to_dict()
                json_file.write_text(
                    json.dumps(doc_dict, indent=2, default=str),
                    encoding="utf-8"
                )
                print(f"  -> {json_file}")

            except Exception as e:
                print(f"  Error: {e}")

    print("")
    print(f"Docling conversion complete!")
    print(f"Files created: {converted}")


if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "docs/sample"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/docling/markdown"

    convert_documents(input_dir, output_dir)
