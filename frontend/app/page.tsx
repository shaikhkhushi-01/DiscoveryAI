"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../lib/api";

const gaps = [
  { title: "Cross-dataset robustness evaluation", type: "Missing experiment", score: 86, evidence: 12 },
  { title: "Long-tail scientific benchmark", type: "Dataset gap", score: 81, evidence: 9 },
  { title: "Domain transfer beyond benchmark setting", type: "Application gap", score: 74, evidence: 15 },
];

const papers = [
  { title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", year: 2020, tags: ["RAG", "Retrieval"] },
  { title: "GraphRAG: Unlocking LLM Discovery on Text Corpora", year: 2024, tags: ["GraphRAG", "Knowledge Graph"] },
  { title: "Scientific Document Understanding with Multimodal Models", year: 2025, tags: ["Scientific NLP", "Multimodal"] },
];

export default function Home() {
  const [active, setActive] = useState("Overview");
  const [live, setLive] = useState(false);
  const [summary, setSummary] = useState({ papers: 1248, concepts: 7936, gaps: 184, evidence: 14200 });
  const [liveGaps, setLiveGaps] = useState(gaps);
  const [livePapers, setLivePapers] = useState(papers);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [apiError, setApiError] = useState("");
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "";

  useEffect(() => {
    if (!apiBase) return;
    Promise.all([
      apiGet("/api/v1/gaps?limit=10"),
      apiGet("/api/v1/trends?limit=20"),
    ]).then(([g, t]) => {
      setLive(true);
      setLiveGaps((g.items || []).map((x: any) => ({
        title: x.title,
        type: x.gap_type || x.type || "Research gap",
        score: x.discovery_score ?? x.score ?? "—",
        evidence: x.retrieval_evidence_count ?? x.evidence_count ?? 0
      })));
      setApiError("");
    }).catch(() => {
      setLive(false);
      setApiError("Live scientific APIs are unavailable. Showing representative interface data.");
    });
  }, [apiBase]);

  const runSearch = async () => {
    if (!query.trim() || !apiBase) return;
    try {
      const data = await apiGet("/api/v1/graph-rag/search?q=" + encodeURIComponent(query));
      setSearchResults(data.items || []);
      setActive("Papers");
    } catch {
      setSearchResults([]);
      setApiError("Search API is unavailable.");
    }
  };
