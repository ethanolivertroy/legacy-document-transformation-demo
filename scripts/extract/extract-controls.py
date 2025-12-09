#!/usr/bin/env python3
"""
extract-controls.py - Extract NIST 800-53 security control references from markdown

Usage: python extract-controls.py <output_dir> <output_file>

This script scans converted markdown files and extracts all references to
NIST 800-53 security controls (e.g., AC-1, AC-2(1), SC-7.a).

The output is a structured JSON file that enables:
- Control coverage analysis
- Cross-document consistency checks
- Gap identification
- FedRAMP 20x KSI mapping
"""

import re
import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

# NIST 800-53 control pattern
# Matches: AC-1, AC-2(1), AC-2.a, SC-7(3).a, etc.
CONTROL_PATTERN = re.compile(
    r'\b([A-Z]{2})-(\d{1,2})(?:\((\d+)\))?(?:\.([a-z]))?',
    re.IGNORECASE
)

# Control family names
CONTROL_FAMILIES = {
    'AC': 'Access Control',
    'AT': 'Awareness and Training',
    'AU': 'Audit and Accountability',
    'CA': 'Assessment, Authorization, and Monitoring',
    'CM': 'Configuration Management',
    'CP': 'Contingency Planning',
    'IA': 'Identification and Authentication',
    'IR': 'Incident Response',
    'MA': 'Maintenance',
    'MP': 'Media Protection',
    'PE': 'Physical and Environmental Protection',
    'PL': 'Planning',
    'PM': 'Program Management',
    'PS': 'Personnel Security',
    'PT': 'PII Processing and Transparency',
    'RA': 'Risk Assessment',
    'SA': 'System and Services Acquisition',
    'SC': 'System and Communications Protection',
    'SI': 'System and Information Integrity',
    'SR': 'Supply Chain Risk Management'
}


def extract_controls_from_file(filepath: Path, tool: str) -> list:
    """Extract all control references from a markdown file."""
    controls = []

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return controls

    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        for match in CONTROL_PATTERN.finditer(line):
            family = match.group(1).upper()
            number = match.group(2)
            enhancement = match.group(3)
            part = match.group(4)

            # Build control ID
            control_id = f"{family}-{number}"
            if enhancement:
                control_id += f"({enhancement})"
            if part:
                control_id += f".{part.lower()}"

            # Get context (surrounding text)
            start = max(0, match.start() - 50)
            end = min(len(line), match.end() + 100)
            context = line[start:end].strip()

            controls.append({
                "control_id": control_id,
                "control_family": family,
                "control_family_name": CONTROL_FAMILIES.get(family, "Unknown"),
                "base_control": f"{family}-{number}",
                "has_enhancement": enhancement is not None,
                "enhancement_number": enhancement,
                "source_document": filepath.name,
                "source_path": str(filepath),
                "conversion_tool": tool,
                "source_location": {
                    "line": line_num,
                    "column": match.start()
                },
                "context_snippet": context
            })

    return controls


def main(output_dir: str, output_file: str) -> None:
    """Process all markdown files and output controls.json."""
    output_path = Path(output_dir)
    all_controls = []

    print("=== Control Extraction ===")
    print(f"Scanning: {output_dir}")

    # Process each tool's output
    for tool in ['pandoc', 'markitdown', 'docling']:
        md_dir = output_path / tool / 'markdown'
        if md_dir.exists():
            print(f"\nProcessing {tool} output...")
            for md_file in sorted(md_dir.glob('*.md')):
                controls = extract_controls_from_file(md_file, tool)
                print(f"  {md_file.name}: {len(controls)} control references")
                all_controls.extend(controls)

    # Generate summary statistics
    by_family = defaultdict(int)
    by_control = defaultdict(list)
    by_tool = defaultdict(int)
    by_document = defaultdict(int)

    for ctrl in all_controls:
        by_family[ctrl['control_family']] += 1
        by_control[ctrl['control_id']].append(ctrl['conversion_tool'])
        by_tool[ctrl['conversion_tool']] += 1
        by_document[ctrl['source_document']] += 1

    # Find controls detected by all tools (consensus)
    unique_controls = set(by_control.keys())
    controls_all_tools = [
        cid for cid, tools in by_control.items()
        if len(set(tools)) == 3
    ]

    output = {
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "controls": all_controls,
        "summary": {
            "total_references": len(all_controls),
            "unique_controls": len(unique_controls),
            "by_family": dict(sorted(by_family.items())),
            "by_tool": dict(by_tool),
            "by_document": dict(by_document),
            "controls_found_by_all_tools": sorted(controls_all_tools),
            "control_families_covered": sorted(by_family.keys())
        }
    }

    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding='utf-8')

    print(f"\n=== Summary ===")
    print(f"Total control references: {len(all_controls)}")
    print(f"Unique controls: {len(unique_controls)}")
    print(f"Control families covered: {len(by_family)}")
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/extracted/controls.json"
    main(output_dir, output_file)
