#!/usr/bin/env python3
"""
extract-entities.py - Extract named entities from converted markdown files

Usage: python extract-entities.py <output_dir> <output_file>

This script identifies and extracts:
- Roles (CISO, System Administrator, etc.)
- Organizations and teams
- Systems and applications
- Crypto modules (FIPS references)
- Email addresses and URLs
- Standards references (NIST, ISO, etc.)
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Entity patterns
ENTITY_PATTERNS = {
    "role": [
        r'\b(CISO|CTO|CIO|CEO|CFO)\b',
        r'\b(Chief (?:Information |Security |Technology |)Officer)\b',
        r'\b(System Administrator|SysAdmin|Admin)\b',
        r'\b(Security (?:Analyst|Engineer|Architect|Manager))\b',
        r'\b(Authorizing Official|AO)\b',
        r'\b(Information System Security (?:Officer|Manager)|ISSO|ISSM)\b',
        r'\b(SOC (?:Analyst|Manager|Team))\b',
        r'\b(Incident Response Team|IRT)\b',
    ],
    "organization": [
        r'\b(US-CERT|CISA|FedRAMP|GSA|NIST|OMB|DHS)\b',
        r'\b(Security Operations Center|SOC)\b',
        r'\b(PMO|Program Management Office)\b',
    ],
    "system": [
        r'\b(AWS|Azure|GCP|Google Cloud)\b',
        r'\b(Splunk|CloudWatch|GuardDuty)\b',
        r'\b(Okta|Active Directory|AD|LDAP)\b',
        r'\b(ServiceNow|Jira|GitHub|GitLab)\b',
        r'\b(Terraform|Ansible|Kubernetes|Docker)\b',
        r'\b(Qualys|Nessus|Tenable)\b',
    ],
    "standard": [
        r'\b(NIST (?:SP )?800-\d+[A-Z]?)\b',
        r'\b(FedRAMP (?:Moderate|High|Low))\b',
        r'\b(FIPS (?:140-[23]|199|200))\b',
        r'\b(ISO (?:27001|27002|27017|27018))\b',
        r'\b(SOC [12])\b',
        r'\b(CIS Benchmark)\b',
        r'\b(PCI[- ]DSS)\b',
        r'\b(HIPAA|GDPR|CCPA)\b',
    ],
    "crypto_module": [
        r'\b(FIPS 140-[23] (?:Level [1-4]|validated))\b',
        r'\b(OpenSSL|BoringSSL|AWS[- ]?KMS)\b',
        r'\b(TLS [0-9.]+|SSL)\b',
        r'\b(AES-(?:128|256)|RSA-(?:2048|4096))\b',
    ],
    "email": [
        r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
    ],
    "url": [
        r'\b(https?://[^\s\)]+)\b',
    ],
    "timeline": [
        r'\b(within (?:\d+|one|two|three|twenty-four) (?:hours?|days?|weeks?|months?))\b',
        r'\b((?:\d+|quarterly|annually|monthly|weekly|daily) (?:review|audit|assessment))\b',
    ],
}


def extract_entities_from_file(filepath: Path, tool: str) -> list:
    """Extract named entities from a markdown file."""
    entities = []

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return entities

    for entity_type, patterns in ENTITY_PATTERNS.items():
        found_values = defaultdict(list)

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                value = match.group(1)
                # Normalize value
                normalized = value.strip()
                if entity_type in ['role', 'organization', 'system', 'standard']:
                    normalized = normalized.upper() if len(normalized) <= 5 else normalized.title()

                # Get context
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 30)
                context = content[start:end].replace('\n', ' ').strip()

                found_values[normalized].append(context)

        # Deduplicate and create entity records
        for normalized, contexts in found_values.items():
            entities.append({
                "entity_type": entity_type,
                "value": normalized,
                "occurrences": len(contexts),
                "source_document": filepath.name,
                "conversion_tool": tool,
                "sample_contexts": contexts[:3]  # Keep up to 3 examples
            })

    return entities


def main(output_dir: str, output_file: str) -> None:
    """Process all markdown files and output entities.json."""
    output_path = Path(output_dir)
    all_entities = []

    print("=== Entity Extraction ===")
    print(f"Scanning: {output_dir}")

    # Process each tool's output
    for tool in ['pandoc', 'markitdown', 'docling']:
        md_dir = output_path / tool / 'markdown'
        if md_dir.exists():
            print(f"\nProcessing {tool} output...")
            for md_file in sorted(md_dir.glob('*.md')):
                entities = extract_entities_from_file(md_file, tool)
                print(f"  {md_file.name}: {len(entities)} entities")
                all_entities.extend(entities)

    # Generate summary
    by_type = defaultdict(int)
    unique_by_type = defaultdict(set)

    for entity in all_entities:
        by_type[entity['entity_type']] += entity['occurrences']
        unique_by_type[entity['entity_type']].add(entity['value'])

    output = {
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "entities": all_entities,
        "summary": {
            "total_entities": len(all_entities),
            "total_occurrences": sum(e['occurrences'] for e in all_entities),
            "by_type": {
                k: {
                    "total_occurrences": v,
                    "unique_values": len(unique_by_type[k])
                }
                for k, v in sorted(by_type.items())
            },
            "unique_values_by_type": {
                k: sorted(v)[:20]  # Top 20 per type
                for k, v in unique_by_type.items()
            }
        }
    }

    # Write output
    output_file_path = Path(output_file)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_text(json.dumps(output, indent=2), encoding='utf-8')

    print(f"\n=== Summary ===")
    print(f"Total entities: {len(all_entities)}")
    for entity_type, count in sorted(by_type.items()):
        print(f"  {entity_type}: {count} occurrences ({len(unique_by_type[entity_type])} unique)")
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/extracted/entities.json"
    main(output_dir, output_file)
