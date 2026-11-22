#!/usr/bin/env python3
"""Generate QASPER answer/evidence predictions without loading gold references.

The default extractive mode is a deterministic, zero-cost BM25-style baseline.
The optional llm_rag mode uses the repository's configured LLM provider.
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
SYSTEM_PROMPT = """You answer questions about one scientific paper using only the supplied paragraphs.
Do not use outside knowledge. Do not invent facts or quotations. If the supplied paragraphs
do not answer the question, return the exact answer 'Unanswerable' and an empty evidence_indices
array. Otherwise return a concise answer and the indices of the paragraph(s) that directly
support it. Return one JSON object with string answer and integer-array evidence_indices.
"""


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def bm25_scores(query: str, documents: list[str], *, k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Small dependency-free BM25 implementation for a single paper's paragraphs."""
    if not documents:
        return []
    tokenized = [tokenize(document) for document in documents]
    query_terms = tokenize(query)
    if not query_terms:
        return [0.0] * len(documents)
    average_length = sum(map(len, tokenized)) / len(tokenized) or 1.0
    document_frequency: Counter[str] = Counter()
    for terms in tokenized:
        document_frequency.update(set(terms))
    scores = []
    total_docs = len(tokenized)
    for terms in tokenized:
        frequencies = Counter(terms)
        score = 0.0
        for term in query_terms:
            frequency = frequencies[term]
            if not frequency:
                continue
            df = document_frequency[term]
            inverse = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            denominator = frequency + k1 * (1 - b + b * len(terms) / average_length)
            score += inverse * frequency * (k1 + 1) / denominator
        scores.append(score)
    return scores


def retrieve_paragraphs(query: str, chunks: list[dict[str, Any]], *, top_k: int = 5,
                        context_scope: str = "full_text") -> list[dict[str, Any]]:
    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")
    if context_scope not in {"full_text", "abstract_only"}:
        raise ValueError("context_scope must be full_text or abstract_only")
    valid = [
        row for row in chunks
        if isinstance(row, dict)
        and isinstance(row.get("text"), str)
        and row["text"].strip()
        and (context_scope == "full_text" or str(row.get("section_name", "")).lower() == "abstract")
    ]
    scores = bm25_scores(query, [row["text"] for row in valid])
    ranked = sorted(
        enumerate(valid),
        key=lambda pair: (-scores[pair[0]], str(pair[1].get("chunk_id", ""))),
    )
    positive = [row for index, row in ranked if scores[index] > 0]
    if not positive:
        return []
    return positive[:top_k]


def extractive_prediction(query: dict[str, Any], chunks: list[dict[str, Any]], *, top_k: int = 5,
                          context_scope: str = "full_text") -> dict[str, Any]:
    ranked = retrieve_paragraphs(
        str(query.get("question") or query.get("query_text") or ""),
        chunks, top_k=top_k, context_scope=context_scope,
    )
    if not ranked:
        answer = "Unanswerable"
    else:
        # A transparent extractive baseline: the highest-ranked paragraph is the answer.
        answer = ranked[0]["text"]
    return {
        "question_id": str(query["query_id"]),
        "predicted_answer": answer,
        "predicted_evidence": [row["text"] for row in ranked],
    }


