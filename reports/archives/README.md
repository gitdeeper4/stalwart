# 📦 Reports Archive

This directory contains archived reports organized by year.

## Structure
- `YYYY/` - All reports from a specific year
- `templates/` - Archived templates

## Archiving Policy
- Daily reports: Archived after 90 days
- Weekly reports: Archived after 1 year
- Monthly reports: Archived after 5 years
- Alert reports: Archived based on severity

## Retrieval
To retrieve an archived report:
```bash
find reports/archives/YYYY -name "*BRIDGEID*"
```

