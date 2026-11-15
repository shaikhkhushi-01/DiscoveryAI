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
  const [livePapers, setLivePapers] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [searchResults, setSearchResults] = useState<any[]>([]);
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

  const runSearch = async () => {
    if (!query.trim() || !apiBase) return;
    try {
      const data = await apiPost("/api/v1/public/graph-rag/retrieve", { query: query.trim(), limit: 8 });
      setSearchResults(data.items || []);
      setActive("Papers");
    } catch {
      setSearchResults([]);
      setApiError("Search API is unavailable.");
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
              <div className="search-box"><span>⌕</span><input ref={searchInputRef} value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && runSearch()} placeholder="Search indexed papers… e.g. scientific RAG" /><button onClick={runSearch}>Explore</button></div>{searchResults.length > 0 && <div className="search-results">{searchResults.map((r:any) => <div key={r.id}><strong>{r.title}</strong><span>{r.year || "Year unavailable"}</span></div>)}</div>}
            </div>
            <div className="hero-orbit"><div className="orbit-ring ring-1" /><div className="orbit-ring ring-2" /><div className="orbit-core">KG<br /><small>REASONING</small></div><span className="node n1">Papers</span><span className="node n2">Methods</span><span className="node n3">Gaps</span><span className="node n4">Evidence</span></div>
          </section>

          <div className="notice"><span>i</span><div><strong>{live ? "Live API connected" : "Transparent demo state"}</strong><br />{live ? "API connectivity is confirmed. Counts reflect available API records; zero means no indexed corpus records yet." : apiError || "Connecting to the DiscoveryAI API…"}</div></div>

          <section className="stats-grid">
            <Stat label="Papers indexed" value={summary.papers.toLocaleString()} delta={overviewLoaded ? "API result" : "not loaded"} />
            <Stat label="Documents extracted" value={summary.concepts.toLocaleString()} delta={live ? "live data" : "unavailable"} />
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

function Stat({label,value,delta}:{label:string,value:string,delta:string}) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{delta} <i>vs previous period</i></small></div>;
}
function GraphNode({x,y,text,kind}:{x:string,y:string,text:string,kind:string}) {
  return <div className={"graph-node "+kind} style={{left:x,top:y}}><span />{text}</div>;
}
