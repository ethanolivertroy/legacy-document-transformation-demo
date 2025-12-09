#!/bin/bash
#
# count-by-family.sh - Count control references by NIST 800-53 family
#
# Usage: ./count-by-family.sh [output_dir]
#
# This script demonstrates how machine-readable documents enable
# quantitative compliance analysis - a key enabler for FedRAMP 20x's
# "novel measurement" approach.
#

set -e

OUTPUT_DIR="${1:-output}"
CONTROLS_JSON="$OUTPUT_DIR/extracted/controls.json"

echo "=============================================="
echo " Control Family Coverage Analysis"
echo "=============================================="
echo ""

if [ ! -f "$CONTROLS_JSON" ]; then
    echo "Error: controls.json not found at $CONTROLS_JSON"
    echo "Run extract-controls.py first."
    exit 1
fi

echo "This report shows how many times each NIST 800-53 control family"
echo "is referenced across your compliance documentation."
echo ""

echo "=== Coverage by Family ==="
echo ""
jq -r '
.summary.by_family | to_entries | sort_by(-.value) |
.[] | "\(.key)\t\(.value)\t" + ("█" * ((.value / 2) | floor))
' "$CONTROLS_JSON" | column -t -s $'\t'

echo ""
echo "=== Coverage Statistics ==="

# Calculate statistics
TOTAL_FAMILIES=20  # NIST 800-53 has 20 control families
COVERED=$(jq '.summary.by_family | keys | length' "$CONTROLS_JSON")
COVERAGE_PCT=$(echo "scale=1; $COVERED * 100 / $TOTAL_FAMILIES" | bc)

echo ""
echo "Control families in NIST 800-53: $TOTAL_FAMILIES"
echo "Families referenced in your docs: $COVERED"
echo "Family coverage: ${COVERAGE_PCT}%"

echo ""
echo "=== Missing Families ==="
echo ""

# All NIST 800-53 families
ALL_FAMILIES="AC AT AU CA CM CP IA IR MA MP PE PL PM PS PT RA SA SC SI SR"
COVERED_FAMILIES=$(jq -r '.summary.by_family | keys | .[]' "$CONTROLS_JSON" | tr '\n' ' ')

for FAMILY in $ALL_FAMILIES; do
    if ! echo "$COVERED_FAMILIES" | grep -q "$FAMILY"; then
        echo "  - $FAMILY: NOT DOCUMENTED"
    fi
done

echo ""
echo "=== Novel Measurement: Documentation Density Score ==="
echo ""

# Calculate a simple "documentation density" score
TOTAL_REFS=$(jq '.summary.total_references' "$CONTROLS_JSON")
UNIQUE_CONTROLS=$(jq '.summary.unique_controls' "$CONTROLS_JSON")
DENSITY=$(echo "scale=2; $TOTAL_REFS / $UNIQUE_CONTROLS" | bc 2>/dev/null || echo "N/A")

echo "Total control references: $TOTAL_REFS"
echo "Unique controls mentioned: $UNIQUE_CONTROLS"
echo "Average references per control: $DENSITY"
echo ""
echo "A higher density suggests controls are well-integrated across documents."
echo "A lower density might indicate controls are siloed in specific documents."
