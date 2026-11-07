"use client";

import { useEffect, useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://discoveryai-6dmk.onrender.com";

type UploadItem = { name: string; status: string; message?: string };
type LibraryItem = { id: number; paper_id: number; title: string; doi?: string | null; page_count?: number | null; document_status: string; indexing?: { job_id: number; status: string; attempts: number; vector_status: string; graph_status: string; last_error?: string | null } | null };

export default function PapersPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [items, setItems] = useState<UploadItem[]>([]);
  const [library, setLibrary] = useState<LibraryItem[]>([]);
  const [libraryBusy, setLibraryBusy] = useState(false);
  const [libraryError, setLibraryError] = useState("");
  const [busy, setBusy] = useState(false);
  const [authBusy, setAuthBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const saved = window.sessionStorage.getItem("discoveryai_access_token");
    if (saved) setToken(saved);
  }, []);

  async function refreshLibrary() {
    if (!token) return;
    setLibraryBusy(true); setLibraryError("");
    try {
      const response = await fetch(API_BASE + "/api/v1/documents", { headers: { Authorization: "Bearer " + token }, cache: "no-store" });
      if (response.status === 401) { window.sessionStorage.removeItem("discoveryai_access_token"); setToken(""); throw new Error("Session expired. Please sign in again."); }
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Could not load document library.");
      setLibrary(Array.isArray(data.items) ? data.items : []);
    } catch (e) { setLibraryError(e instanceof Error ? e.message : "Could not load document library."); }
    finally { setLibraryBusy(false); }
  }

  useEffect(() => {
    if (!token) return;
    void refreshLibrary();
    const timer = window.setInterval(() => { void refreshLibrary(); }, 10000);
    return () => window.clearInterval(timer);
  }, [token]);

  async function login(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setNotice("");
    setAuthBusy(true);
    try {
      const response = await fetch(API_BASE + "/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Login failed. Check your email and password.");
      window.sessionStorage.setItem("discoveryai_access_token", data.access_token);
      setToken(data.access_token);
      setPassword("");
      setNotice("Login successful. You can now upload papers.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed.");
    } finally {
      setAuthBusy(false);
    }
  }

  async function uploadAll() {
    if (!token) {
      setError("Please sign in first. Uploading papers requires a researcher account.");
      return;
    }
    if (!files.length) {
      setError("Select one or more PDF files first.");
      return;
    }
    setBusy(true);
    setError("");
    setNotice("");
    const results: UploadItem[] = [...items];
    const alreadyQueued = new Set(items.filter(item => item.status === "Indexing queued").map(item => item.name));
    for (const file of files) {
      if (alreadyQueued.has(file.name)) continue;
      if (!file.name.toLowerCase().endsWith(".pdf") || file.type && file.type !== "application/pdf") {
        results.push({ name: file.name, status: "Failed", message: "Only PDF files are accepted." });
        setItems([...results]);
        continue;
      }
      try {
        const form = new FormData();
        form.append("file", file);
        const uploaded = await fetch(API_BASE + "/api/v1/documents/upload", {
          method: "POST",
          headers: { Authorization: "Bearer " + token },
          body: form,
        });
        const uploadData = await uploaded.json().catch(() => ({}));
        if (uploaded.status === 401) {
          results.push({ name: file.name, status: "Re-login required", message: "Session expired before this file could be uploaded." });
          setItems([...results]);
          window.sessionStorage.removeItem("discoveryai_access_token");
          setToken("");
          setError("Session expired. Sign in again, then click Upload and index to continue with the remaining PDFs. Already queued files will be skipped.");
          setBusy(false);
          return;
        }
        if (!uploaded.ok) {
          const detail = typeof uploadData.detail === "string" ? uploadData.detail : JSON.stringify(uploadData.detail || uploadData);
          throw new Error(detail || "PDF upload failed (" + uploaded.status + ").");
        }
        const documentId = uploadData.id;
        if (!documentId) throw new Error("Upload response did not include a document ID.");
        const indexed = await fetch(API_BASE + "/api/v1/documents/" + documentId + "/index", {
          method: "POST",
          headers: { Authorization: "Bearer " + token },
        });
        const indexData = await indexed.json().catch(() => ({}));
        if (indexed.status === 401) {
          results.push({ name: file.name, status: "Re-login required", message: "PDF uploaded; sign in again to queue indexing. Retrying is safe because duplicate PDF uploads return the existing document." });
          setItems([...results]);
          window.sessionStorage.removeItem("discoveryai_access_token");
          setToken("");
          setError("Session expired after upload. Sign in again and click Upload and index to resume; this PDF will be queued without creating a duplicate.");
          setBusy(false);
          return;
        }
        if (!indexed.ok) {
          const detail = typeof indexData.detail === "string" ? indexData.detail : JSON.stringify(indexData.detail || indexData);
          throw new Error("Uploaded, but indexing could not be queued: " + (detail || indexed.status));
        }
        results.push({ name: file.name, status: "Indexing queued", message: "Document " + documentId + " · job " + (indexData.job_id ?? "created") });
      } catch (e) {
        const message = e instanceof Error ? e.message : "Unexpected upload error.";
        results.push({ name: file.name, status: "Failed", message });
      }
      setItems([...results]);
    }
    setBusy(false);
    setNotice("Upload batch finished. Check each paper's status below; 'Indexing queued' means processing has been scheduled, not completed.");
  }

  function signOut() {
    window.sessionStorage.removeItem("discoveryai_access_token");
    setToken("");
    setNotice("Signed out.");
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/"><span className="brand-mark">D</span><div><strong>DiscoveryAI</strong><small>Scientific Intelligence</small></div></a>
        <nav>
          <a className="nav-item" href="/">Overview</a>
          <a className="nav-item active" href="/papers">Papers</a>
        </nav>
        <div className="sidebar-bottom"><div className="status"><span className="live-dot" /> Document workspace</div><div className="version">PDF ingestion and indexing</div></div>
      </aside>
      <section className="workspace">
        <header className="topbar"><div><p className="eyebrow">SCIENTIFIC DISCOVERY WORKSPACE</p><h1>Papers</h1></div><div className="top-actions"><span className="demo-pill">DOCUMENT LIBRARY</span><a className="icon-btn" href="/">⌂</a></div></header>
        <div className="content">
          <section className="panel" style={{ maxWidth: 920, margin: "0 auto" }}>
            <span className="label">CORPUS INGESTION</span>
            <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontSize: 26, margin: "8px 0" }}>Upload research papers</h2>
            <p style={{ color: "#8490a2", fontSize: 13, lineHeight: 1.6 }}>Add PDF papers to your private DiscoveryAI corpus. Each file is parsed and then queued for vector and knowledge-graph indexing.</p>

            {!token ? (
              <form onSubmit={login} style={{ display: "grid", gap: 12, maxWidth: 440, marginTop: 24 }}>
                <div className="notice"><span>i</span><div><strong>Researcher sign-in required</strong><br />The upload and indexing API is protected. Sign in with your DiscoveryAI account to continue.</div></div>
                <label style={{ color: "#aeb9c8", fontSize: 12 }}>Email<input required type="email" autoComplete="username" value={email} onChange={e => setEmail(e.target.value)} style={fieldStyle} /></label>
                <label style={{ color: "#aeb9c8", fontSize: 12 }}>Password<input required type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} style={fieldStyle} /></label>
                <button className="primary" disabled={authBusy} type="submit">{authBusy ? "Signing in…" : "Sign in"}</button>
              </form>
            ) : (
              <div style={{ marginTop: 20 }}>
                <div className="notice"><span>✓</span><div><strong>Signed in</strong><br />Your access token is held only in this browser tab session.</div><button type="button" className="text-btn" onClick={signOut}>Sign out</button></div>
                <input ref={inputRef} type="file" accept="application/pdf,.pdf" multiple onChange={e => { setFiles(Array.from(e.target.files || [])); setItems([]); setError(""); }} style={{ display: "none" }} />
                <div onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); const selected = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith(".pdf")); setFiles(selected); setItems([]); setError(selected.length ? "" : "Drop PDF files only."); }} onClick={() => inputRef.current?.click()} role="button" tabIndex={0} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") inputRef.current?.click(); }} style={{ border: "1px dashed #45675f", borderRadius: 12, padding: "34px 20px", textAlign: "center", cursor: "pointer", background: "#0c171b", marginTop: 18 }}>
                  <div style={{ fontSize: 28, color: "#5ee7c4" }}>＋</div>
                  <strong style={{ display: "block", margin: "8px 0", fontSize: 14 }}>Choose PDFs or drag them here</strong>
                  <span style={{ color: "#78869a", fontSize: 11 }}>Multiple PDF files supported</span>
                </div>
                {files.length > 0 && <div style={{ marginTop: 16 }}><strong style={{ fontSize: 12 }}>{files.length} PDF file(s) selected</strong><div style={{ maxHeight: 180, overflow: "auto", marginTop: 8 }}>{files.map((f, i) => <div key={f.name + i} style={{ padding: "7px 0", borderBottom: "1px solid #1a2634", color: "#9aa6b7", fontSize: 11 }}>{f.name} <span style={{ color: "#5f6d80" }}>· {(f.size / 1024 / 1024).toFixed(1)} MB</span></div>)}</div></div>}
                <button className="primary" type="button" disabled={busy || !files.length} onClick={uploadAll} style={{ marginTop: 18 }}>{busy ? "Uploading and queueing…" : "Upload and index selected PDFs"}</button>
              </div>
            )}
            {error && <div role="alert" style={{ marginTop: 16, color: "#ff9d9d", fontSize: 12 }}>{error}</div>}
            {notice && <div role="status" className="notice" style={{ marginTop: 16 }}>{notice}</div>}
          </section>
          {items.length > 0 && <section className="panel" style={{ maxWidth: 920, margin: "18px auto 0" }}><div className="panel-head"><div><span className="label">BATCH RESULTS</span><h3>Upload progress</h3></div><span className="muted">{items.filter(x => x.status === "Indexing queued").length}/{items.length} queued</span></div>{items.map((item, i) => <div key={item.name + i} style={{ padding: "12px 0", borderTop: "1px solid #1a2634" }}><strong style={{ display: "block", fontSize: 12 }}>{item.name}</strong><span style={{ color: item.status === "Failed" ? "#ff9d9d" : "#5ee7c4", fontSize: 11 }}>{item.status}</span>{item.message && <p style={{ margin: "4px 0 0", color: "#78869a", fontSize: 10 }}>{item.message}</p>}</div>)}</section>}
        </div>
      </section>
    </main>
  );
}

const fieldStyle: React.CSSProperties = { display: "block", width: "100%", marginTop: 6, padding: "11px 12px", border: "1px solid #293747", borderRadius: 8, background: "#070c13", color: "#e9edf5", outline: "none" };
