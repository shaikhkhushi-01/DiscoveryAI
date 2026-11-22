#!/usr/bin/env python3
"""Download and normalize the pinned QASPER v0.3.0 release.

Raw archives and generated benchmark data stay local under data/benchmarks/qasper
(which is gitignored). Gold references are written separately from model inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATASET_VERSION = "0.3.0"
DATASET_REPO = "allenai/qasper"
DATASET_REVISION = "fdc9d8214fbab5dd782958601db4d678e6934a54"
LICENSE = "CC BY 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
PAPER_URL = "https://aclanthology.org/2021.naacl-main.365/"
DATASET_CARD_URL = f"https://huggingface.co/datasets/{DATASET_REPO}"
ARCHIVES = {
    "train_dev": {
        "url": "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz",
        "sha256": "a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a",
        "max_bytes": 20 * 1024 * 1024,
        "files": {
            "qasper-train-v0.3.json": "train",
            "qasper-dev-v0.3.json": "validation",
        },
    },
    "test": {
        "url": "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz",
        "sha256": "72a52a41193e2838b8074f80ac074b94f956b84886c36a61c58a7df4171bdd72",
        "max_bytes": 10 * 1024 * 1024,
        "files": {"qasper-test-v0.3.json": "test"},
    },
}
EXPECTED_PAPERS = {"train": 888, "validation": 281, "test": 416}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_verified(url: str, expected_sha256: str, destination: Path, max_bytes: int) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        existing = destination.read_bytes()
        if sha256_bytes(existing) == expected_sha256:
            return {"path": str(destination), "sha256": expected_sha256, "bytes": len(existing), "reused": True}
        raise ValueError(f"Existing archive checksum mismatch; remove it manually before retry: {destination}")

    request = urllib.request.Request(url, headers={"User-Agent": "DiscoveryAI-QASPER/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        final_url = response.geturl()
        if not final_url.startswith("https://"):
            raise ValueError(f"Refusing non-HTTPS archive redirect: {final_url}")
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > max_bytes:
            raise ValueError(f"Archive exceeds size limit: {declared} bytes")
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"Archive exceeds size limit ({max_bytes} bytes)")
    actual = sha256_bytes(data)
    if actual != expected_sha256:
        raise ValueError(f"Archive SHA-256 mismatch for {url}: expected {expected_sha256}, got {actual}")
    fd, temp_name = tempfile.mkstemp(prefix=destination.name + ".", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        Path(temp_name).replace(destination)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return {"path": str(destination), "sha256": actual, "bytes": len(data), "reused": False}


def read_json_from_tar(archive_path: Path, expected_name: str, max_member_bytes: int = 100 * 1024 * 1024) -> dict[str, Any]:
    with tarfile.open(archive_path, mode="r:gz") as archive:
        matches = [m for m in archive.getmembers() if Path(m.name).name == expected_name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one {expected_name} in {archive_path.name}; found {len(matches)}")
        member = matches[0]
        if not member.isfile() or member.size > max_member_bytes:
            raise ValueError(f"Unsafe or oversized archive member: {member.name}")
        stream = archive.extractfile(member)
        if stream is None:
            raise ValueError(f"Could not read archive member: {member.name}")
        payload = stream.read(max_member_bytes + 1)
    if len(payload) > max_member_bytes:
        raise ValueError(f"Archive member too large: {expected_name}")
    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{expected_name} must contain a JSON object keyed by paper ID")
    return parsed


def _list_at(value: Any, index: int) -> Any:
    if not isinstance(value, list) or index >= len(value):
        return None
    return value[index]


def normalize_paper(split: str, source_key: str, paper: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    paper_id = str(paper.get("id") or source_key).strip()
    if not paper_id:
        raise ValueError("Paper record has no stable ID")
    title = str(paper.get("title") or "").strip()
    abstract = str(paper.get("abstract") or "").strip()
    full_text = paper.get("full_text") or {}
    # QASPER releases have appeared in two equivalent representations:
    # (1) the original list of {section_name, paragraphs} objects and
    # (2) the Hugging Face columnar object with parallel section_name /
    # paragraphs arrays. Accept both; silently treating a list as {} drops
    # every body paragraph and makes "full_text" evaluation abstract-only.
    if isinstance(full_text, list):
        section_names = []
        paragraphs_by_section = []
        for section_index, section in enumerate(full_text):
            if not isinstance(section, dict):
                raise ValueError(f"{paper_id}: full_text[{section_index}] must be an object")
            section_names.append(section.get("section_name"))
            paragraphs_by_section.append(section.get("paragraphs") or [])
    elif isinstance(full_text, dict):
        section_names = full_text.get("section_name") or []
        paragraphs_by_section = full_text.get("paragraphs") or []
    else:
        raise ValueError(f"{paper_id}: full_text must be a list or object")
    if not isinstance(section_names, list) or not isinstance(paragraphs_by_section, list):
        raise ValueError(f"{paper_id}: malformed full_text sections")
    if len(section_names) != len(paragraphs_by_section):
        raise ValueError(f"{paper_id}: section_name and paragraphs lengths differ")

    chunks: list[dict[str, Any]] = []
    if abstract:
        chunks.append({
            "chunk_id": f"{paper_id}::abstract::0",
            "paper_id": paper_id,
            "section_name": "Abstract",
            "paragraph_index": 0,
            "text": abstract,
            "text_origin": "QASPER v0.3.0 dataset release",
        })
    for section_index, section_paragraphs in enumerate(paragraphs_by_section):
        if not isinstance(section_paragraphs, list):
            continue
        section_name = str(section_names[section_index] or f"section_{section_index + 1}")
        for paragraph_index, paragraph in enumerate(section_paragraphs):
            text_value = str(paragraph or "").strip()
            if not text_value:
                continue
            chunks.append({
                "chunk_id": f"{paper_id}::section::{section_index}::paragraph::{paragraph_index}",
                "paper_id": paper_id,
                "section_name": section_name,
                "paragraph_index": paragraph_index,
                "text": text_value,
                "text_origin": "QASPER v0.3.0 dataset release",
            })

    qas_records = paper.get("qas") or []
    # Canonical QASPER v0.3 stores one QA object per list item.
    if not isinstance(qas_records, list):
        raise ValueError(f"{paper_id}: qas must be a list of QA objects")

    queries: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    seen_question_ids: set[str] = set()
    for index, qa in enumerate(qas_records):
        if not isinstance(qa, dict):
            raise ValueError(f"{paper_id}: qas[{index}] must be an object")
        qid = str(qa.get("question_id") or f"{paper_id}::q::{index}").strip()
        question_text = str(qa.get("question") or "").strip()
        if not qid or not question_text:
            raise ValueError(f"{paper_id}: qas[{index}] has missing question_id or question")
        if qid in seen_question_ids:
            raise ValueError(f"{paper_id}: duplicate question_id {qid}")
        seen_question_ids.add(qid)
        queries.append({
            "query_id": qid,
            "split": split,
            "paper_id": paper_id,
            "paper_title": title,
            "paper_abstract": abstract,
            "question": question_text,
            "query_text": question_text,
        })

        raw_annotations = qa.get("answers") or []
        if not isinstance(raw_annotations, list):
            raise ValueError(f"{paper_id}/{qid}: answers must be a list")
        normalized_answers = []
        for annotation_index, annotation in enumerate(raw_annotations):
            if not isinstance(annotation, dict) or not isinstance(annotation.get("answer"), dict):
                raise ValueError(f"{paper_id}/{qid}: answer annotation {annotation_index} is malformed")
            answer = annotation["answer"]
            extractive = answer.get("extractive_spans") or []
            evidence = answer.get("evidence") or []
            highlighted = answer.get("highlighted_evidence") or []
            if not isinstance(extractive, list) or not isinstance(evidence, list) or not isinstance(highlighted, list):
                raise ValueError(f"{paper_id}/{qid}: answer spans/evidence must be lists")
            normalized_answers.append({
                "unanswerable": bool(answer.get("unanswerable", False)),
                "extractive_spans": extractive,
                "yes_no": answer.get("yes_no"),
                "free_form_answer": answer.get("free_form_answer") or "",
                "evidence": evidence,
                "highlighted_evidence": highlighted,
                "annotation_id": annotation.get("annotation_id") or answer.get("annotation_id"),
            })
        references.append({
            "query_id": qid,
            "paper_id": paper_id,
            "answers": normalized_answers,
            "labels_available": bool(normalized_answers),
        })

    paper_record = {
        "paper_id": paper_id,
        "split": split,
        "title": title,
        "abstract": abstract,
        "chunk_count": len(chunks),
        "dataset": DATASET_REPO,
        "dataset_version": DATASET_VERSION,
        "license": LICENSE,
    }
    return paper_record, chunks, queries, references


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(path)


def prepare(output_dir: Path, *, download: bool = True) -> dict[str, Any]:
    raw_dir = output_dir / "raw"
    normalized_dir = output_dir / "normalized"
    archive_metadata: dict[str, Any] = {}
    if download:
        for archive_name, config in ARCHIVES.items():
            archive_metadata[archive_name] = download_verified(
                config["url"], config["sha256"], raw_dir / f"qasper-{archive_name}-v{DATASET_VERSION}.tgz",
                config["max_bytes"],
            )
    else:
        for archive_name, config in ARCHIVES.items():
            path = raw_dir / f"qasper-{archive_name}-v{DATASET_VERSION}.tgz"
            if not path.exists() or sha256_bytes(path.read_bytes()) != config["sha256"]:
                raise ValueError(f"Missing or invalid pinned archive: {path}")
            archive_metadata[archive_name] = {
                "path": str(path), "sha256": config["sha256"], "bytes": path.stat().st_size, "reused": True,
            }

    split_payloads: dict[str, dict[str, Any]] = {}
    for archive_name, config in ARCHIVES.items():
        archive_path = Path(archive_metadata[archive_name]["path"])
        for filename, split in config["files"].items():
            split_payloads[split] = read_json_from_tar(archive_path, filename)

    all_paper_ids: set[str] = set()
    split_stats: dict[str, Any] = {}
    total_questions = 0
    for split in ("train", "validation", "test"):
        source = split_payloads[split]
        if len(source) != EXPECTED_PAPERS[split]:
            raise ValueError(f"{split}: expected {EXPECTED_PAPERS[split]} papers, got {len(source)}")
        paper_rows: list[dict[str, Any]] = []
        chunk_rows: list[dict[str, Any]] = []
        query_rows: list[dict[str, Any]] = []
        reference_rows: list[dict[str, Any]] = []
        split_question_ids: set[str] = set()
        for source_key, paper in source.items():
            if not isinstance(paper, dict):
                raise ValueError(f"{split}/{source_key}: paper record must be an object")
            paper_row, chunks, queries, references = normalize_paper(split, str(source_key), paper)
            if paper_row["paper_id"] in all_paper_ids:
                raise ValueError(f"Paper-level split leakage/duplicate paper ID: {paper_row['paper_id']}")
            all_paper_ids.add(paper_row["paper_id"])
            paper_rows.append(paper_row)
            chunk_rows.extend(chunks)
            for query in queries:
                query_id = str(query["query_id"])
                if query_id in split_question_ids:
                    raise ValueError(f"{split}: duplicate question ID across papers: {query_id}")
                split_question_ids.add(query_id)
            query_rows.extend(queries)
            reference_rows.extend(references)
        write_jsonl(normalized_dir / "papers" / f"{split}.jsonl", paper_rows)
        write_jsonl(normalized_dir / "chunks" / f"{split}.jsonl", chunk_rows)
        write_jsonl(normalized_dir / "queries" / f"{split}.jsonl", query_rows)
        write_jsonl(normalized_dir / "references" / f"{split}.jsonl", reference_rows)
        labels_available = sum(1 for row in reference_rows if row["labels_available"])
        split_stats[split] = {
            "papers": len(paper_rows),
            "chunks": len(chunk_rows),
            "questions": len(query_rows),
            "questions_with_reference_annotations": labels_available,
            "gold_references_separate_from_query_inputs": True,
        }
        total_questions += len(query_rows)

    manifest = {
        "dataset": DATASET_REPO,
        "dataset_version": DATASET_VERSION,
        "dataset_revision_for_metadata": DATASET_REVISION,
        "license_claimed_by_official_dataset_card": LICENSE,
        "license_url": LICENSE_URL,
        "paper_citation_url": PAPER_URL,
        "dataset_card_url": DATASET_CARD_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive_checksums": archive_metadata,
        "split_statistics": split_stats,
        "total_papers": len(all_paper_ids),
        "total_questions": total_questions,
        "processing": {
            "full_text_source": "QASPER v0.3.0 package; original paper text is documented as extracted from S2ORC",
            "raw_archives_and_normalized_text_are_local_only": True,
            "gold_references_are_not_in_query_files": True,
            "train_dev_test_paper_ids_are_disjoint": True,
            "no_model_predictions_or_scores_generated": True,
        },
        "limitations": [
            "QASPER validates scientific-paper QA/evidence-selection tasks, not research-gap discovery quality.",
            "The dataset card declares CC BY 4.0; preserve attribution and verify source-content terms before redistribution or independent corpus re-hosting.",
            "The script records whether answer annotations are present per split; it does not assume test gold labels are available.",
        ],
    }
    normalized_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = normalized_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/benchmarks/qasper"))
    parser.add_argument("--verify-local-archives-only", action="store_true",
                        help="Do not download; verify pinned local archives and normalize them")
    args = parser.parse_args()
    try:
        manifest = prepare(args.output_dir, download=not args.verify_local_archives_only)
    except (OSError, ValueError, json.JSONDecodeError, tarfile.TarError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "manifest": str(args.output_dir / "normalized" / "manifest.json"),
                      "total_papers": manifest["total_papers"],
                      "total_questions": manifest["total_questions"],
                      "splits": manifest["split_statistics"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
