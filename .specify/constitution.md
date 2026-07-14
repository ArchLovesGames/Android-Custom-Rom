# Project Constitution

## Principles

1. Dataset accuracy comes first. User-facing compatibility results must be traceable to structured CSV data.
2. Changes must preserve startup validation for schemas and compatibility references.
3. User workflows should remain searchable, bounded, and understandable on large datasets.
4. Security-sensitive information must never be committed to the repository.
5. New behavior should include focused tests or a documented reason tests were not added.

## Quality Gates

Before merge, contributors should run the configured tests and quality checks:

```bash
pre-commit run --all-files
```
