"use client";

import { useEffect, useRef, useState } from "react";
import { apiGet, apiPost } from "../lib/api";

export default function Home() {
  const [active, setActive] = useState("Overview");
  const [live, setLive] = useState(false);
  const [overviewLoaded, setOverviewLoaded] = useState(false);
  const [gapsLoaded, setGapsLoaded] = useState(false);
  const [summary, setSummary] = useState({ papers: 0, concepts: 0, gaps: 0, evidence: 0 });
  const [liveGaps, setLiveGaps] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchStatus, setSearchStatus] = useState("");
  const [searchAnswer, setSearchAnswer] = useState("");
  const [searching, setSearching] = useState(false);
  const [apiError, setApiError] = useState("");
  // Override with NEXT_PUBLIC_API_URL to point at the deployed backend.
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "https://discoveryai-6dmk.onrender.com";

  useEffect(() => {
    let cancelled = false;

    // Load each endpoint independently: a trends failure must not hide working
    // overview/gap data and leave every dashboard metric at zero.
    apiGet("/api/v1/public/overview")
      .then((overview) => {
        if (cancelled) return;
        setSummary((current) => ({
          ...current,
          papers: overview.papers_indexed ?? 0,
          concepts: overview.concepts ?? 0,
          evidence: overview.evidence_links ?? 0,
        }));
        setOverviewLoaded(true);
        setLive(true);
      })
      .catch(() => {
        if (!cancelled) setApiError("Could not load overview metrics from the live API.");
      });

    apiGet("/api/v1/public/gaps?limit=10")
      .then((g) => {
        if (cancelled) return;
        setLiveGaps((g.items || []).map((x: any) => ({
          title: x.title || x.topic || "Untitled research gap",
          type: x.gap_type || x.type || "Research gap",
          score: x.discovery_score ?? x.score ?? x.confidence ?? "—",
          evidence: x.retrieval_evidence_count ?? x.evidence_count ?? 0,
        })));
        setSummary((current) => ({ ...current, gaps: g.count ?? (g.items || []).length }));
        setGapsLoaded(true);
        setLive(true);
      })
      .catch(() => {
        if (!cancelled) setApiError("Research-gap data could not be loaded from the live API.");
      });

    // Trends are not currently rendered from this endpoint, so its failure
    // should not affect dashboard metrics.
    apiGet("/api/v1/public/trends?limit=20").catch(() => undefined);

    return () => { cancelled = true; };
  }, []);

  const groupedSearchResults = (() => {
    type EvidenceGroup = { title: string; year: string; items: { item: any; index: number }[] };
    const groups = new Map<string, EvidenceGroup>();
    searchResults.forEach((item: any, index: number) => {
      const title = item.title || item.paper_title || item.node_name || "Evidence result";
      const key = String(item.paper_id ?? item.document_id ?? title);
      const group = groups.get(key) ?? { title, year: item.year || "", items: [] };
      group.items.push({ item, index });
      groups.set(key, group);
    });
    return Array.from(groups.values());
  })();

  const runSearch = async () => {
    if (!query.trim() || searching) return;
    setSearching(true);
    setSearchStatus("");
    setSearchResults([]);
    setSearchAnswer("");
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 45000);
    try {
      const response = await fetch(`${apiBase}/api/v1/public/graph-rag/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim(), limit: 8 }),
        cache: "no-store",
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`API request failed (${response.status})`);
      const data = await response.json();
      const results = Array.isArray(data.sources) ? data.sources : [];
      setSearchResults(results);
      setSearchAnswer(typeof data.answer === "string" ? data.answer : "The API returned evidence but no answer text.");
      setSearchStatus(results.length ? `Answer generated from ${results.length} retrieved evidence item${results.length === 1 ? "" : "s"}.` : "No relevant evidence was identified within the indexed corpus and search scope.");
    } catch (error) {
      setSearchResults([]);
      setSearchStatus(error instanceof Error && error.name === "AbortError" ? "Search timed out after 45 seconds. The backend retrieval or database service may be unavailable." : error instanceof Error ? `Search failed: ${error.message}` : "Search failed: the API could not be reached.");
    } finally {
      window.clearTimeout(timeout);
      setSearching(false);
    }
  };

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">D</span><div><strong>DiscoveryAI</strong><small>Scientific Intelligence</small></div></div>
        <nav>
          {[
            ["Overview", "/"],
            ["Research Gaps", "/research-gaps"],
            ["Knowledge Graph", "/knowledge-graph"],
            ["Papers", "/papers"],
            ["Trends", "/trends"],
            ["Hypotheses", "/hypotheses"],
            ["Experiments", "/experiments"],
          ].map(([item, href]) => (
            <a key={item} href={href} className={item === "Overview" ? "nav-item active" : "nav-item"}>
              <span className="nav-dot" />{item}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="status"><span className="live-dot" /> Pipeline ready</div>
          <div className="version">DiscoveryAI v0.1 · Phase 4 foundation</div>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">SCIENTIFIC DISCOVERY WORKSPACE</p>
            <h1>{active}</h1>
          </div>
          <div className="top-actions">
            <span className={live ? "demo-pill live-pill" : "demo-pill"}>{live ? "LIVE DATA" : "DEMO DATA"}</span>
            <button className="icon-btn" type="button" aria-label="Focus research search" onClick={() => searchInputRef.current?.focus()}>⌕</button>
            <div className="avatar">AI</div>
          </div>
        </header>

        <div className="content">
          <section className="hero">
            <div>
              <span className="label">RESEARCH OPPORTUNITY ENGINE</span>
              <h2>Find what the literature<br /><em>has not answered yet.</em></h2>
              <p>Evidence-grounded analysis across papers, methods, datasets, experiments and research gaps.</p>
              <div className="search-box"><span>⌕</span><input ref={searchInputRef} value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && runSearch()} placeholder="Search indexed papers… e.g. scientific RAG" /><button onClick={runSearch} disabled={searching || !query.trim()}>{searching ? "Searching…" : "Explore"}</button></div>{searchStatus && <p className="muted" role="status" aria-live="polite" style={{ marginTop: 10 }}>{searchStatus}</p>}{searchAnswer && <div className="panel" style={{ marginTop: 12 }}><span className="label">EVIDENCE-GROUNDED ANSWER</span><AnswerWithCitations answer={searchAnswer} /></div>}{searchResults.length > 0 && <div className="search-results">{groupedSearchResults.map((group, groupIndex) => <section key={`${group.title}-${groupIndex}`} style={{ border: "1px solid rgba(148,163,184,.2)", borderRadius: 12, padding: 16, marginTop: 12 }}><div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline", flexWrap: "wrap" }}><strong>{group.title}</strong><span>{group.items.length} evidence passage{group.items.length === 1 ? "" : "s"}{group.year ? ` · ${group.year}` : ""}</span></div>{group.items.map(({ item, index }) => <div id={`evidence-${index + 1}`} key={item.id ?? `${item.paper_id ?? "result"}-${index}`} style={{ scrollMarginTop: 24, borderTop: "1px solid rgba(148,163,184,.14)", marginTop: 12, paddingTop: 12 }}><span style={{ fontSize: 12, opacity: .75 }}>Evidence {index + 1}{item.section ? ` · ${item.section}` : item.relationship ? ` · ${item.relationship}` : ""}</span>{item.text && <p style={{ marginTop: 6 }}>{item.text}</p>}</div>)}</section>)}</div>}
            </div>
            <div className="hero-orbit"><div className="orbit-ring ring-1" /><div className="orbit-ring ring-2" /><div className="orbit-core">KG<br /><small>REASONING</small></div><span className="node n1">Papers</span><span className="node n2">Methods</span><span className="node n3">Gaps</span><span className="node n4">Evidence</span></div>
          </section>

          <div className="notice"><span>i</span><div><strong>{live ? "Live API connected" : "Transparent demo state"}</strong><br />{live ? "API connectivity is confirmed. Counts reflect available API records; zero means no indexed corpus records yet." : apiError || "Connecting to the DiscoveryAI API…"}</div></div>

          <section className="stats-grid">
            <Stat label="Papers indexed" value={summary.papers.toLocaleString()} delta={overviewLoaded ? "API result" : "not loaded"} />
            <Stat label="Documents extracted" value={summary.concepts.toLocaleString()} delta={overviewLoaded ? "API result" : "not loaded"} />
            <Stat label="Candidate gaps" value={summary.gaps.toLocaleString()} delta={live ? "live data" : "unavailable"} />
            <Stat label="Evidence links" value={summary.evidence.toLocaleString()} delta={live ? "live data" : "unavailable"} />
          </section>

          <section className="grid-2">
            <div className="panel">
              <div className="panel-head"><div><span className="label">OPPORTUNITIES</span><h3>Research gaps detected</h3></div><a className="text-btn" href="/research-gaps">View all →</a></div>
              <div className="gap-list">{liveGaps.length ? liveGaps.map((g) => <div className="gap-row" key={g.title}><div className="gap-icon">◈</div><div className="gap-main"><strong>{g.title}</strong><span>{g.type} · {g.evidence} evidence links</span></div><div className="score"><b>{g.score}</b><small>DS</small></div></div>) : <p className="muted">{live ? "No research gaps were returned by the API." : "Research gaps will appear when the live API is available."}</p>}</div>
            </div>

            <div className="panel">
              <div className="panel-head"><div><span className="label">RESEARCH LANDSCAPE</span><h3>Topic activity</h3></div><span className="muted">2019 — 2025</span></div>
              <div className="chart" style={{ minHeight: 180, display: "grid", placeItems: "center" }}><p className="muted">No verified trend series is connected yet. No synthetic values are shown.</p></div>
              <div className="trend-note">Live trend visualization is pending.</div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-head"><div><span className="label">EVIDENCE EXPLORER</span><h3>Scientific knowledge landscape</h3></div><div className="legend"><span><i className="legend-dot paper" /> Papers</span><span><i className="legend-dot method" /> Methods</span><span><i className="legend-dot gap" /> Gaps</span></div></div>
            <div className="graph" style={{ minHeight: 220, display: "grid", placeItems: "center" }}><p className="muted" style={{ textAlign: "center", maxWidth: 360 }}>No live graph records are available yet. Upload and successfully index papers to populate the knowledge graph.</p></div>
          </section>

          <section className="grid-2">
            <div className="panel">
              <div className="panel-head"><div><span className="label">PAPER INTELLIGENCE</span><h3>Recently analyzed</h3></div></div>
              <div className="paper-list"><p className="muted">Recent-paper feed is not connected to a public live endpoint yet. <a href="/papers">Open your private document library →</a></p></div>
            </div>
            <div className="panel opportunity"><span className="label">NEXT DISCOVERY</span><h3>Turn a gap into a hypothesis.</h3><p>Validated gaps can flow into experiment planning, hypothesis generation and evidence-backed research reports.</p><a className="primary" href="/hypotheses">Open Discovery Flow →</a><div className="flow"><span>Gap</span><i>→</i><span>Hypothesis</span><i>→</i><span>Experiment</span></div></div>
          </section>
        </div>
      </section>
    </main>
  );
}

function AnswerWithCitations({ answer }: { answer: string }) {
  let text = answer;
  try {
    const parsed = JSON.parse(answer);
    if (parsed && typeof parsed.answer === "string") text = parsed.answer;
  } catch {
    // The API may return plain text rather than a JSON-encoded answer.
  }

  const parts = text.split(/\[(VECTOR EVIDENCE\s+\d+(?:\s*,\s*VECTOR EVIDENCE\s+\d+)*)\]/g);
  return (
    <p style={{ whiteSpace: "pre-wrap", lineHeight: 1.75, marginTop: 12 }}>
      {parts.map((part, index) => {
        if (index % 2 === 0) return <span key={index}>{part}</span>;
        const citations = part.split(/,\s*/);
        return (
          <span key={index}>
            {citations.map((citation, citationIndex) => {
              const match = citation.match(/^VECTOR EVIDENCE\s+(\d+)$/);
              if (!match) return <span key={citationIndex}>{citation}</span>;
              const evidenceNumber = Number(match[1]);
              return (
                <a
                  key={citationIndex}
                  href={`#evidence-${evidenceNumber}`}
                  style={{ display: "inline-block", margin: "0 2px", color: "#5ee7c4", textDecoration: "underline", textUnderlineOffset: 3, fontWeight: 600 }}
                  title={`Jump to retrieved evidence ${evidenceNumber}`}
                >
                  [Evidence {evidenceNumber}]
                </a>
              );
            })}
          </span>
        );
      })}
    </p>
  );
}

function Stat({label,value,delta}:{label:string,value:string,delta:string}) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{delta} <i>vs previous period</i></small></div>;
}
