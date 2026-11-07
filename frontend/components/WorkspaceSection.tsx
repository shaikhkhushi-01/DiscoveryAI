"use client";

import { FormEvent, useEffect, useState } from "react";

type SectionKey = "research-gaps" | "knowledge-graph" | "trends" | "hypotheses" | "experiments";
type Config = { title: string; eyebrow: string; description: string; endpoint: string; method?: "GET" | "POST"; protected?: boolean; actionLabel?: string; placeholder?: string; bodyKey?: string };

const configs: Record<SectionKey, Config> = {
  "research-gaps": {
    title: "Research Gaps", eyebrow: "EVIDENCE-BASED OPPORTUNITIES",
    description: "Candidate research gaps detected from the indexed literature. Review source evidence before treating a candidate as a validated gap.",
    endpoint: "/api/v1/public/gaps?limit=50",
  },
  "knowledge-graph": {
    title: "Knowledge Graph", eyebrow: "CONNECTED SCIENTIFIC KNOWLEDGE",
    description: "Explore the nodes and relationships stored in the DiscoveryAI knowledge graph.",
    endpoint: "/api/v1/knowledge-graph/overview", protected: true,
  },
  trends: {
    title: "Trends", eyebrow: "RESEARCH LANDSCAPE",
    description: "Topic and publication trend signals calculated from the available research corpus.",
    endpoint: "/api/v1/public/trends?limit=50",
  },
  hypotheses: {
    title: "Hypotheses", eyebrow: "RESEARCH HYPOTHESIS GENERATION",
    description: "Generate candidate hypotheses from a research question using the indexed corpus. Treat outputs as proposals that require expert review.",
    endpoint: "/api/v1/intelligence/hypotheses", method: "POST", protected: true,
    actionLabel: "Generate hypotheses", placeholder: "e.g. How can retrieval evaluation improve evidence grounding in scientific RAG systems?", bodyKey: "question",
  },
  experiments: {
    title: "Experiments", eyebrow: "DISCOVERY WORKFLOW",
    description: "Run the available discovery workflow to turn a research question into structured next-step suggestions. This version does not yet save or execute laboratory/computational experiments.",
    endpoint: "/api/v1/agents/discover", method: "POST", protected: true,
    actionLabel: "Run discovery workflow", placeholder: "Describe the research question or candidate gap you want to investigate…", bodyKey: "question",
  },
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://discoveryai-6dmk.onrender.com";

export default function WorkspaceSection({ section }: { section: SectionKey }) {
  const config = configs[section];
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [question, setQuestion] = useState("");
  const [data, setData] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const saved = window.sessionStorage.getItem("discoveryai_access_token") || "";
    setToken(saved);
  }, []);

  async function request(url: string, options: RequestInit = {}) {
    const response = await fetch(API_BASE + url, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: "Bearer " + token } : {}),
        ...(options.headers || {}),
      },
      cache: "no-store",
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail || payload);
      throw new Error(detail || "Request failed (" + response.status + ").");
    }
    return payload;
  }

  async function load() {
    setBusy(true); setError(""); setNotice("");
    try {
      const result = await request(config.endpoint);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load this section.");
    } finally { setBusy(false); }
  }

  useEffect(() => {
    if (!config.protected || token) void load();
    // Reload when the user signs in; config is stable for the selected section.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, section]);

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      const response = await fetch(API_BASE + "/api/v1/auth/login", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Sign-in failed. Check your credentials.");
      window.sessionStorage.setItem("discoveryai_access_token", payload.access_token);
      setToken(payload.access_token); setPassword(""); setNotice("Signed in successfully.");
    } catch (e) { setError(e instanceof Error ? e.message : "Sign-in failed."); }
    finally { setBusy(false); }
  }

  async function runAction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (question.trim().length < 5) { setError("Please enter a research question with at least 5 characters."); return; }
    setBusy(true); setError(""); setNotice(""); setData(null);
    try {
      const result = await request(config.endpoint, {
        method: config.method || "POST",
        body: JSON.stringify({ [config.bodyKey || "question"]: question.trim() }),
      });
      setData(result); setNotice("Request completed. Review the output and verify its evidence before relying on it.");
    } catch (e) { setError(e instanceof Error ? e.message : "The request failed."); }
    finally { setBusy(false); }
  }

  const needsAction = config.method === "POST";

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/"><span className="brand-mark">D</span><div><strong>DiscoveryAI</strong><small>Scientific Intelligence</small></div></a>
        <nav>
          <a className="nav-item" href="/">Overview</a>
          <a className={section === "research-gaps" ? "nav-item active" : "nav-item"} href="/research-gaps">Research Gaps</a>
          <a className={section === "knowledge-graph" ? "nav-item active" : "nav-item"} href="/knowledge-graph">Knowledge Graph</a>
          <a className="nav-item" href="/papers">Papers</a>
          <a className={section === "trends" ? "nav-item active" : "nav-item"} href="/trends">Trends</a>
          <a className={section === "hypotheses" ? "nav-item active" : "nav-item"} href="/hypotheses">Hypotheses</a>
          <a className={section === "experiments" ? "nav-item active" : "nav-item"} href="/experiments">Experiments</a>
        </nav>
        <div className="sidebar-bottom"><div className="status"><span className="live-dot" /> Connected workspace</div><div className="version">DiscoveryAI · Research tools</div></div>
      </aside>
      <section className="workspace">
        <header className="topbar"><div><p className="eyebrow">SCIENTIFIC DISCOVERY WORKSPACE</p><h1>{config.title}</h1></div><div className="top-actions"><span className="demo-pill">{error ? "API ERROR" : config.protected && !token ? "SIGN IN REQUIRED" : data !== null ? "LIVE DATA" : "CONNECTING"}</span><a className="icon-btn" href="/">⌂</a></div></header>
        <div className="content">
          <section className="panel">
            <span className="label">{config.eyebrow}</span>
            <h2 style={{ font: "600 25px 'Space Grotesk'", margin: "8px 0" }}>{config.title}</h2>
            <p style={{ color: "#8490a2", fontSize: 12, lineHeight: 1.7, maxWidth: 850 }}>{config.description}</p>
            {config.protected && !token ? (
              <form onSubmit={signIn} style={{ display: "grid", gap: 12, maxWidth: 430, marginTop: 22 }}>
                <div className="notice"><span>i</span><div><strong>Sign in required</strong><br />This research API requires your DiscoveryAI researcher account.</div></div>
                <label style={labelStyle}>Email<input type="email" required autoComplete="username" value={email} onChange={e=>setEmail(e.target.value)} style={inputStyle}/></label>
                <label style={labelStyle}>Password<input type="password" required autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} style={inputStyle}/></label>
                <button className="primary" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
              </form>
            ) : needsAction ? (
              <form onSubmit={runAction} style={{ display: "grid", gap: 12, maxWidth: 800, marginTop: 22 }}>
                <label style={labelStyle}>Research question<textarea required minLength={5} value={question} onChange={e=>setQuestion(e.target.value)} placeholder={config.placeholder} rows={4} style={{...inputStyle, resize:"vertical"}}/></label>
                <div><button className="primary" disabled={busy}>{busy ? "Working…" : config.actionLabel}</button></div>
              </form>
            ) : (
              <div style={{ display:"flex", gap:10, alignItems:"center", marginTop:18 }}>
                <button className="primary" onClick={load} disabled={busy}>{busy ? "Loading…" : "Refresh data"}</button>
                <span className="muted">Live API response · no illustrative sample records</span>
              </div>
            )}
            {error && <div role="alert" style={{ marginTop:16, color:"#ff9d9d", fontSize:12 }}>{error}</div>}
            {notice && <div role="status" className="notice" style={{ marginTop:16 }}>{notice}</div>}
          </section>
          {data !== null && <section className="panel" style={{ marginTop:16 }}>
            <div className="panel-head"><div><span className="label">LIVE RESPONSE</span><h3>{needsAction ? "Generated output" : "Retrieved records"}</h3></div><span className="muted">{Array.isArray(data) ? data.length + " items" : "API result"}</span></div>
            <ResultView value={data}/>
          </section>}
        </div>
      </section>
    </main>
  );
}

