# Days 21–30 — Scientific Document Intelligence

- Day 21: authenticated PDF upload, validation, SHA-256 storage identity, duplicate detection, status.
- Day 22: PyMuPDF text, metadata, page extraction and parsing errors.
- Day 23: scientific section detection.
- Day 24: table extraction attempt and figure/image metadata.
- Day 25: reference-section and DOI extraction.
- Day 26: scientific text cleaning.
- Day 27: section-aware overlapping chunks with IDs.
- Day 28: PDF metadata mapped into Paper with filename fallback.
- Day 29: provider-neutral LLM interface, JSON structured-output helper and extraction prompt.
- Day 30: async Ollama `/api/generate` provider with configurable model/base URL.

Validation: `cd backend && pytest app/tests`.
Runtime PostgreSQL/PDF/Ollama integration is not claimed as executed through GitHub repository operations.
