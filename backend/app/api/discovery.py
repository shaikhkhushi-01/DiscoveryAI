from __future__ import annotations

import json
from collections import Counter
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.paper import Paper

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


def _payload(document: Document) -> dict[str, Any]:
    try:
        return json.loads(document.metadata_json or "{}")
    except json.JSONDecodeError:
        return {}


def _extraction(payload: dict[str, Any]) -> dict[str, Any]:
    extracted = payload.get("extraction")
    return extracted if isinstance(extracted, dict) else {}


def _candidate_gaps(db: Session, limit: int = 10) -> list[dict[str, Any]]:
    documents = db.query(Document).order_by(Document.id.desc()).all()
    candidates: Counter[str] = Counter()
    evidence: dict[str, list[int]] = {}
    kinds: dict[str, str] = {}

    for document in documents:
        extraction = _extraction(_payload(document))
        for item in extraction.get("limitations", []) or []:
            text = item.get("text") if isinstance(item, dict) else str(item)
            if not text:
                continue
            key = text.strip()
            candidates[key] += 1
            evidence.setdefault(key, []).append(document.id)
            kinds[key] = "limitation signal"
        for item in extraction.get("future_work", []) or []:
            text = item.get("text") if isinstance(item, dict) else str(item)
            if not text:
                continue
            key = text.strip()
            candidates[key] += 1
            evidence.setdefault(key, []).append(document.id)
            kinds[key] = "future-work signal"

    rows = []
    for text, count in candidates.most_common(limit):
        rows.append(
            {
                "title": text,
                "type": kinds[text],
                "evidence_count": count,
                "source_document_ids": sorted(set(evidence[text])),
                "status": "candidate",
                "score": min(100, 50 + count * 10),
                "score_type": "heuristic_candidate_signal",
            }
        )
    return rows


@router.get("/summary")
def discovery_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    paper_count = db.query(func.count(Paper.id)).scalar() or 0
    document_count = db.query(func.count(Document.id)).scalar() or 0
    extracted_count = 0

    for document in db.query(Document).all():
        if _extraction(_payload(document)):
            extracted_count += 1

    gaps = _candidate_gaps(db, limit=5)
    return {
        "source": "live_database",
        "demo_data": False,
        "papers_indexed": paper_count,
        "documents_ingested": document_count,
        "documents_extracted": extracted_count,
        "candidate_gaps": len(_candidate_gaps(db, limit=1000)),
        "evidence_links": sum(item["evidence_count"] for item in gaps),
        "candidate_gap_preview": gaps,
    }


@router.get("/papers")
def discovery_papers(limit: int = 20, db: Session = Depends(get_db)) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    papers = (
        db.query(Paper)
        .order_by(Paper.id.desc())
        .limit(limit)
        .all()
    )
    items = []
    for paper in papers:
        document = paper.document
        extraction_ready = bool(
            document and _extraction(_payload(document))
        )
        items.append(
            {
                "id": paper.id,
                "title": paper.title,
                "year": paper.publication_date.year if paper.publication_date else None,
                "venue": paper.venue,
                "document_id": document.id if document else None,
                "status": document.status if document else "paper_only",
                "page_count": document.page_count if document else None,
                "extraction_ready": extraction_ready,
            }
        )
    return {"source": "live_database", "demo_data": False, "items": items}


@router.get("/gaps")
def discovery_gaps(limit: int = 20, db: Session = Depends(get_db)) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    return {
        "source": "live_database",
        "demo_data": False,
        "method": "candidate signals from persisted limitations and future-work extraction",
        "items": _candidate_gaps(db, limit=limit),
    }


@router.get("/search")
def discovery_search(q: str, limit: int = 20, db: Session = Depends(get_db)) -> dict[str, Any]:
    query = q.strip()
    limit = max(1, min(limit, 50))
    if not query:
        return {"source": "live_database", "demo_data": False, "items": []}

    pattern = f"%{query}%"
    papers = (
        db.query(Paper)
        .outerjoin(Document)
        .filter(
            or_(
                Paper.title.ilike(pattern),
                Paper.abstract.ilike(pattern),
                Document.extracted_text.ilike(pattern),
            )
        )
        .order_by(Paper.id.desc())
        .limit(limit)
        .all()
    )
    return {
        "source": "live_database",
        "demo_data": False,
        "query": query,
        "items": [
            {"id": paper.id, "title": paper.title, "year": paper.publication_date.year if paper.publication_date else None}
            for paper in papers
        ],
    }
