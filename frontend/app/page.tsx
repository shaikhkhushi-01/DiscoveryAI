"use client";

import { useState } from "react";

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

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">D</span><div><strong>DiscoveryAI</strong><small>Scientific Intelligence</small></div></div>
        <nav>
          {["Overview", "Research Gaps", "Knowledge Graph", "Papers", "Trends", "Hypotheses", "Experiments"].map((item) => (
            <button key={item} className={active === item ? "nav-item active" : "nav-item"} onClick={() => setActive(item)}>
              <span className="nav-dot" />{item}
            </button>
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
            <span className="demo-pill">DEMO DATA</span>
            <button className="icon-btn">⌕</button>
            <div className="avatar">AI</div>
          </div>
        </header>

        <div className="content">
          <section className="hero">
            <div>
              <span className="label">RESEARCH OPPORTUNITY ENGINE</span>
              <h2>Find what the literature<br /><em>has not answered yet.</em></h2>
              <p>Evidence-grounded analysis across papers, methods, datasets, experiments and research gaps.</p>
              <div className="search-box"><span>⌕</span><input placeholder="Ask a research question… e.g. What experiments are missing in scientific RAG?" /><button>Explore</button></div>
            </div>
            <div className="hero-orbit"><div className="orbit-ring ring-1" /><div className="orbit-ring ring-2" /><div className="orbit-core">KG<br /><small>REASONING</small></div><span className="node n1">Papers</span><span className="node n2">Methods</span><span className="node n3">Gaps</span><span className="node n4">Evidence</span></div>
          </section>

          <div className="notice"><span>i</span><div><strong>Transparent demo state</strong><br />The dashboard is connected to the DiscoveryAI interface layer. Metrics and gap cards below are representative UI data until the live ingestion, vector search and graph services are running.</div></div>

          <section className="stats-grid">
            <Stat label="Papers indexed" value="1,248" delta="+18.4%" />
            <Stat label="Concepts extracted" value="7,936" delta="+12.1%" />
            <Stat label="Candidate gaps" value="184" delta="+9.7%" />
            <Stat label="Evidence links" value="14.2K" delta="+21.6%" />
          </section>

          <section className="grid-2">
            <div className="panel">
              <div className="panel-head"><div><span className="label">OPPORTUNITIES</span><h3>Research gaps detected</h3></div><button className="text-btn">View all →</button></div>
              <div className="gap-list">{gaps.map((g) => <div className="gap-row" key={g.title}><div className="gap-icon">◈</div><div className="gap-main"><strong>{g.title}</strong><span>{g.type} · {g.evidence} evidence links</span></div><div className="score"><b>{g.score}</b><small>DS</small></div></div>)}</div>
            </div>

            <div className="panel">
              <div className="panel-head"><div><span className="label">RESEARCH LANDSCAPE</span><h3>Topic activity</h3></div><span className="muted">2019 — 2025</span></div>
              <div className="chart"><div className="y-labels"><span>High</span><span>Mid</span><span>Low</span></div><div className="bars">{[38,52,44,67,61,78,91].map((h,i)=><div className="bar-wrap" key={i}><div className="bar" style={{height: h + "%"}} /><span>{2019+i}</span></div>)}</div></div>
              <div className="trend-note"><span className="trend-up">↗ 24%</span> growth in indexed research activity</div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-head"><div><span className="label">EVIDENCE EXPLORER</span><h3>Scientific knowledge landscape</h3></div><div className="legend"><span><i className="legend-dot paper" /> Papers</span><span><i className="legend-dot method" /> Methods</span><span><i className="legend-dot gap" /> Gaps</span></div></div>
            <div className="graph">
              <div className="graph-center">Scientific<br /><b>Discovery</b></div>
              <GraphNode x="12%" y="22%" text="RAG" kind="paper" /><GraphNode x="34%" y="12%" text="GraphRAG" kind="method" /><GraphNode x="67%" y="20%" text="Benchmarks" kind="paper" /><GraphNode x="82%" y="43%" text="Dataset gap" kind="gap" /><GraphNode x="70%" y="72%" text="Evaluation" kind="method" /><GraphNode x="35%" y="76%" text="Scientific NLP" kind="paper" /><GraphNode x="15%" y="55%" text="Evidence" kind="method" />
              <svg className="graph-lines" viewBox="0 0 100 100" preserveAspectRatio="none"><line x1="50" y1="50" x2="15" y2="27" /><line x1="50" y1="50" x2="37" y2="18" /><line x1="50" y1="50" x2="70" y2="26" /><line x1="50" y1="50" x2="84" y2="49" /><line x1="50" y1="50" x2="72" y2="78" /><line x1="50" y1="50" x2="39" y2="82" /><line x1="50" y1="50" x2="19" y2="61" /></svg>
            </div>
          </section>

          <section className="grid-2">
            <div className="panel">
              <div className="panel-head"><div><span className="label">PAPER INTELLIGENCE</span><h3>Recently analyzed</h3></div></div>
              <div className="paper-list">{papers.map((p) => <div className="paper" key={p.title}><div className="paper-file">PDF</div><div><strong>{p.title}</strong><span>{p.year} · {p.tags.map(t => <em key={t}>{t}</em>)}</span></div><button>→</button></div>)}</div>
            </div>
            <div className="panel opportunity"><span className="label">NEXT DISCOVERY</span><h3>Turn a gap into a hypothesis.</h3><p>Validated gaps can flow into experiment planning, hypothesis generation and evidence-backed research reports.</p><button className="primary">Open Discovery Flow →</button><div className="flow"><span>Gap</span><i>→</i><span>Hypothesis</span><i>→</i><span>Experiment</span></div></div>
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
