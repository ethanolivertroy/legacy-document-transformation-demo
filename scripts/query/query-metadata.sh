#!/bin/bash
#
# query-metadata.sh - Query extracted document metadata using jq
#
# Usage: ./query-metadata.sh [output_dir]
#
# Demonstrates how structured metadata enables powerful queries
# that would be impossible with traditional document management.
#

set -e

OUTPUT_DIR="${1:-output}"
EXTRACTED_DIR="$OUTPUT_DIR/extracted"

echo "=============================================="
echo " Document Metadata Analysis"
echo "=============================================="
echo ""

# Check if metadata exists
if [ ! -f "$EXTRACTED_DIR/metadata.json" ]; then
    echo "Error: metadata.json not found"
    echo "Run the extraction scripts first."
    exit 1
fi

echo "=== Document Summary ==="
jq '.summary' "$EXTRACTED_DIR/metadata.json"
echo ""

echo "=== Documents by Type ==="
jq '.documents[] | {file: .source_file, type: .document_type, version: .version}' "$EXTRACTED_DIR/metadata.json"
echo ""

echo "=== Control Family Coverage by Document ==="
jq '.documents[] | {file: .source_file, families: .control_families}' "$EXTRACTED_DIR/metadata.json"
echo ""

echo "=== Document Statistics ==="
jq '.documents[] | {file: .source_file, words: .statistics.word_count, tables: .statistics.table_row_count}' "$EXTRACTED_DIR/metadata.json"
echo ""

# If controls.json exists, show control summary
if [ -f "$EXTRACTED_DIR/controls.json" ]; then
    echo "=== Control Distribution ==="
    jq '.summary.by_family' "$EXTRACTED_DIR/controls.json"
    echo ""

    echo "=== Top 10 Most Referenced Controls ==="
    jq '[.controls | group_by(.control_id) | .[] | {control: .[0].control_id, count: length}] | sort_by(-.count) | .[0:10]' "$EXTRACTED_DIR/controls.json"
fi
