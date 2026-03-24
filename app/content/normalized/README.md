# Normalized curriculum content

This directory contains a generated, versioned normalization of curriculum source markdown files from `context_docs_md/`.

## Pipeline

Run:

```bash
python3 scripts/normalize_curriculum.py
```

Outputs:

- `manifest.json` describing the current data version and datasets.
- `v1/*.json` data files for:
  - `year_group`
  - `term`
  - `block`
  - `strand`
  - `small_step`
  - `method_stage` (CPA)
  - `vocabulary_entries`
  - `times_table_expectations`

## Source quality metadata

Every record includes:

- `metadata.source_file`
- `metadata.source_quality` (`full_text`, `summary_from_visual`, `partial_extract`)

Use this flag to prevent over-trusting records from summarized or partial sources.

## Schemas

`schemas/*.schema.json` define record-level JSON Schemas for each normalized dataset.
