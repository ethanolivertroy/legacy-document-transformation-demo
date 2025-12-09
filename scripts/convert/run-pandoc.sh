#!/bin/bash
#
# run-pandoc.sh - Convert documents to markdown using Pandoc
#
# Usage: ./run-pandoc.sh <input_dir> <output_dir>
#
# Pandoc is a universal document converter that handles DOCX reliably.
# It preserves document structure, tables, and formatting well.
#

set -e

INPUT_DIR="${1:-docs/sample}"
OUTPUT_DIR="${2:-output/pandoc/markdown}"

mkdir -p "$OUTPUT_DIR"

echo "=== Pandoc Conversion ==="
echo "Input: $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Process DOCX files
for file in "$INPUT_DIR"/*.docx; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .docx)
        echo "Converting: $filename.docx"
        pandoc "$file" \
            --from=docx \
            --to=gfm \
            --wrap=none \
            --extract-media="$OUTPUT_DIR/media" \
            -o "$OUTPUT_DIR/${filename}.md"
        echo "  -> $OUTPUT_DIR/${filename}.md"
    fi
done

# Process PDF files (if available - requires pdftotext)
for file in "$INPUT_DIR"/*.pdf; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .pdf)
        echo "Converting: $filename.pdf"
        # Pandoc can handle PDFs if poppler-utils is installed
        pandoc "$file" \
            --from=pdf \
            --to=gfm \
            --wrap=none \
            -o "$OUTPUT_DIR/${filename}.md" 2>/dev/null || \
        echo "  Warning: PDF conversion may require additional tools"
    fi
done

echo ""
echo "Pandoc conversion complete!"
echo "Files created: $(ls -1 "$OUTPUT_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
