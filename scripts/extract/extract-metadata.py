#!/usr/bin/env python3
"""
extract-metadata.py - Extract document metadata from converted markdown files

Usage: python extract-metadata.py <output_dir> <output_file>

This script analyzes converted markdown files to extract:
- Document titles and types
- Version information
- Dates (effective, revision, etc.)
- Control family coverage
- Document statistics (word count, sections, tables)
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Patterns for metadata extraction
TITLE_PATTERNS = [
    r'^#\s+(.+)$',  # Markdown H1
    r'^(.+)\n={3,}$',  # Underline style H1
]

VERSION_PATTERNS = [
    r'[Vv]ersion[:\s]+([0-9]+(?:\.[0-9]+)*)',
    r'[Vv]\.?\s*([0-9]+(?:\.[0-9]+)+)',
    r'[Rr]evision[:\s]+([0-9]+(?:\.[0-9]+)*)',
]

DATE_PATTERNS = [
    r'(?:Effective|Date|Updated|Revised)[:\s]+(\d{4}-\d{2}-\d{2})',
    r'(\d{4}-\d{2}-\d{2})',
    r'(\d{1,2}/\d{1,2}/\d{4})',
    r'([A-Z][a-z]+ \d{1,2},? \d{4})',
]

DOCUMENT_TYPE_KEYWORDS = {
    'policy': ['policy', 'policies'],
    'procedure': ['procedure', 'process', 'workflow'],
    'ssp': ['system security plan', 'ssp', 'security plan'],
    'poam': ['plan of action', 'poa&m', 'poam', 'milestones'],
    'sar': ['security assessment', 'sar', 'assessment report'],
    'plan': ['plan', 'planning'],
    'guide': ['guide', 'guidance', 'handbook'],
}

CONTROL_PATTERN = re.compile(r'\b([A-Z]{2})-\d+')


def extract_metadata_from_file(filepath: Path, tool: str) -> dict:
    """Extract metadata from a single markdown file."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {"error": str(e)}

    lines = content.split('\n')
    metadata = {
        "source_file": filepath.name,
        "source_path": str(filepath),
        "conversion_tool": tool,
        "title": None,
        "document_type": "unknown",
        "version": None,
        "dates_found": [],
        "control_families": [],
        "statistics": {
            "word_count": 0,
            "line_count": len(lines),
            "heading_count": 0,
            "table_row_count": 0,
            "list_item_count": 0
        }
    }

    # Extract title (first H1)
    for line in lines[:20]:  # Check first 20 lines
        for pattern in TITLE_PATTERNS:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                metadata["title"] = match.group(1).strip()
                break
        if metadata["title"]:
            break

    # Extract version
    for pattern in VERSION_PATTERNS:
        match = re.search(pattern, content)
        if match:
            metadata["version"] = match.group(1)
            break

    # Extract dates
    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, content):
            date_str = match.group(1)
            if date_str not in metadata["dates_found"]:
                metadata["dates_found"].append(date_str)
                if len(metadata["dates_found"]) >= 5:  # Limit to 5 dates
                    break

    # Determine document type
    content_lower = content.lower()
    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        if any(kw in content_lower for kw in keywords):
            metadata["document_type"] = doc_type
            break

    # Extract control families mentioned
    families = set()
    for match in CONTROL_PATTERN.finditer(content):
        families.add(match.group(1).upper())
    metadata["control_families"] = sorted(families)

    # Calculate statistics
    metadata["statistics"]["word_count"] = len(content.split())
    metadata["statistics"]["heading_count"] = len(re.findall(r'^#+\s', content, re.MULTILINE))
    metadata["statistics"]["table_row_count"] = len(re.findall(r'^\|', content, re.MULTILINE))
    metadata["statistics"]["list_item_count"] = len(re.findall(r'^[\-\*]\s', content, re.MULTILINE))

    return metadata


def main(output_dir: str, output_file: str) -> None:
    """Process all markdown files and output metadata.json."""
    output_path = Path(output_dir)
    all_metadata = []

    print("=== Metadata Extraction ===")
    print(f"Scanning: {output_dir}")

    # Process each tool's output
    for tool in ['pandoc', 'markitdown', 'docling']:
        md_dir = output_path / tool / 'markdown'
        if md_dir.exists():
            print(f"\nProcessing {tool} output...")
            for md_file in sorted(md_dir.glob('*.md')):
                metadata = extract_metadata_from_file(md_file, tool)
                print(f"  {md_file.name}: {metadata.get('document_type', 'unknown')}")
                all_metadata.append(metadata)

    # Generate summary
    doc_types = defaultdict(int)
    all_families = set()
    total_words = 0

    for meta in all_metadata:
        doc_types[meta.get('document_type', 'unknown')] += 1
        all_families.update(meta.get('control_families', []))
        total_words += meta.get('statistics', {}).get('word_count', 0)

    output = {
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "documents": all_metadata,
        "summary": {
            "total_documents": len(all_metadata),
            "by_type": dict(doc_types),
            "all_control_families": sorted(all_families),
            "total_word_count": total_words
        }
    }

    # Write output
    output_file_path = Path(output_file)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_text(json.dumps(output, indent=2), encoding='utf-8')

    print(f"\n=== Summary ===")
    print(f"Documents processed: {len(all_metadata)}")
    print(f"Document types: {dict(doc_types)}")
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/extracted/metadata.json"
    main(output_dir, output_file)