async def llm_prediction(query: dict[str, Any], chunks: list[dict[str, Any]], *, top_k: int = 5,
                         context_scope: str = "full_text") -> dict[str, Any]:
    from app.services.llm.factory import get_llm_provider

    question = str(query.get("question") or query.get("query_text") or "").strip()
    ranked = retrieve_paragraphs(question, chunks, top_k=top_k, context_scope=context_scope)
    if not ranked:
        return {
            "question_id": str(query["query_id"]),
            "predicted_answer": "Unanswerable",
            "predicted_evidence": [],
        }
    passages = [{"index": index, "text": row["text"]} for index, row in enumerate(ranked)]
    prompt = (
        f"Paper title: {query.get('paper_title', '')}\n"
        f"Paper abstract: {query.get('paper_abstract', '')}\n"
        f"Question: {question}\n\n"
        f"Retrieved paragraphs (the only evidence you may use):\n"
        f"{json.dumps(passages, ensure_ascii=False)}\n\n"
        "Return JSON: {\"answer\": \"concise answer or Unanswerable\", "
        "\"evidence_indices\": [0]}. Indices must refer to the supplied paragraph list. "
        "Return an empty evidence_indices list for Unanswerable."
    )
    result = await get_llm_provider().structured(prompt, system=SYSTEM_PROMPT, temperature=0.0)
    answer = result.get("answer")
    indices = result.get("evidence_indices")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError(f"{query['query_id']}: model returned an empty answer")
    if not isinstance(indices, list):
        raise ValueError(f"{query['query_id']}: evidence_indices must be a list")
    clean_indices: list[int] = []
    for index in indices:
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(ranked):
            raise ValueError(f"{query['query_id']}: model cited an invalid evidence index")
        if index not in clean_indices:
            clean_indices.append(index)
    if answer.strip().lower() == "unanswerable" and clean_indices:
        raise ValueError(f"{query['query_id']}: Unanswerable response cannot cite evidence")
    if answer.strip().lower() != "unanswerable" and not clean_indices:
        raise ValueError(f"{query['query_id']}: answer has no traceable evidence")
    return {
        "question_id": str(query["query_id"]),
        "predicted_answer": answer.strip(),
        "predicted_evidence": [ranked[index]["text"] for index in clean_indices],
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: each JSONL row must be an object")
            rows.append(row)
    return rows


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


async def generate(data_dir: Path, output: Path, *, split: str, mode: str, top_k: int,
                   max_questions: int | None, code_revision: str,
                   context_scope: str = "full_text") -> dict[str, Any]:
    if split == "test":
        raise ValueError("Test split is locked. Generate validation predictions first; no test generation is enabled.")
    normalized = data_dir / "normalized"
    query_path = normalized / "queries" / f"{split}.jsonl"
    chunk_path = normalized / "chunks" / f"{split}.jsonl"
    manifest_path = normalized / "manifest.json"
    for path in (query_path, chunk_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing QASPER prepared file: {path}; run prepare_qasper.py first")

    queries = read_jsonl(query_path)
    chunks = read_jsonl(chunk_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if max_questions is not None:
        if max_questions < 1:
            raise ValueError("max_questions must be positive")
        queries = queries[:max_questions]
    if not queries:
        raise ValueError(f"No {split} questions found")

    by_paper: dict[str, list[dict[str, Any]]] = {}
    for chunk in chunks:
        by_paper.setdefault(str(chunk.get("paper_id") or ""), []).append(chunk)

    # Record what context is actually present; a shared source-file hash alone
    # cannot prove that abstract-only and full-text modes saw different content.
    abstract_chunks = [row for row in chunks if str(row.get("section_name", "")).strip().lower() == "abstract"
                       and isinstance(row.get("text"), str) and row["text"].strip()]
    body_chunks = [row for row in chunks if str(row.get("section_name", "")).strip().lower() != "abstract"
                   and isinstance(row.get("text"), str) and row["text"].strip()]
    papers_with_abstract = {str(row.get("paper_id") or "") for row in abstract_chunks}
    papers_with_body = {str(row.get("paper_id") or "") for row in body_chunks}

    predictions = []
    for query in queries:
        paper_id = str(query.get("paper_id") or "")
        paper_chunks = by_paper.get(paper_id, [])
        if mode == "extractive":
            prediction = extractive_prediction(
                query, paper_chunks, top_k=top_k, context_scope=context_scope
            )
        else:
            prediction = await llm_prediction(
                query, paper_chunks, top_k=top_k, context_scope=context_scope
            )
        predictions.append(prediction)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    metadata = {
        "dataset": manifest.get("dataset"),
        "dataset_version": manifest.get("dataset_version"),
        "split": split,
        "mode": mode,
        "context_scope": context_scope,
        "top_k": top_k,
        "questions_generated": len(predictions),
        "context_inventory": {
            "total_nonempty_chunks": len(abstract_chunks) + len(body_chunks),
            "abstract_chunks": len(abstract_chunks),
            "non_abstract_chunks": len(body_chunks),
            "papers_with_abstract": len(papers_with_abstract),
            "papers_with_non_abstract_text": len(papers_with_body),
            "selected_scope_chunk_count": len(abstract_chunks) if context_scope == "abstract_only" else len(abstract_chunks) + len(body_chunks),
        },
        "query_file_sha256": file_sha256(query_path),
        "chunk_file_sha256": file_sha256(chunk_path),
        "manifest_sha256": file_sha256(manifest_path),
        "code_revision": code_revision,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gold_references_loaded": False,
        "test_split_used": False,
    }
    metadata_path = output.with_suffix(output.suffix + ".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"prediction_file": str(output), "metadata_file": str(metadata_path), **metadata}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/benchmarks/qasper"))
    parser.add_argument("--split", choices=("train", "validation"), default="validation")
    parser.add_argument("--mode", choices=("extractive", "llm_rag"), default="extractive")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--context-scope", choices=("full_text", "abstract_only"), default="full_text")
    parser.add_argument("--max-questions", type=int, default=None, help="Optional smoke-test cap")
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    output = args.output or (args.data_dir / "predictions" / f"{args.split}.{args.mode}.jsonl")
    try:
        report = asyncio.run(generate(
            args.data_dir, output, split=args.split, mode=args.mode, top_k=args.top_k,
            max_questions=args.max_questions, code_revision=args.code_revision,
            context_scope=args.context_scope,
        ))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, **report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
