from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import fitz

MAX_PDF_BYTES = 20 * 1024 * 1024
ALLOWED_CONTENT_TYPE = "application/pdf"

SECTION_ALIASES = {
    "abstract": "abstract", "introduction": "introduction", "related work": "related_work",
    "background": "related_work", "method": "methodology", "methods": "methodology",
    "methodology": "methodology", "experiments": "experiments", "experimental results": "experiments",
    "results": "results", "discussion": "results", "conclusion": "conclusion", "conclusions": "conclusion",
}

class DocumentIngestionError(Exception):
    pass

def validate_pdf(content: bytes, filename: str, content_type: str | None = None) -> None:
    if not filename.lower().endswith(".pdf") or content_type not in (None, ALLOWED_CONTENT_TYPE):
        raise DocumentIngestionError("Only PDF documents are accepted")
    if not content or len(content) > MAX_PDF_BYTES or not content.startswith(b"%PDF"):
        raise DocumentIngestionError("Invalid or oversized PDF")

def checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def safe_storage_path(root: Path, digest: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{digest}.pdf"

def store_pdf(content: bytes, root: Path, digest: str) -> Path:
    path = safe_storage_path(root, digest)
    path.write_bytes(content)
    return path

def _metadata(doc: fitz.Document) -> dict[str, Any]:
    raw = doc.metadata or {}
    return {k: v for k, v in raw.items() if v}

def parse_pdf(path: Path) -> dict[str, Any]:
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise DocumentIngestionError(f"PDF parsing failed: {exc}") from exc
    try:
        pages = []
        for number, page in enumerate(doc, start=1):
            text = page.get_text("text")
            blocks = page.get_text("blocks")
            pages.append({"page": number, "text": text, "blocks": len(blocks), "width": page.rect.width, "height": page.rect.height})
        return {"page_count": len(doc), "metadata": _metadata(doc), "pages": pages, "text": "\n\n".join(p["text"] for p in pages)}
    finally:
        doc.close()

def clean_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def detect_sections(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    hits = []
    for i, line in enumerate(lines):
        normalized = re.sub(r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)", "", line).strip().lower().rstrip(":")
        key = SECTION_ALIASES.get(normalized)
        if key and len(line.strip()) < 100:
            hits.append((i, key, line.strip()))
    sections = []
    for index, (start, key, heading) in enumerate(hits):
        end = hits[index + 1][0] if index + 1 < len(hits) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        sections.append({"type": key, "heading": heading, "text": body})
    return sections

def extract_tables_and_figures(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    try:
        tables = []
        figures = []
        for page_number, page in enumerate(doc, start=1):
            try:
                found = page.find_tables()
                for idx, table in enumerate(found.tables, start=1):
                    tables.append({"page": page_number, "index": idx, "rows": table.extract()})
            except Exception:
                pass
            for image_index, image in enumerate(page.get_images(full=True), start=1):
                figures.append({"page": page_number, "index": image_index, "xref": image[0]})
        return {"tables": tables, "figures": figures}
    finally:
        doc.close()

def extract_references(text: str) -> list[dict[str, str]]:
    match = re.search(r"(?im)^\s*(?:references|bibliography)\s*$", text)
    if not match:
        return []
    tail = text[match.end():]
    entries = [x.strip() for x in re.split(r"\n\s*(?=\[?\d{1,3}\]?\s+)", tail) if x.strip()]
    refs = []
    for idx, entry in enumerate(entries, start=1):
        doi = re.search(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", entry, re.I)
        refs.append({"index": str(idx), "text": entry, "doi": doi.group(0).rstrip(".,;") if doi else ""})
    return refs

def chunk_sections(sections: list[dict[str, str]], chunk_size: int = 1200, overlap: int = 150) -> list[dict[str, Any]]:
    chunks = []
    for section in sections:
        text = section["text"]
        start = 0
        local = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            chunks.append({"chunk_id": f"{section['type']}-{local}", "section": section["type"], "text": text[start:end]})
            local += 1
            if end == len(text): break
            start = max(0, end - overlap)
    return chunks

def process_pdf(path: Path) -> dict[str, Any]:
    parsed = parse_pdf(path)
    cleaned = clean_text(parsed["text"])
    sections = detect_sections(cleaned)
    media = extract_tables_and_figures(path)
    references = extract_references(cleaned)
    chunks = chunk_sections(sections)
    return {**parsed, "text": cleaned, "sections": sections, "references": references, "chunks": chunks, **media}
