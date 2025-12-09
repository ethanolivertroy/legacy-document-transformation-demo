#!/bin/bash
#
# find-controls.sh - Find all references to a specific control or control family
#
# Usage:
#   ./find-controls.sh AC        # Find all Access Control references
#   ./find-controls.sh AC-2      # Find specific control AC-2
#   ./find-controls.sh AC-2\(1\) # Find enhancement AC-2(1)
#
# This script demonstrates how machine-readable documents enable
# quick searches across all compliance documentation.
#

set -e

CONTROL="${1:-AC}"
OUTPUT_DIR="${2:-output}"

echo "=============================================="
echo " Control Search: $CONTROL"
echo "=============================================="
echo ""

# Search each tool's output
for TOOL in pandoc markitdown docling; do
    echo "--- $TOOL output ---"
    MD_DIR="$OUTPUT_DIR/$TOOL/markdown"

    if [ -d "$MD_DIR" ]; then
        # Use grep with line numbers and color
        RESULTS=$(grep -rn --color=always "$CONTROL" "$MD_DIR" --include="*.md" 2>/dev/null || true)
        if [ -n "$RESULTS" ]; then
            echo "$RESULTS"
        else
            echo "  (no matches found)"
        fi
    else
        echo "  (directory not found: $MD_DIR)"
    fi
    echo ""
done

# If extracted JSON exists, show structured data
CONTROLS_JSON="$OUTPUT_DIR/extracted/controls.json"
if [ -f "$CONTROLS_JSON" ]; then
    echo "--- Structured Data (controls.json) ---"
    echo ""

    # Count occurrences
    COUNT=$(jq "[.controls[] | select(.control_id | startswith(\"$CONTROL\"))] | length" "$CONTROLS_JSON" 2>/dev/null || echo "0")
    echo "Total references matching '$CONTROL': $COUNT"
    echo ""

    # Show unique controls found
    echo "Unique controls:"
    jq -r "[.controls[] | select(.control_id | startswith(\"$CONTROL\")) | .control_id] | unique | .[]" "$CONTROLS_JSON" 2>/dev/null | head -20
fi
