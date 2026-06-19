/*
File: App.tsx

Purpose:
Main entry point for the React QA Automation Dashboard. Renders a modern
dark-mode frontend that communicates with the GitHub REST API to monitor
test runs, trigger headless Selenium executions via workflow dispatches,
cache metrics locally, parse artifact zip contents, and display diagnostics.

Author: <Your Name>

Created: 2026-06-19
*/

import React, { useState, useEffect } from "react";
import JSZip from "jszip";
import {
  Activity,
  Play,
  FileText,
  Image,
  BookOpen,
  Settings,
  AlertCircle,
  CheckCircle,
  Loader,
  Download,
  Database,
  ShieldCheck,
  RefreshCw,
  Layers,
  Clock,
  Cpu
} from "lucide-react";

// Types for GitHub API objects
interface WorkflowRun {
  id: number;
  run_number: number;
  status: string;
  conclusion: string;
  html_url: string;
  created_at: string;
  trigger_user: string;
  artifacts_url: string;
}

interface Artifact {
  id: number;
  name: string;
  size_in_bytes: number;
  archive_download_url: string;
}

interface CachedData {
  latestStatus: string;
  latestSummary: string;
  reportMetadata: string;
  lastUpdated: string;
}

export default function App() {
  // 1. App State Configuration
  const [repoOwner, setRepoOwner] = useState("01mayankk");
  const [repoName, setRepoName] = useState("Enterprise-QA-Automation-Framework");
  const [activeTab, setActiveTab] = useState<"dashboard" | "execution" | "reports" | "screenshots" | "docs">("dashboard");
  
  // Transient in-memory token (Never saved in localStorage)
  const [githubPat, setGithubPat] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  // 2. Data State
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [apiError, setApiError] = useState("");
  
  // Dynamic triggering configuration
  const [envChoice, setEnvChoice] = useState("qa");
  const [browserChoice, setBrowserChoice] = useState("chrome");
  const [headlessChoice, setHeadlessChoice] = useState("true");
  const [retryChoice, setRetryChoice] = useState("2");
  
  // Trigger state monitoring
  const [dispatchStatus, setDispatchStatus] = useState<"idle" | "sending" | "success" | "error">("idle");
  const [dispatchMessage, setDispatchMessage] = useState("");

  // Extracted reports/screenshot states
  const [extractedReport, setExtractedReport] = useState<string | null>(null);
  const [extractingRunId, setExtractingRunId] = useState<number | null>(null);
  const [extractionError, setExtractionError] = useState("");
  const [extractedImages, setExtractedImages] = useState<string[]>([]);
  
  // Documentation content states
  const [docContent, setDocContent] = useState("");
  const [selectedDocPath, setSelectedDocPath] = useState("docs/LEARNING_GUIDE.md");
  const [loadingDoc, setLoadingDoc] = useState(false);

  // 3. Client Caching Layer Implementation
  const [cache, setCache] = useState<CachedData | null>(null);
  const [largeArtifactUrl, setLargeArtifactUrl] = useState<{ url: string; name: string } | null>(null);

  useEffect(() => {
    // Load cache from localStorage on start
    const storedCache = localStorage.getItem("qa_dashboard_cache");
    if (storedCache) {
      try {
        setCache(JSON.parse(storedCache));
      } catch (e) {
        console.error("Failed to parse local storage cache", e);
      }
    }

    // Load runs list cache on start (Stale-While-Revalidate pattern)
    const storedRuns = localStorage.getItem("qa_dashboard_runs_cache");
    if (storedRuns) {
      try {
        setWorkflowRuns(JSON.parse(storedRuns));
      } catch (e) {
        console.error("Failed to parse local storage runs cache", e);
      }
    }
  }, []);

  const saveToCache = (status: string, summary: string, metadata: string) => {
    const newCache: CachedData = {
      latestStatus: status,
      latestSummary: summary,
      reportMetadata: metadata,
      lastUpdated: new Date().toLocaleTimeString()
    };
    setCache(newCache);
    localStorage.setItem("qa_dashboard_cache", JSON.stringify(newCache));
  };

  // 4. API Core Logic
  const getFullRepoPath = () => `${repoOwner}/${repoName}`;

  // Fetch runs using public endpoints (No token needed for public repositories)
  const fetchRuns = async () => {
    setLoadingRuns(true);
    setApiError("");
    try {
      const response = await fetch(
        `https://api.github.com/repos/${getFullRepoPath()}/actions/runs`,
        {
          headers: githubPat ? { Authorization: `token ${githubPat}` } : {}
        }
      );
      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: Failed to retrieve runs.`);
      }
      const data = await response.json();
      
      const runs = (data.workflow_runs || []).map((run: any) => ({
        id: run.id,
        run_number: run.run_number,
        status: run.status,
        conclusion: run.conclusion,
        html_url: run.html_url,
        created_at: run.created_at,
        trigger_user: run.triggering_actor?.login || "GitHub System",
        artifacts_url: run.artifacts_url
      }));

      setWorkflowRuns(runs);
      localStorage.setItem("qa_dashboard_runs_cache", JSON.stringify(runs));

      // Populate Cache with latest run
      if (runs.length > 0) {
        const latestRun = runs[0];
        saveToCache(
          latestRun.status,
          latestRun.conclusion || "Pending",
          `Run #${latestRun.run_number} triggered by ${latestRun.trigger_user}`
        );
      }
    } catch (err: any) {
      setApiError(err.message || "An unknown error occurred.");
    } finally {
      setLoadingRuns(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, [repoOwner, repoName]);

  // Trigger dispatch (Requires user PAT)
  const triggerWorkflow = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubPat) {
      setDispatchStatus("error");
      setDispatchMessage("A Personal Access Token (PAT) is required to trigger execution workflows.");
      return;
    }

    setDispatchStatus("sending");
    setDispatchMessage("Dispatching GitHub REST trigger event...");

    try {
      const response = await fetch(
        `https://api.github.com/repos/${getFullRepoPath()}/actions/workflows/main.yml/dispatches`,
        {
          method: "POST",
          headers: {
            Authorization: `token ${githubPat}`,
            Accept: "application/vnd.github+json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            ref: "main",
            inputs: {
              environment: envChoice,
              browser: browserChoice,
              headless: headlessChoice,
              retry_count: retryChoice
            }
          })
        }
      );

      if (response.status === 204) {
        setDispatchStatus("success");
        setDispatchMessage("Workflow run successfully dispatched! Live polling has started.");
        
        // Wait 4 seconds and refresh list to capture the newly queued run
        setTimeout(() => {
          fetchRuns();
        }, 4000);
      } else {
        const errText = await response.text();
        throw new Error(`GitHub Response ${response.status}: ${errText}`);
      }
    } catch (err: any) {
      setDispatchStatus("error");
      setDispatchMessage(err.message || "Failed to trigger GHA dispatch.");
    }
  };

  // Download & Extract Artifact ZIP in Browser
  const extractArtifactReport = async (runId: number, artifactsUrl: string) => {
    if (!githubPat) {
      setExtractionError("Downloading artifacts requires authentication. Please configure your transient PAT.");
      return;
    }

    setExtractingRunId(runId);
    setExtractionError("");
    setExtractedReport(null);
    setExtractedImages([]);
    setLargeArtifactUrl(null);

    try {
      // 1. Fetch artifacts listing for this run
      const artifactsResponse = await fetch(artifactsUrl, {
        headers: { Authorization: `token ${githubPat}` }
      });
      if (!artifactsResponse.ok) throw new Error("Failed to fetch run artifacts metadata.");
      
      const artifactsData = await artifactsResponse.json();
      const list: Artifact[] = artifactsData.artifacts || [];

      // Find execution-report or failure-screenshots
      const reportArtifact = list.find(art => art.name === "execution-report");
      
      if (!reportArtifact) {
        throw new Error("No 'execution-report' artifact found for this run (run may still be in progress).");
      }

      // Check Artifact Extraction Size Limits (Limit: 20MB)
      const sizeInMB = reportArtifact.size_in_bytes / (1024 * 1024);
      if (sizeInMB > 20) {
        const downloadUrl = `https://api.github.com/repos/${getFullRepoPath()}/actions/artifacts/${reportArtifact.id}/zip`;
        setLargeArtifactUrl({ url: downloadUrl, name: reportArtifact.name });
        throw new Error(`Artifact size (${sizeInMB.toFixed(2)} MB) exceeds browser unzipping limit of 20MB. Download options enabled below.`);
      }

      // 2. Download Zip archive blob from GitHub API
      const downloadUrl = `https://api.github.com/repos/${getFullRepoPath()}/actions/artifacts/${reportArtifact.id}/zip`;
      const zipResponse = await fetch(downloadUrl, {
        headers: { Authorization: `token ${githubPat}` }
      });

      if (!zipResponse.ok) {
        throw new Error(`Direct download blocked. CORS configuration or token authorization error (HTTP ${zipResponse.status}).`);
      }

      const zipBlob = await zipResponse.blob();

      // 3. Extract using JSZip
      const zip = await JSZip.loadAsync(zipBlob);
      
      // Look for report.html or execution_summary.md
      const reportFile = zip.file("report.html");
      const summaryFile = zip.file("execution_summary.md");

      if (reportFile) {
        const htmlText = await reportFile.async("string");
        setExtractedReport(htmlText);
      } else if (summaryFile) {
        const mdText = await summaryFile.async("string");
        setExtractedReport(`<pre style="font-family: monospace; color:#fff; white-space: pre-wrap;">${mdText}</pre>`);
      } else {
        throw new Error("HTML report and markdown summary files are missing in the artifact ZIP.");
      }

    } catch (err: any) {
      setExtractionError(err.message || "Failed to download and unzip run artifacts.");
    } finally {
      setExtractingRunId(null);
    }
  };

  // Load failure screenshots if any
  const extractFailureScreenshots = async (runId: number, artifactsUrl: string) => {
    if (!githubPat) {
      setExtractionError("Transient PAT required to extract screenshots.");
      return;
    }
    setExtractingRunId(runId);
    setExtractionError("");
    setExtractedImages([]);
    setLargeArtifactUrl(null);

    try {
      const listResponse = await fetch(artifactsUrl, {
        headers: { Authorization: `token ${githubPat}` }
      });
      const data = await listResponse.json();
      const list: Artifact[] = data.artifacts || [];

      const screenshotArtifact = list.find(art => art.name === "failure-screenshots");
      if (!screenshotArtifact) {
        throw new Error("No failure screenshots uploaded for this run (test run passed or screenshots omitted).");
      }

      const sizeInMB = screenshotArtifact.size_in_bytes / (1024 * 1024);
      if (sizeInMB > 20) {
        const downloadUrl = `https://api.github.com/repos/${getFullRepoPath()}/actions/artifacts/${screenshotArtifact.id}/zip`;
        setLargeArtifactUrl({ url: downloadUrl, name: screenshotArtifact.name });
        throw new Error(`Screenshot archive size (${sizeInMB.toFixed(2)} MB) exceeds browser unzipping limit of 20MB. Download options enabled below.`);
      }

      // Download and parse
      const downloadUrl = `https://api.github.com/repos/${getFullRepoPath()}/actions/artifacts/${screenshotArtifact.id}/zip`;
      const response = await fetch(downloadUrl, {
        headers: { Authorization: `token ${githubPat}` }
      });
      const zipBlob = await response.blob();
      const zip = await JSZip.loadAsync(zipBlob);
      
      const imageUrls: string[] = [];
      const imageFiles = Object.keys(zip.files).filter(name => name.endsWith(".png"));

      for (const name of imageFiles) {
        const imgBlob = await zip.files[name].async("blob");
        imageUrls.push(URL.createObjectURL(imgBlob));
      }

      if (imageUrls.length === 0) {
        throw new Error("No screenshot PNG images found inside archive.");
      }
      setExtractedImages(imageUrls);

    } catch (err: any) {
      setExtractionError(err.message || "Failed to parse screenshots.");
    } finally {
      setExtractingRunId(null);
    }
  };

  // Fetch documentation from GitHub contents API
  const fetchDoc = async (path: string) => {
    setLoadingDoc(true);
    setDocContent("");
    try {
      const response = await fetch(
        `https://api.github.com/repos/${getFullRepoPath()}/contents/${path}`,
        {
          headers: githubPat ? { Authorization: `token ${githubPat}` } : {}
        }
      );
      if (!response.ok) throw new Error("Document missing in target remote repository.");
      const data = await response.json();
      
      // Decode Base64 content
      const decoded = atob(data.content.replace(/\s/g, ""));
      setDocContent(decoded);
    } catch (err: any) {
      setDocContent(`Error loading documentation: ${err.message}`);
    } finally {
      setLoadingDoc(false);
    }
  };

  useEffect(() => {
    if (activeTab === "docs") {
      fetchDoc(selectedDocPath);
    }
  }, [activeTab, selectedDocPath, repoOwner, repoName]);

  // Simple Markdown to HTML formatting helper
  const parseMarkdown = (md: string) => {
    if (!md) return "";
    return md
      .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-semibold my-4 border-b border-gray-800 pb-2 text-purple-400">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-semibold my-3 text-blue-400">$1</h2>')
      .replace(/^### (.*$)/gim, '<h3 class="text-xl font-medium my-2 text-emerald-400">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-900 text-pink-400 px-2 py-0.5 rounded font-mono text-sm">$1</code>')
      .replace(/^\s*\-\s+(.*$)/gim, '<li class="ml-6 list-disc text-gray-300">$1</li>')
      .replace(/\n$/gim, "<br />");
  };

  return (
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "20px" }}>
      
      {/* Top Navbar */}
      <header className="glass-panel" style={{ padding: "16px 24px", marginBottom: "24px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Activity style={{ color: "hsl(var(--primary))", width: "28px", height: "28px" }} />
          <div>
            <h1 style={{ fontSize: "1.25rem", fontWeight: 600, letterSpacing: "-0.5px" }}>Antigravity QA</h1>
            <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))" }}>Platform Orchestrator Dashboard</p>
          </div>
        </div>

        <nav style={{ display: "flex", gap: "6px" }}>
          {[
            { id: "dashboard", label: "Overview", icon: Layers },
            { id: "execution", label: "Run Tests", icon: Play },
            { id: "reports", label: "HTML Reports", icon: FileText },
            { id: "screenshots", label: "Failure Grabs", icon: Image },
            { id: "docs", label: "Documentation", icon: BookOpen },
          ].map(tab => {
            const Icon = tab.icon;
            const isSelected = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className="btn-secondary"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "8px 14px",
                  fontSize: "0.875rem",
                  backgroundColor: isSelected ? "hsl(var(--primary))" : "rgba(255,255,255,0.03)",
                  color: isSelected ? "white" : "hsl(var(--foreground))",
                  borderColor: isSelected ? "hsl(var(--primary))" : "rgba(255,255,255,0.05)"
                }}
              >
                <Icon style={{ width: "16px", height: "16px" }} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        <div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.875rem", padding: "8px 12px" }}
          >
            <Settings style={{ width: "16px", height: "16px" }} />
            <span>Settings</span>
          </button>
        </div>
      </header>

      {/* Settings Modal (Transient credentials) */}
      {showSettings && (
        <section className="glass-panel" style={{ padding: "20px", marginBottom: "24px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, marginBottom: "6px" }}>GitHub Repository Path</label>
            <div style={{ display: "flex", gap: "8px" }}>
              <input
                type="text"
                placeholder="owner/repo"
                value={`${repoOwner}/${repoName}`}
                onChange={(e) => {
                  const split = e.target.value.split("/");
                  if (split[0]) setRepoOwner(split[0]);
                  if (split[1]) setRepoName(split[1]);
                }}
                style={{ flex: 1 }}
              />
            </div>
            <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))", marginTop: "4px" }}>
              Target: github.com/{repoOwner}/{repoName}
            </p>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, marginBottom: "6px", color: "hsl(var(--warning))" }}>
              Transient Personal Access Token (PAT)
            </label>
            <input
              type="password"
              placeholder="ghp_..."
              value={githubPat}
              onChange={(e) => setGithubPat(e.target.value)}
              style={{ width: "100%" }}
            />
            <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))", marginTop: "4px" }}>
              Stored in React memory (transient state) — never saved to localStorage to prevent XSS exposure.
            </p>
          </div>
        </section>
      )}

      {/* Tab Vews */}
      <main style={{ minHeight: "60vh" }}>
        
        {/* OVERVIEW / HOME VIEW */}
        {activeTab === "dashboard" && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
            
            {/* Framework Stats */}
            <div className="glass-panel" style={{ padding: "24px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Database style={{ color: "hsl(var(--primary))", width: "18px", height: "18px" }} />
                  <span>Framework Metrics</span>
                </h3>
                
                {cache ? (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", margin: "16px 0" }}>
                    <div style={{ background: "rgba(255,255,255,0.02)", padding: "12px", borderRadius: "8px" }}>
                      <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))" }}>Last Status</p>
                      <h4 style={{ fontSize: "1.5rem", fontWeight: 600, color: cache.latestStatus === "completed" ? "hsl(var(--success))" : "hsl(var(--warning))" }}>
                        {cache.latestStatus}
                      </h4>
                    </div>
                    <div style={{ background: "rgba(255,255,255,0.02)", padding: "12px", borderRadius: "8px" }}>
                      <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))" }}>Outcome</p>
                      <h4 style={{ fontSize: "1.5rem", fontWeight: 600, color: cache.latestSummary === "success" ? "hsl(var(--success))" : "hsl(var(--error))" }}>
                        {cache.latestSummary}
                      </h4>
                    </div>
                    <div style={{ gridColumn: "span 2", fontSize: "0.8125rem", color: "hsl(var(--muted))" }}>
                      {cache.reportMetadata}
                    </div>
                  </div>
                ) : (
                  <p style={{ color: "hsl(var(--muted))", fontSize: "0.875rem", margin: "16px 0" }}>No cached metrics found. Run a test suite to initialize cache.</p>
                )}
              </div>
              
              <div style={{ borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "12px", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "hsl(var(--muted))" }}>
                <span>LocalStorage Caching</span>
                <span>{cache ? `Updated: ${cache.lastUpdated}` : "Inactive"}</span>
              </div>
            </div>

            {/* Test Run Connection Card */}
            <div className="glass-panel" style={{ padding: "24px" }}>
              <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                <ShieldCheck style={{ color: "hsl(var(--success))", width: "18px", height: "18px" }} />
                <span>Security & API Integrity</span>
              </h3>
              <p style={{ fontSize: "0.875rem", color: "hsl(var(--muted))", marginBottom: "16px" }}>
                This dashboard uses token-free endpoints to retrieve public run logs and histories. Personal Access Tokens are processed only in transient memory during your browser session for dispatch operations.
              </p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 12px", background: "rgba(255,255,255,0.02)", borderRadius: "6px", fontSize: "0.875rem" }}>
                  <span style={{ color: "hsl(var(--muted))" }}>Public Runs Fetch</span>
                  <span style={{ color: "hsl(var(--success))", fontWeight: 500 }}>Operational</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 12px", background: "rgba(255,255,255,0.02)", borderRadius: "6px", fontSize: "0.875rem" }}>
                  <span style={{ color: "hsl(var(--muted))" }}>PAT Status</span>
                  <span>{githubPat ? <span style={{ color: "hsl(var(--success))" }}>Active (Transient)</span> : <span style={{ color: "hsl(var(--warning))" }}>Missing (Triggering Disabled)</span>}</span>
                </div>
              </div>
            </div>

            {/* Technology Stack Grid */}
            <div className="glass-panel" style={{ padding: "24px", gridColumn: "span 2" }}>
              <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <Cpu style={{ color: "hsl(var(--primary))", width: "18px", height: "18px" }} />
                <span>Technology Integrations</span>
              </h3>
              
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px" }}>
                {[
                  { name: "Selenium WebDriver", category: "Core Automation", spec: "Python API" },
                  { name: "Pytest", category: "Test Runner", spec: "v9.1.1 Engine" },
                  { name: "Docker Compose", category: "Containerization", spec: "Headless Sandbox" },
                  { name: "React + Vite", category: "Web Dashboard", spec: "TypeScript Serverless" },
                  { name: "GitHub Actions", category: "CI/CD Pipeline", spec: "API Dispatcher" },
                  { name: "Vercel", category: "Frontend Host", spec: "Static CDN" }
                ].map((stack, idx) => (
                  <div key={idx} style={{ border: "1px solid rgba(255,255,255,0.04)", padding: "12px", borderRadius: "8px", background: "rgba(255,255,255,0.01)" }}>
                    <h4 style={{ fontSize: "0.875rem", fontWeight: 600 }}>{stack.name}</h4>
                    <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))", marginTop: "2px" }}>{stack.category}</p>
                    <span style={{ display: "inline-block", fontSize: "0.6875rem", background: "rgba(139,92,246,0.1)", color: "hsl(var(--primary))", padding: "2px 6px", borderRadius: "4px", marginTop: "6px" }}>{stack.spec}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* TEST RUN TRIGGER VIEW */}
        {activeTab === "execution" && (
          <div style={{ maxWidth: "720px", margin: "0 auto" }} className="glass-panel">
            <div style={{ borderBottom: "1px solid rgba(255,255,255,0.05)", padding: "20px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ fontSize: "1.125rem", fontWeight: 600 }}>Launch Headless Regression Suite</h3>
                <p style={{ fontSize: "0.8125rem", color: "hsl(var(--muted))" }}>Dispatch GitHub Actions automated tests on the cloud</p>
              </div>
              <Play style={{ color: "hsl(var(--primary))" }} />
            </div>

            <form onSubmit={triggerWorkflow} style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, marginBottom: "6px" }}>Target Environment</label>
                  <select value={envChoice} onChange={(e) => setEnvChoice(e.target.value)} style={{ width: "100%" }}>
                    <option value="qa">QA Environment (demowebshop)</option>
                    <option value="development">Development Sandbox</option>
                    <option value="production">Production Storefront</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, marginBottom: "6px" }}>WebDriver Browser</label>
                  <select value={browserChoice} onChange={(e) => setBrowserChoice(e.target.value)} style={{ width: "100%" }}>
                    <option value="chrome">Chrome (Pre-installed Stable)</option>
                    <option value="firefox">Firefox (GeckoDriver)</option>
                  </select>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, marginBottom: "6px" }}>Headless Execution</label>
                  <select value={headlessChoice} onChange={(e) => setHeadlessChoice(e.target.value)} style={{ width: "100%" }}>
                    <option value="true">True (Enabled inside CI/CD)</option>
                    <option value="false">False (Requires local GUI display)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, marginBottom: "6px" }}>Pytest Rerun Retries</label>
                  <input
                    type="number"
                    min="0"
                    max="5"
                    value={retryChoice}
                    onChange={(e) => setRetryChoice(e.target.value)}
                    style={{ width: "100%" }}
                  />
                </div>
              </div>

              {!githubPat && (
                <div style={{ background: "rgba(245,158,11,0.06)", border: "1px solid rgba(245,158,11,0.2)", padding: "12px", borderRadius: "8px", display: "flex", gap: "10px", alignItems: "flex-start" }}>
                  <AlertCircle style={{ color: "hsl(var(--warning))", width: "20px", height: "20px", flexShrink: 0 }} />
                  <p style={{ fontSize: "0.8125rem", color: "hsl(var(--muted))" }}>
                    <strong>Token Required</strong>: To trigger dispatch events, you must configure a transient GitHub Personal Access Token in <strong>Settings</strong> at the top bar.
                  </p>
                </div>
              )}

              {dispatchStatus !== "idle" && (
                <div style={{ 
                  background: dispatchStatus === "success" ? "rgba(16,185,129,0.06)" : dispatchStatus === "sending" ? "rgba(139,92,246,0.06)" : "rgba(239,68,68,0.06)",
                  border: dispatchStatus === "success" ? "1px solid rgba(16,185,129,0.2)" : dispatchStatus === "sending" ? "1px solid rgba(139,92,246,0.2)" : "1px solid rgba(239,68,68,0.2)",
                  padding: "12px", 
                  borderRadius: "8px", 
                  display: "flex", 
                  gap: "10px", 
                  alignItems: "center" 
                }}>
                  {dispatchStatus === "sending" ? <Loader className="animate-spin" style={{ width: "18px", height: "18px", color: "hsl(var(--primary))" }} /> :
                   dispatchStatus === "success" ? <CheckCircle style={{ width: "18px", height: "18px", color: "hsl(var(--success))" }} /> :
                   <AlertCircle style={{ width: "18px", height: "18px", color: "hsl(var(--error))" }} />}
                  <span style={{ fontSize: "0.875rem" }}>{dispatchMessage}</span>
                </div>
              )}

              <button
                type="submit"
                className="btn-primary"
                disabled={!githubPat || dispatchStatus === "sending"}
                style={{ padding: "12px", display: "flex", justifyContent: "center", alignItems: "center", gap: "8px", width: "100%", fontSize: "0.9375rem" }}
              >
                <Play style={{ width: "16px", height: "16px" }} />
                <span>Trigger Dispatch Run</span>
              </button>
            </form>
          </div>
        )}

        {/* REPORTS & ARTIFACTS LIST VIEW */}
        {activeTab === "reports" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "20px" }}>
            
            {/* Run List */}
            <div className="glass-panel" style={{ padding: "20px", maxHeight: "80vh", overflowY: "auto" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>Workflow Runs</h3>
                <button onClick={fetchRuns} className="btn-secondary" style={{ padding: "6px 10px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "4px" }}>
                  <RefreshCw style={{ width: "12px", height: "12px" }} />
                  <span>Refresh</span>
                </button>
              </div>

              {loadingRuns ? (
                <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}><Loader className="animate-spin" /></div>
              ) : apiError ? (
                <p style={{ color: "hsl(var(--error))", fontSize: "0.875rem" }}>{apiError}</p>
              ) : workflowRuns.length === 0 ? (
                <p style={{ color: "hsl(var(--muted))", fontSize: "0.875rem" }}>No execution history found.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {workflowRuns.map(run => (
                    <div 
                      key={run.id}
                      onClick={() => extractArtifactReport(run.id, run.artifacts_url)}
                      style={{ 
                        padding: "10px 12px", 
                        background: "rgba(255,255,255,0.01)", 
                        border: "1px solid rgba(255,255,255,0.05)", 
                        borderRadius: "8px", 
                        cursor: "pointer",
                        transition: "all 0.2s"
                      }}
                      className="hover:border-purple-500 hover:bg-gray-900"
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem" }}>
                        <span style={{ fontWeight: 600 }}>Run #{run.run_number}</span>
                        <span style={{ 
                          color: run.status === "completed" ? (run.conclusion === "success" ? "hsl(var(--success))" : "hsl(var(--error))") : "hsl(var(--warning))" 
                        }}>
                          {run.conclusion || run.status}
                        </span>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.6875rem", color: "hsl(var(--muted))", marginTop: "4px" }}>
                        <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                          <Clock style={{ width: "10px", height: "10px" }} />
                          {new Date(run.created_at).toLocaleDateString()}
                        </span>
                        <span>{run.trigger_user}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Artifact Content Viewer */}
            <div className="glass-panel" style={{ padding: "20px", display: "flex", flexDirection: "column", minHeight: "60vh" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, borderBottom: "1px solid rgba(255,255,255,0.05)", paddingBottom: "12px", marginBottom: "16px" }}>
                Artifact Report Reader
              </h3>

              {!githubPat && (
                <div style={{ background: "rgba(245,158,11,0.05)", padding: "12px", borderRadius: "8px", marginBottom: "16px", display: "flex", gap: "8px", fontSize: "0.8125rem", color: "hsl(var(--muted))" }}>
                  <AlertCircle style={{ color: "hsl(var(--warning))", width: "18px", height: "18px", flexShrink: 0 }} />
                  <span>
                    <strong>Credentials Missing</strong>: Downloading and unzipping action report artifacts requires configuration of your Personal Access Token in the top <strong>Settings</strong> panel.
                  </span>
                </div>
              )}

              {extractingRunId && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, gap: "10px" }}>
                  <Loader className="animate-spin" style={{ color: "hsl(var(--primary))", width: "32px", height: "32px" }} />
                  <p style={{ fontSize: "0.875rem", color: "hsl(var(--muted))" }}>Fetching ZIP artifact archive & parsing HTML logs...</p>
                </div>
              )}

              {extractionError && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, gap: "12px", color: "hsl(var(--error))" }}>
                  <AlertCircle style={{ width: "32px", height: "32px" }} />
                  <p style={{ fontSize: "0.875rem", textAlign: "center", maxWidth: "400px" }}>{extractionError}</p>
                  
                  {largeArtifactUrl && (
                    <div style={{ marginTop: "12px", padding: "16px", background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "8px", display: "flex", flexDirection: "column", gap: "8px", alignItems: "center" }}>
                      <p style={{ fontSize: "0.8125rem", color: "hsl(var(--muted))", textAlign: "center" }}>
                        Download the ZIP manually using your transient Personal Access Token.
                      </p>
                      <button
                        onClick={async () => {
                          try {
                            const response = await fetch(largeArtifactUrl.url, {
                              headers: { Authorization: `token ${githubPat}` }
                            });
                            if (!response.ok) throw new Error(`HTTP ${response.status}`);
                            const blob = await response.blob();
                            const blobUrl = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = blobUrl;
                            a.download = `${largeArtifactUrl.name}.zip`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(blobUrl);
                          } catch (e: any) {
                            alert(`Failed to download artifact: ${e.message}`);
                          }
                        }}
                        className="btn-primary"
                        style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 14px", fontSize: "0.8125rem" }}
                      >
                        <Download style={{ width: "14px", height: "14px" }} />
                        <span>Download ZIP Archive ({largeArtifactUrl.name})</span>
                      </button>
                    </div>
                  )}
                </div>
              )}

              {extractedReport && !extractingRunId && (
                <div 
                  style={{ 
                    flex: 1, 
                    background: "rgba(10,12,20,0.5)", 
                    borderRadius: "8px", 
                    padding: "16px", 
                    overflowY: "auto", 
                    maxHeight: "65vh" 
                  }}
                  dangerouslySetInnerHTML={{ __html: extractedReport }}
                />
              )}

              {!extractedReport && !extractingRunId && !extractionError && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, color: "hsl(var(--muted))" }}>
                  <FileText style={{ width: "40px", height: "40px", marginBottom: "10px" }} />
                  <p style={{ fontSize: "0.875rem" }}>Select a run from the history tree to view the generated Pytest HTML report details.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* SCREENSHOT FAILURE VIEW */}
        {activeTab === "screenshots" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "20px" }}>
            
            {/* Run List for Screenshots */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "12px" }}>Failure Run Logs</h3>
              <p style={{ fontSize: "0.75rem", color: "hsl(var(--muted))", marginBottom: "16px" }}>Select a run to extract failure screenshot images.</p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {workflowRuns.map(run => (
                  <div 
                    key={run.id}
                    onClick={() => extractFailureScreenshots(run.id, run.artifacts_url)}
                    style={{ 
                      padding: "10px 12px", 
                      background: "rgba(255,255,255,0.01)", 
                      border: "1px solid rgba(255,255,255,0.05)", 
                      borderRadius: "8px", 
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <div>
                      <span style={{ display: "block", fontSize: "0.8125rem", fontWeight: 600 }}>Run #{run.run_number}</span>
                      <span style={{ fontSize: "0.6875rem", color: "hsl(var(--muted))" }}>{new Date(run.created_at).toLocaleDateString()}</span>
                    </div>
                    <span style={{ 
                      fontSize: "0.75rem", 
                      color: run.status === "completed" ? (run.conclusion === "success" ? "hsl(var(--success))" : "hsl(var(--error))") : "hsl(var(--warning))" 
                    }}>
                      {run.conclusion || run.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Screenshots Display View */}
            <div className="glass-panel" style={{ padding: "20px", display: "flex", flexDirection: "column", minHeight: "60vh" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, borderBottom: "1px solid rgba(255,255,255,0.05)", paddingBottom: "12px", marginBottom: "16px" }}>
                Failure Screenshots Gallery
              </h3>

              {extractingRunId && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, gap: "10px" }}>
                  <Loader className="animate-spin" style={{ color: "hsl(var(--primary))", width: "32px", height: "32px" }} />
                  <p style={{ fontSize: "0.875rem", color: "hsl(var(--muted))" }}>Downloading screenshots package...</p>
                </div>
              )}

              {extractionError && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, gap: "12px", color: "hsl(var(--error))" }}>
                  <AlertCircle style={{ width: "32px", height: "32px" }} />
                  <p style={{ fontSize: "0.875rem", textAlign: "center", maxWidth: "400px" }}>{extractionError}</p>
                  
                  {largeArtifactUrl && (
                    <div style={{ marginTop: "12px", padding: "16px", background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "8px", display: "flex", flexDirection: "column", gap: "8px", alignItems: "center" }}>
                      <p style={{ fontSize: "0.8125rem", color: "hsl(var(--muted))", textAlign: "center" }}>
                        Download the ZIP manually using your transient Personal Access Token.
                      </p>
                      <button
                        onClick={async () => {
                          try {
                            const response = await fetch(largeArtifactUrl.url, {
                              headers: { Authorization: `token ${githubPat}` }
                            });
                            if (!response.ok) throw new Error(`HTTP ${response.status}`);
                            const blob = await response.blob();
                            const blobUrl = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = blobUrl;
                            a.download = `${largeArtifactUrl.name}.zip`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(blobUrl);
                          } catch (e: any) {
                            alert(`Failed to download artifact: ${e.message}`);
                          }
                        }}
                        className="btn-primary"
                        style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 14px", fontSize: "0.8125rem" }}
                      >
                        <Download style={{ width: "14px", height: "14px" }} />
                        <span>Download ZIP Archive ({largeArtifactUrl.name})</span>
                      </button>
                    </div>
                  )}
                </div>
              )}

              {extractedImages.length > 0 && !extractingRunId && (
                <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "20px", overflowY: "auto", maxHeight: "65vh" }}>
                  {extractedImages.map((src, idx) => (
                    <div key={idx} style={{ border: "2px solid rgba(239, 68, 68, 0.2)", borderRadius: "8px", overflow: "hidden", background: "rgba(0,0,0,0.3)" }}>
                      <div style={{ padding: "8px 12px", background: "rgba(239, 68, 68, 0.08)", fontSize: "0.75rem", fontWeight: 500, color: "hsl(var(--error))", borderBottom: "1px solid rgba(239, 68, 68, 0.15)" }}>
                        Failure State Capture #{idx + 1}
                      </div>
                      <img src={src} alt={`Failure Capture ${idx + 1}`} style={{ width: "100%", height: "auto", display: "block" }} />
                    </div>
                  ))}
                </div>
              )}

              {extractedImages.length === 0 && !extractingRunId && !extractionError && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flex: 1, color: "hsl(var(--muted))" }}>
                  <Image style={{ width: "40px", height: "40px", marginBottom: "10px" }} />
                  <p style={{ fontSize: "0.875rem" }}>Select a failing run from the list to unzip and display visual failure states.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* DOCUMENTATION VIEWER VIEW */}
        {activeTab === "docs" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 3fr", gap: "20px" }}>
            
            {/* Guide List */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "12px" }}>Framework Manuals</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {[
                  { path: "docs/LEARNING_GUIDE.md", label: "Learning Guide" },
                  { path: "docs/Architecture.md", label: "Architecture System" },
                  { path: "docs/ExecutionFlow.md", label: "Execution Lifecycles" },
                  { path: "docs/TestingStrategy.md", label: "Testing Strategy" },
                  { path: "docs/ErrorHandling.md", label: "Error Diagnostics" },
                  { path: "docs/DeploymentGuide.md", label: "Deployment Manual" },
                  { path: "docs/ArchitectureDecisionRecord.md", label: "Architecture Decisions (ADR)" },
                  { path: "docs/SecurityConsiderations.md", label: "Security & Sandbox limits" },
                  { path: "docs/FRONTEND_GUIDE.md", label: "Frontend Dashboard Guide" },
                  { path: "docs/InterviewQuestions.md", label: "Interview Card Prep" },
                ].map(doc => (
                  <button
                    key={doc.path}
                    onClick={() => setSelectedDocPath(doc.path)}
                    className="btn-secondary"
                    style={{
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 12px",
                      fontSize: "0.8125rem",
                      backgroundColor: selectedDocPath === doc.path ? "hsl(var(--primary))" : "rgba(255,255,255,0.01)",
                      color: selectedDocPath === doc.path ? "white" : "hsl(var(--foreground))",
                      borderColor: selectedDocPath === doc.path ? "hsl(var(--primary))" : "rgba(255,255,255,0.05)"
                    }}
                  >
                    {doc.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Doc View Content */}
            <div className="glass-panel" style={{ padding: "24px 30px", maxHeight: "80vh", overflowY: "auto" }}>
              {loadingDoc ? (
                <div style={{ display: "flex", justifyContent: "center", padding: "80px" }}><Loader className="animate-spin" /></div>
              ) : (
                <article 
                  style={{ color: "hsl(var(--foreground))" }}
                  dangerouslySetInnerHTML={{ __html: parseMarkdown(docContent) }}
                />
              )}
            </div>
          </div>
        )}

      </main>

      <footer style={{ marginTop: "40px", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "16px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px", fontSize: "0.8125rem", color: "hsl(var(--muted))" }}>
        <span>Portfolio QA Automation Framework Dashboard</span>
        <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span>Free Open-Source MIT License</span>
        </span>
      </footer>

    </div>
  );
}
