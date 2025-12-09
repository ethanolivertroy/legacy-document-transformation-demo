#!/bin/bash
#
# fedramp-20x-ksi-check.sh - Check documentation against FedRAMP 20x KSIs
#
# Usage: ./fedramp-20x-ksi-check.sh [output_dir]
#
# This script demonstrates the "novel measurement" approach that
# FedRAMP 20x encourages. Instead of just checking "do we have docs?",
# it analyzes whether documentation provides evidence for Key Security
# Indicators (KSIs).
#
# PHILOSOPHY:
# Traditional: "Do I have the document?" ✓ or ✗
# FedRAMP 20x: "Can I measure the security outcome?" → Quantified evidence
#

set -e

OUTPUT_DIR="${1:-output}"
CONTROLS_JSON="$OUTPUT_DIR/extracted/controls.json"
ENTITIES_JSON="$OUTPUT_DIR/extracted/entities.json"

echo "=============================================="
echo " FedRAMP 20x KSI Evidence Check"
echo "=============================================="
echo ""
echo "This check demonstrates how machine-readable documentation"
echo "enables MEASUREMENT-based compliance verification."
echo ""

# Define KSI categories with required evidence
# Format: KSI_NAME="control_pattern:entity_types"
declare -A KSIS=(
    ["vulnerability-management"]="RA-5|SI-2:system,timeline"
    ["access-control"]="AC-2|AC-3|AC-6|IA-2:role,system"
    ["logging-monitoring"]="AU-2|AU-6|SI-4:system,timeline"
    ["encryption"]="SC-8|SC-13|SC-28:crypto_module,standard"
    ["incident-response"]="IR-4|IR-6|IR-8:role,timeline,email"
    ["configuration-management"]="CM-2|CM-6|CM-8:system,standard"
    ["boundary-protection"]="SC-7|AC-4:system"
)

echo "=== KSI Evidence Analysis ==="
echo ""

TOTAL_KSIS=${#KSIS[@]}
DOCUMENTED_KSIS=0
PARTIALLY_DOCUMENTED=0

for KSI in "${!KSIS[@]}"; do
    IFS=':' read -r CONTROL_PATTERN ENTITY_TYPES <<< "${KSIS[$KSI]}"

    echo "KSI: $KSI"
    echo "  Required controls: $CONTROL_PATTERN"
    echo "  Expected entities: $ENTITY_TYPES"

    # Check control coverage
    CONTROL_REFS=0
    if [ -f "$CONTROLS_JSON" ]; then
        CONTROL_REFS=$(jq "[.controls[] | select(.control_id | test(\"^($CONTROL_PATTERN)\"))] | length" "$CONTROLS_JSON" 2>/dev/null || echo "0")
    fi

    # Check entity coverage
    ENTITY_REFS=0
    if [ -f "$ENTITIES_JSON" ]; then
        for ETYPE in $(echo "$ENTITY_TYPES" | tr ',' '\n'); do
            COUNT=$(jq "[.entities[] | select(.entity_type == \"$ETYPE\")] | length" "$ENTITIES_JSON" 2>/dev/null || echo "0")
            ENTITY_REFS=$((ENTITY_REFS + COUNT))
        done
    fi

    # Determine status
    if [ "$CONTROL_REFS" -gt 5 ] && [ "$ENTITY_REFS" -gt 3 ]; then
        STATUS="STRONG EVIDENCE"
        DOCUMENTED_KSIS=$((DOCUMENTED_KSIS + 1))
        ICON="✅"
    elif [ "$CONTROL_REFS" -gt 0 ]; then
        STATUS="PARTIAL"
        PARTIALLY_DOCUMENTED=$((PARTIALLY_DOCUMENTED + 1))
        ICON="⚠️"
    else
        STATUS="WEAK/MISSING"
        ICON="❌"
    fi

    echo "  Control refs: $CONTROL_REFS | Entity refs: $ENTITY_REFS"
    echo "  Status: $ICON $STATUS"
    echo ""
done

echo "=============================================="
echo " Summary"
echo "=============================================="
echo ""
echo "Total KSIs checked: $TOTAL_KSIS"
echo "Strong evidence: $DOCUMENTED_KSIS"
echo "Partial evidence: $PARTIALLY_DOCUMENTED"
echo "Weak/Missing: $((TOTAL_KSIS - DOCUMENTED_KSIS - PARTIALLY_DOCUMENTED))"
echo ""

# Calculate overall readiness score
READINESS=$(echo "scale=0; ($DOCUMENTED_KSIS * 100 + $PARTIALLY_DOCUMENTED * 50) / $TOTAL_KSIS" | bc)
echo "FedRAMP 20x Readiness Score: ${READINESS}%"
echo ""

echo "=============================================="
echo " Novel Measurement Recommendations"
echo "=============================================="
echo ""
echo "FedRAMP 20x encourages moving beyond 'checkbox compliance' to"
echo "outcome-based measurement. Based on your documentation analysis:"
echo ""

if [ "$CONTROL_REFS" -lt 50 ]; then
    echo "📊 MEASUREMENT OPPORTUNITY: Control Implementation Depth"
    echo "   Track: How many controls have implementation details vs just mentions"
    echo ""
fi

if [ -f "$ENTITIES_JSON" ]; then
    TIMELINE_COUNT=$(jq '[.entities[] | select(.entity_type == "timeline")] | length' "$ENTITIES_JSON" 2>/dev/null || echo "0")
    if [ "$TIMELINE_COUNT" -lt 10 ]; then
        echo "📊 MEASUREMENT OPPORTUNITY: Procedural Timeliness"
        echo "   Track: SLA definitions, response times, review frequencies"
        echo ""
    fi

    ROLE_COUNT=$(jq '[.entities[] | select(.entity_type == "role")] | length' "$ENTITIES_JSON" 2>/dev/null || echo "0")
    if [ "$ROLE_COUNT" -lt 5 ]; then
        echo "📊 MEASUREMENT OPPORTUNITY: Responsibility Assignment"
        echo "   Track: Clear ownership for each security control"
        echo ""
    fi
fi

echo "💡 TIP: Use the extracted JSON data to build dashboards that"
echo "   continuously monitor your compliance posture, rather than"
echo "   relying on point-in-time assessments."