function ResultView({ value }: { value: any }) {
  if (Array.isArray(value)) {
    if (!value.length) return <p className="muted">No records returned by the API yet.</p>;
    return <div>{value.map((item, index) => <article key={index} style={{ padding:"14px 0", borderTop:"1px solid #1a2634" }}><strong style={{fontSize:13, color:"#dce5ef"}}>{item.title || item.name || item.topic || item.label || "Record " + (index+1)}</strong><pre style={preStyle}>{JSON.stringify(item, null, 2)}</pre></article>)}</div>;
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value);
    return <div>{entries.map(([key, item]) => <div key={key} style={{ padding:"12px 0", borderTop:"1px solid #1a2634" }}><strong style={{fontSize:11, color:"#5ee7c4", textTransform:"capitalize"}}>{key.replace(/_/g," ")}</strong>{Array.isArray(item) ? <ResultView value={item}/> : item && typeof item === "object" ? <pre style={preStyle}>{JSON.stringify(item, null, 2)}</pre> : <p style={{fontSize:12, color:"#b1bdcc", whiteSpace:"pre-wrap"}}>{String(item ?? "—")}</p>}</div>)}</div>;
  }
  return <pre style={preStyle}>{String(value ?? "No data returned.")}</pre>;
}

const labelStyle: React.CSSProperties = { color:"#aeb9c8", fontSize:12, display:"grid", gap:6 };
const inputStyle: React.CSSProperties = { width:"100%", padding:"11px 12px", border:"1px solid #293747", borderRadius:8, background:"#070c13", color:"#e9edf5", outline:"none", font:"12px 'DM Sans'" };
const preStyle: React.CSSProperties = { whiteSpace:"pre-wrap", overflowX:"auto", color:"#9eacbd", background:"#070c13", border:"1px solid #1a2634", borderRadius:8, padding:12, fontSize:10, lineHeight:1.6, marginTop:8 };
