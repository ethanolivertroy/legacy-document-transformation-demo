# Sample Compliance Documents

This directory contains synthetic compliance documents for testing the transformation pipeline. These documents are designed to mimic real FedRAMP compliance documentation while containing no sensitive information.

## Included Documents

| File | Type | Description | Control Families |
|------|------|-------------|------------------|
| `sample-access-control-policy.docx` | Policy | Access Control Policy per NIST 800-53 | AC |
| `sample-ssp-excerpt.docx` | SSP | System Security Plan control implementations | AC, AU, CM, IA, SC, SI |
| `sample-poam.docx` | POA&M | Plan of Action & Milestones with findings | AC, CM, RA, AU, IR |
| `sample-ir-procedure.docx` | Procedure | Incident Response procedure document | IR |

## Purpose

These documents demonstrate:

1. **Realistic structure** - Proper headings, sections, tables
2. **Control references** - NIST 800-53 control IDs in standard format
3. **Named entities** - Roles (CISO, Admin), systems (AWS, Splunk), standards (FIPS, FedRAMP)
4. **Metadata patterns** - Version numbers, dates, document types

## Regenerating Samples

To regenerate or modify these samples:

```bash
pip install python-docx
python scripts/create-samples.py
```

The script is in `scripts/create-samples.py` and can be modified to create different document types or content.

## Adding Your Own Documents

See the [BYOD Guide](../../BYOD.md) for instructions on adding your own compliance documents.
