#!/usr/bin/env python3
"""Run a clearly labelled TF-IDF nearest-neighbour baseline on weak labels.

This is a text-similarity / label-transfer baseline, not a gold benchmark or a
claim of research-gap discovery. Fit uses train abstracts and inferred gaps
only; evaluation labels are used only for metrics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalised_hash(text: str) -> str:
    normalised = " ".join(text.lower().split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _token_f1(reference: str, prediction: str) -> float:
    from collections import Counter
    ref, pred = Counter(_tokens(reference)), Counter(_tokens(prediction))
    overlap = sum((ref & pred).values())
    if not ref and not pred:
        return 1.0
    if not overlap:
        return 0.0
    precision = overlap / sum(pred.values())
    recall = overlap / sum(ref.values())
    return 2 * precision * recall / (precision + recall)


def _lcs_length(a: list[str], b: list[str]) -> int:
    # One-row dynamic programming keeps memory bounded by the shorter sequence.
    if len(a) < len(b):
        a, b = b, a
    previous = [0] * (len(b) + 1)
    for token_a in a:
        current = [0]
        for j, token_b in enumerate(b, start=1):
            current.append(previous[j - 1] + 1 if token_a == token_b
                           else max(previous[j], current[j - 1]))
        previous = current
    return previous[-1]


def _rouge_l_f1(reference: str, prediction: str) -> float:
    ref, pred = _tokens(reference), _tokens(prediction)
    if not ref and not pred:
        return 1.0
    if not ref or not pred:
        return 0.0
    lcs = _lcs_length(ref, pred)
    precision, recall = lcs / len(pred), lcs / len(ref)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "token_f1_mean": _mean([row["token_f1"] for row in rows]),
        "rouge_l_f1_mean": _mean([row["rouge_l_f1"] for row in rows]),
        "cosine_similarity_mean": _mean([row["cosine_similarity"] for row in rows]),
    }


def run(input_path: Path, output_path: Path, split: str) -> dict[str, Any]:
    artifact = json.loads(input_path.read_text(encoding="utf-8"))
    if artifact.get("artifact_type") != "weak_label_research_gap_dataset":
        raise ValueError("Input is not the expected weak-label artifact")
    eligibility = artifact.get("evaluation_eligibility", {})
    if eligibility.get("status") != "not_gold_benchmark_compatible":
        raise ValueError("Refusing artifact without explicit non-gold eligibility marker")

    records = artifact.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Artifact records must be a non-empty list")
    train = [r for r in records if r.get("split") == "train"]
    evaluation = [r for r in records if r.get("split") == split]
    if not train or not evaluation:
        raise ValueError(f"Need non-empty train and {split} partitions")

    required = ("paper_id", "abstract", "research_gap_llm_inferred",
                "generator_model", "primary_category")
    for row in train + evaluation:
        if any(not str(row.get(key, "")).strip() for key in required):
            raise ValueError("A train/evaluation record is missing a required field")
    train_ids = {row["paper_id"] for row in train}
    if any(row["paper_id"] in train_ids for row in evaluation):
        raise ValueError("Paper ID overlap between train and evaluation split")
    train_hashes = {_normalised_hash(row["abstract"]) for row in train}
    if any(_normalised_hash(row["abstract"]) in train_hashes for row in evaluation):
        raise ValueError("Exact normalized abstract overlap across train/evaluation")

    vectorizer = TfidfVectorizer(
        lowercase=True, strip_accents="unicode", stop_words="english",
        ngram_range=(1, 2), min_df=2, max_features=100_000, sublinear_tf=True,
    )
    train_matrix = vectorizer.fit_transform([row["abstract"] for row in train])
    eval_matrix = vectorizer.transform([row["abstract"] for row in evaluation])
    similarities = cosine_similarity(eval_matrix, train_matrix)

    results: list[dict[str, Any]] = []
    for index, row in enumerate(evaluation):
        best_index = int(similarities[index].argmax())
        prediction = train[best_index]["research_gap_llm_inferred"]
        reference = row["research_gap_llm_inferred"]
        results.append({
            "paper_id": row["paper_id"],
            "split": split,
            "generator_model": row["generator_model"],
            "primary_category": row["primary_category"],
            "nearest_train_paper_id": train[best_index]["paper_id"],
            "cosine_similarity": float(similarities[index, best_index]),
            "reference_is_llm_inferred": True,
            "prediction_method": "copy research_gap_llm_inferred from nearest TF-IDF train abstract",
            "prediction": prediction,
            "reference": reference,
            "token_f1": _token_f1(reference, prediction),
            "rouge_l_f1": _rouge_l_f1(reference, prediction),
        })

    by_generator: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        by_generator[row["generator_model"]].append(row)
        by_category[row["primary_category"]].append(row)

    report = {
        "report_type": "weak_label_exploratory_nearest_neighbor_baseline",
        "scientific_status": "exploratory_weak_label_only_not_gold_evaluation",
        "source_dataset": artifact.get("source", {}),
        "method": {
            "name": "TF-IDF cosine nearest-neighbour label transfer",
            "input": "abstract only",
            "target": "research_gap_llm_inferred",
            "fit_partition": "train only",
            "evaluation_partition": split,
            "vectorizer": "word unigram/bigram TF-IDF; English stop words; min_df=2; max_features=100000",
            "prediction": "copy target text from the most similar training abstract",
            "metrics": ["token_f1_mean", "rouge_l_f1_mean", "cosine_similarity_mean"],
        },
        "counts": {"train": len(train), "evaluation": len(evaluation)},
        "overall": _summarise(results),
        "by_generator_model": {key: _summarise(value) for key, value in sorted(by_generator.items())},
        "by_primary_category": {key: _summarise(value) for key, value in sorted(by_category.items())},
        "limitations": [
            "Targets are LLM-inferred labels, not expert-validated ground truth.",
            "This measures similarity-based reproduction of dataset phrasing, not scientific gap discovery.",
            "ROUGE-L and token F1 measure lexical overlap and do not establish semantic correctness.",
            "The source split is random, not chronological; no future-generalization claim is supported.",
            "Generator style and category imbalance can confound subgroup metrics.",
            "Nearest-neighbour label transfer is a simple retrieval baseline, not a trained generative model.",
        ],
        "predictions": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Imported weak-label JSON artifact")
    parser.add_argument("--output", type=Path, required=True, help="Report JSON destination")
    parser.add_argument("--split", choices=("validation", "test"), default="validation")
    args = parser.parse_args()
    report = run(args.input, args.output, args.split)
    print(json.dumps({
        "ok": True,
        "report_type": report["report_type"],
        "scientific_status": report["scientific_status"],
        "split": args.split,
        "counts": report["counts"],
        "overall": report["overall"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
