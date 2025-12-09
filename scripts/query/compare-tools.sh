#!/bin/bash
#
# compare-tools.sh - Compare output quality between conversion tools
#
# Usage: ./compare-tools.sh [document-name]
#
# This script helps you understand which conversion tool works best
# for your specific document types.
#

set -e

DOC="${1:-sample-access-control-policy}"
OUTPUT_DIR="${2:-output}"

echo "=============================================="
echo " Tool Comparison: $DOC"
echo "=============================================="
echo ""

# Check which tools have output for this document
TOOLS_FOUND=0
for TOOL in pandoc markitdown docling; do
    if [ -f "$OUTPUT_DIR/$TOOL/markdown/${DOC}.md" ]; then
        TOOLS_FOUND=$((TOOLS_FOUND + 1))
    fi
done

if [ $TOOLS_FOUND -eq 0 ]; then
    echo "No output found for document: $DOC"
    echo "Available documents:"
    ls -1 "$OUTPUT_DIR"/*/markdown/*.md 2>/dev/null | xargs -I {} basename {} .md | sort -u
    exit 1
fi

echo "=== File Sizes ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        SIZE=$(wc -c < "$FILE" | tr -d ' ')
        echo "$TOOL: $SIZE bytes"
    else
        echo "$TOOL: (not available)"
    fi
done
echo ""

echo "=== Word Counts ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        WC=$(wc -w < "$FILE" | tr -d ' ')
        echo "$TOOL: $WC words"
    fi
done
echo ""

echo "=== Line Counts ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        LC=$(wc -l < "$FILE" | tr -d ' ')
        echo "$TOOL: $LC lines"
    fi
done
echo ""

echo "=== Heading Detection ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        HEADINGS=$(grep -c "^#" "$FILE" 2>/dev/null || echo "0")
        echo "$TOOL: $HEADINGS headings"
    fi
done
echo ""

echo "=== Table Detection (rows with |) ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        TABLES=$(grep -c "^|" "$FILE" 2>/dev/null || echo "0")
        echo "$TOOL: $TABLES table rows"
    fi
done
echo ""

echo "=== Control References Found ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        CONTROLS=$(grep -oE '[A-Z]{2}-[0-9]+' "$FILE" 2>/dev/null | sort -u | wc -l | tr -d ' ')
        echo "$TOOL: $CONTROLS unique controls"
    fi
done
echo ""

echo "=== First 10 Lines Comparison ==="
for TOOL in pandoc markitdown docling; do
    FILE="$OUTPUT_DIR/$TOOL/markdown/${DOC}.md"
    if [ -f "$FILE" ]; then
        echo ""
        echo "--- $TOOL ---"
        head -10 "$FILE"
    fi
done
