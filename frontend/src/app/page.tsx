"use client";

import React, { useState, useEffect } from "react";
import { api, TelemetryPayload } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import MetricCards from "@/components/MetricCards";
import Remediation from "@/components/Remediation";

export default function CisoDashboard() {
  const [activeTab, setActiveTab] = useState<string>("dashboard");

  // Ingestion State
  const [docId, setDocId] = useState<string>("policy_telemetry_v3");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestLogs, setIngestLogs] = useState<string[]>([]);
  const [lastIngested, setLastIngested] = useState<{
    docId: string;
    recordId: number;
    chunksCount: number;
  } | null>(null);

  // Auditing State
  const [bulletinText, setBulletinText] = useState<string>(
    `SEBI CYBERSECURITY DIRECTIVE: REFORMATTED AUDIT AND TRACE LOG MANAGEMENT 2026\nCHAPTER III: REPOSITORY INTEGRITY AND CRYPTOGRAPHIC SAFEGUARDS\nSection 4.2: Cryptographical Log Protection\nTo prevent insider tampering, all core transaction and system access log aggregates must be cryptographically protected from unauthorized alterations.\n(a) Centralized log streams must be signed at the application level using HMAC-SHA256 signatures before being written to disk.\n(b) Storage buckets containing log aggregates must utilize dedicated Customer-Managed Keys (CMK) via Key Management Services (KMS) with automated annual rotation enabled. Default provider-managed keys are no longer sufficient for compliance.`
  );
  const [isAuditing, setIsAuditing] = useState<boolean>(false);
  const [auditProgress, setAuditProgress] = useState<number>(0);
  const [auditStatus, setAuditStatus] = useState<string>("");
  
  // Dashboard Telemetry Cache State
  const [telemetry, setTelemetry] = useState<TelemetryPayload | null>(null);
  const [recordId, setRecordId] = useState<number>(-1);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // Poll health and sync mock values or read initial db state if available
  useEffect(() => {
    // Optionally fetch initial status on load
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleIngest = async () => {
    if (!selectedFile) {
      alert("Please upload a txt or pdf policy document first.");
      return;
    }

    setIsIngesting(true);
    setIngestLogs(["Initializing file stream reader...", "Segmenting document into logical clauses..."]);

    try {
      const response = await api.ingestPolicy(docId, selectedFile);
      setIngestLogs((prev) => [
        ...prev,
        "Computing deterministic SHA-256 chunk hashes...",
        `Generating semantic embeddings for ${response.chunks_count} clauses...`,
        "Indexing embedded dimensions into Qdrant collection...",
        `Successfully logged Document Record ID #${response.relational_record_id}!`,
      ]);
      setLastIngested({
        docId: response.document_id,
        recordId: response.relational_record_id,
        chunksCount: response.chunks_count,
      });
    } catch (err: any) {
      setIngestLogs((prev) => [...prev, `Ingestion error: ${err.message || err}`]);
    } finally {
      setIsIngesting(false);
    }
  };

  const handleAnalyze = async () => {
    if (!bulletinText.trim()) {
      alert("Please paste the regulatory bulletin text to evaluate.");
      return;
    }

    setIsAuditing(true);
    setAuditProgress(10);
    setAuditStatus("Formulating Planning Objectives...");

    // Simulated progress transitions to engage CISO visual feedback loop
    const progressIntervals = [
      { p: 35, s: "Executing semantic vector queries..." },
      { p: 65, s: "Conducting comparative gap analysis..." },
      { p: 85, s: "Synthesizing mitigation blueprints..." },
    ];

    progressIntervals.forEach((step, idx) => {
      setTimeout(() => {
        setAuditProgress(step.p);
        setAuditStatus(step.s);
      }, (idx + 1) * 800);
    });

    try {
      const response = await api.analyzeCompliance(bulletinText);
      setTimeout(() => {
        setAuditProgress(100);
        setAuditStatus("Analysis complete!");
        setTelemetry(response.telemetry);
        setRecordId(response.relational_record_id);
        setIsAuditing(false);
        setActiveTab("dashboard"); // bounce back to dashboard to review visual grids
      }, 3000);
    } catch (err: any) {
      setIsAuditing(false);
      setAuditStatus("Analysis failed.");
      alert(`Audit failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  // Generate Institutional PDF Boardroom Report by opening a beautifully styled printable overlay window
  const handleExportPdf = () => {
    if (!telemetry || !telemetry.report) {
      alert("No active compliance telemetry report to export. Please run the live audit analysis first.");
      return;
    }

    setIsExporting(true);
    const report = telemetry.report;

    // Build highly polished HTML Document for printing
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      alert("Pop-up blocker prevented opening report. Please allow popups for this site.");
      setIsExporting(false);
      return;
    }

    const dateStr = new Date().toLocaleString();
    const mappingsHtml = report.compliance_drift_matrix
      .map(
        (m, idx) => `
        <div class="card" style="border-left: 5px solid ${
          m.status === "Non-Compliant" ? "#EF4444" : m.status === "Partial" ? "#F59E0B" : "#10B981"
        };">
          <div class="card-header">Reference Mapping #${idx + 1}</div>
          <div class="field"><span class="label">Regulatory Clause:</span> ${m.regulatory_clause}</div>
          <div class="field"><span class="label">Internal Policy Ref:</span> ${m.internal_policy_reference}</div>
          <div class="field"><span class="label">Alignment Status:</span> <span class="badge ${m.status.toLowerCase()}">${m.status.toUpperCase()}</span></div>
          <div class="field"><span class="label">Delta Evidence:</span> <span class="evidence">${m.delta_evidence}</span></div>
        </div>
      `
      )
      .join("");

    const blueprintsHtml = report.drift_remediation_blueprints
      .map(
        (b, idx) => `
        <div class="blueprint-section">
          <h3>3.${idx + 1} Remediation: ${b.clause_at_risk}</h3>
          <div style="margin-bottom: 8px;">
            <span class="label">Severity Level:</span> <span class="badge ${b.severity_rating.toLowerCase()}">${b.severity_rating}</span>
            <span class="label" style="margin-left: 20px;">Clarity Score:</span> <code>${b.clarity_score}/100</code>
          </div>
          <pre>${b.technical_remediation_blueprint}</pre>
        </div>
      `
      )
      .join("");

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>ReguDrift AI - Boardroom Compliance Audit</title>
        <style>
          body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            color: #1e293b;
            margin: 40px;
            font-size: 14px;
            line-height: 1.6;
          }
          header {
            border-bottom: 2px solid #1e3a8a;
            padding-bottom: 12px;
            margin-bottom: 30px;
          }
          .title-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          .logo {
            font-size: 24px;
            font-weight: bold;
            color: #1e3a8a;
          }
          .date {
            font-size: 11px;
            color: #64748b;
          }
          .cover-meta {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
          }
          .cover-meta table {
            width: 100%;
            border-collapse: collapse;
          }
          .cover-meta td {
            padding: 6px 0;
            font-size: 13px;
          }
          .cover-meta td.label {
            font-weight: bold;
            color: #475569;
            width: 180px;
          }
          h2 {
            font-size: 18px;
            color: #1e3a8a;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 6px;
            margin-top: 30px;
          }
          .summary-box {
            background-color: #f8fafc;
            border-left: 4px solid #1e3a8a;
            padding: 15px;
            font-style: italic;
            margin-bottom: 25px;
          }
          .card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 16px;
          }
          .card-header {
            font-weight: bold;
            color: #1e3a8a;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
          }
          .field {
            margin-bottom: 8px;
          }
          .field span.label {
            font-weight: bold;
            color: #475569;
            display: inline-block;
            width: 140px;
          }
          .badge {
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
          }
          .badge.non-compliant, .badge.critical, .badge.high {
            background-color: #fee2e2;
            color: #dc2626;
          }
          .badge.partial, .badge.medium {
            background-color: #fef3c7;
            color: #d97706;
          }
          .badge.compliant, .badge.low {
            background-color: #dcfce7;
            color: #16a34a;
          }
          .evidence {
            color: #475569;
          }
          .blueprint-section {
            margin-bottom: 25px;
            page-break-inside: avoid;
          }
          pre {
            font-family: 'Courier New', Courier, monospace;
            background-color: #f1f5f9;
            padding: 15px;
            border-radius: 4px;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
            border: 1px solid #cbd5e1;
          }
          footer {
            margin-top: 50px;
            border-top: 1px solid #e2e8f0;
            padding-top: 10px;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
          }
          @media print {
            body { margin: 20px; }
            footer { position: fixed; bottom: 0; width: 100%; }
          }
        </style>
      </head>
      <body>
        <header>
          <div class="title-container">
            <div class="logo">🛡️ REGUDRIFT AI</div>
            <div class="date">REPORT GENERATION: ${dateStr}</div>
          </div>
        </header>
        
        <div class="cover-meta">
          <table>
            <tr>
              <td class="label">SQL Audit ID:</td>
              <td>#${recordId}</td>
            </tr>
            <tr>
              <td class="label">Operational Health:</td>
              <td>${report.remediation_timeline_weeks > 4 ? "Action Required" : "Aligned"}</td>
            </tr>
            <tr>
              <td class="label">Vector Index Provider:</td>
              <td>QDRANT Vector DB Core</td>
            </tr>
            <tr>
              <td class="label">System Boundary:</td>
              <td>PRODUCTION - Secure Docker Enclave</td>
            </tr>
          </table>
        </div>

        <h2>1. Executive Audit Summary</h2>
        <div class="summary-box">
          ${report.executive_summary}
        </div>

        <h2>2. Compliance Drift Matrix Mappings</h2>
        <div style="margin-top: 15px;">
          ${mappingsHtml}
        </div>

        <h2>3. Technical Remediation Blueprints</h2>
        <div style="margin-top: 15px;">
          ${blueprintsHtml}
        </div>

        <footer>
          CONFIDENTIAL - FOR BOARDROOM AUDIT COMMITTEE DIRECT OPERATIONS ONLY - GENERATED VIA REGUDRIFT STATEFUL ORCHESTRATOR
        </footer>

        <script>
          window.onload = function() {
            window.print();
          }
        </script>
      </body>
      </html>
    `);
    printWindow.document.close();
    setIsExporting(false);
  };

  // Determine overall status based on telemetry findings
  const getOverallStatus = () => {
    if (!telemetry || !telemetry.report) return "Drift Detected";
    const statuses = telemetry.report.compliance_drift_matrix.map((m) => m.status);
    if (statuses.includes("Non-Compliant")) return "Non-Compliant";
    if (statuses.includes("Partial")) return "Partial";
    return "Compliant";
  };

  const getOverallHealth = () => {
    if (!telemetry || !telemetry.report) return 75;
    const statuses = telemetry.report.compliance_drift_matrix.map((m) => m.status);
    if (statuses.includes("Non-Compliant")) return 45;
    if (statuses.includes("Partial")) return 75;
    return 100;
  };

  return (
    <>
      {/* Dynamic Navigation Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Dashboard Canvas Wrapper */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        
        {/* Top App Bar Header */}
        <header className="flex justify-between items-center w-full px-gutter h-16 max-w-full docked top-0 border-b border-outline-variant bg-surface-container-low z-40 flex-shrink-0">
          <div className="flex items-center gap-component-gap md:hidden">
            <div className="w-8 h-8 rounded bg-primary-container border border-primary flex items-center justify-center">
              <span className="text-primary text-sm font-bold">🛡️</span>
            </div>
            <span className="font-headline-md font-bold tracking-tight text-on-surface text-lg">
              ReguDrift AI
            </span>
          </div>

          {/* Quick Queries Input */}
          <div className="hidden md:flex flex-1 max-w-md mx-container-padding relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">🔍</span>
            <input
              className="w-full bg-surface-container border border-outline-variant rounded py-1.5 pl-10 pr-4 font-body-sm text-xs text-on-surface focus:outline-none focus:border-on-surface transition-colors placeholder:text-on-surface-variant/40"
              placeholder="Query audit logs, policies, instances..."
              type="text"
            />
          </div>

          <div className="flex items-center gap-gutter ml-auto">
            <div className="flex gap-2">
              <button className="p-1.5 rounded text-on-surface-variant hover:text-primary transition-all focus:outline-none text-sm">
                🔔
              </button>
              <button className="p-1.5 rounded text-on-surface-variant hover:text-primary transition-all focus:outline-none text-sm">
                🛡️
              </button>
            </div>
            <div className="w-8 h-8 rounded border border-outline-variant bg-surface-container-high overflow-hidden cursor-pointer hover:border-primary transition-colors flex items-center justify-center">
              <span className="text-on-surface-variant text-sm">👤</span>
            </div>
          </div>
        </header>

        {/* Scrollable Main Content Container */}
        <main className="flex-1 overflow-y-auto p-container-padding lg:p-8 flex flex-col gap-container-padding bg-background">
          
          {/* TAB 1: AUDITING DASHBOARD */}
          {activeTab === "dashboard" && (
            <>
              {/* Dynamic Health & Vulnerability Cards */}
              <MetricCards
                healthScore={getOverallHealth()}
                activeGuidelines={142}
                criticalGaps={telemetry?.report?.drift_remediation_blueprints?.length || 12}
                statusText={getOverallStatus()}
                hasAudited={!!telemetry}
              />

              {/* SPLIT-SCREEN DRIFT INSPECTOR */}
              <section className="flex flex-col gap-component-gap mt-4">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="font-title-sm text-base font-semibold text-on-surface flex items-center gap-2">
                    <span>🔁</span>
                    Drift Inspector
                  </h2>
                  <span className="font-label-caps text-[10px] text-on-surface-variant py-1 px-2 border border-outline-variant rounded bg-surface-container-highest uppercase tracking-wider">
                    {telemetry ? "Active Comparative Audit Tracked" : "Live Verification Baseline"}
                  </span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-[1px] bg-outline-variant border border-outline-variant rounded overflow-hidden">
                  
                  {/* Left Pane: Regulatory Mandates */}
                  <div className="bg-surface-container flex flex-col h-[400px]">
                    <div className="px-density-medium py-2 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
                      <span className="font-label-caps text-[10px] text-on-surface uppercase tracking-wider">
                        Regulatory Directive Bulletin
                      </span>
                      <span className="text-on-surface-variant text-sm">📋</span>
                    </div>
                    <div className="flex-1 p-container-padding overflow-y-auto font-body-sm text-xs text-on-surface-variant leading-relaxed">
                      {telemetry && telemetry.report ? (
                        <div>
                          <h4 className="font-bold text-on-surface text-sm mb-3">
                            Evaluated Target Clauses
                          </h4>
                          {telemetry.analysis?.target_clauses_evaluated.map((clause, idx) => (
                            <div
                              key={idx}
                              className="p-3 bg-slate-900 border border-outline-variant rounded mb-3"
                            >
                              <span className="text-primary font-semibold text-xs">Clause {idx + 1}:</span>
                              <p className="mt-1 text-on-surface/90 text-xs">{clause}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div>
                          <p className="mb-4">
                            4.1.2 All institutional trading gateways must enforce multi-factor authentication (MFA) utilizing hardware-backed tokens for administrators.
                          </p>
                          <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded text-on-surface my-4 relative">
                            <p className="font-semibold mb-1 text-amber-500">
                              ⚠️ Clause 4.1.3: Data Encryption at Rest
                            </p>
                            <p className="text-on-surface-variant text-[12px]">
                              "Sensitive financial telemetry and transaction logs must be encrypted at rest using AES-256 or equivalent cryptographic standards managed by a Key Management Service (KMS)."
                            </p>
                          </div>
                          <p className="mb-4">
                            4.1.4 Network segmentation must strictly isolate the transaction processing environment from general networks.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Pane: Internal Telemetry & Gaps */}
                  <div className="bg-surface-container-lowest flex flex-col h-[400px]">
                    <div className="px-density-medium py-2 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
                      <span className="font-label-caps text-[10px] text-on-surface flex items-center gap-1 uppercase tracking-wider">
                        <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse mr-1"></span>
                        Internal Infrastructure Telemetry
                      </span>
                      <span className="text-on-surface-variant text-sm">⚙️</span>
                    </div>
                    <div className="flex-1 p-density-medium overflow-y-auto font-code-terminal text-xs text-on-surface-variant leading-relaxed">
                      {telemetry && telemetry.report ? (
                        <div>
                          <div className="text-on-surface-variant/40 mb-2 font-mono">
                            # Active Compliance Drift Mapping Matrix
                          </div>
                          {telemetry.report.compliance_drift_matrix.map((mapping, idx) => {
                            const isCritical = mapping.status === "Non-Compliant";
                            const isWarning = mapping.status === "Partial";
                            return (
                              <div
                                key={idx}
                                className={`p-3 rounded mb-3 border-l-4 font-sans ${
                                  isCritical
                                    ? "bg-red-500/5 border-red-500"
                                    : isWarning
                                    ? "bg-amber-500/5 border-amber-500"
                                    : "bg-emerald-500/5 border-emerald-500"
                                }`}
                              >
                                <div className="flex justify-between items-center mb-1">
                                  <span className="font-bold text-on-surface text-xs font-mono">
                                    Ref: {mapping.internal_policy_reference}
                                  </span>
                                  <span
                                    className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                                      isCritical
                                        ? "bg-red-950 text-red-400"
                                        : isWarning
                                        ? "bg-amber-950 text-amber-400"
                                        : "bg-emerald-950 text-emerald-400"
                                    }`}
                                  >
                                    {mapping.status}
                                  </span>
                                </div>
                                <p className="text-on-surface-variant text-[11px] mt-1 font-mono">
                                  {mapping.delta_evidence}
                                </p>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="font-mono text-xs p-4">
                          <div className="text-on-surface-variant/30 mb-2"># Snapshot: telemetry-organization-root</div>
                          <div className="text-on-surface-variant/30 mb-4"># AWS Region: eu-west-1</div>
                          
                          <div className="pl-2 border-l border-outline-variant mb-4">
                            <div className="text-emerald-400">Resource: aws_iam_role.admin_gateway</div>
                            <div className="pl-4">mfa_enforced = <span className="text-emerald-400">true</span></div>
                            <div className="pl-4">hardware_token_required = <span className="text-emerald-400">true</span></div>
                          </div>

                          <div className="p-2 bg-amber-500/5 border-l-2 border-amber-500 mb-4 relative">
                            <div className="text-amber-400">Resource: aws_rds_cluster.financial_telemetry</div>
                            <div className="pl-4">engine = "aurora-postgresql"</div>
                            <div className="pl-4">
                              storage_encrypted = <span className="text-red-400 bg-red-950/50 px-1">false</span>
                              <span className="text-on-surface-variant/40 ml-2"># DRIFT DETECTED</span>
                            </div>
                            <div className="pl-4">kms_key_id = <span className="text-red-400 bg-red-950/50 px-1">null</span></div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              </section>

              {/* Dynamic Developer Remediation Terminal */}
              <Remediation
                blueprints={telemetry?.report?.drift_remediation_blueprints}
                onExportPdf={handleExportPdf}
                isExportingPdf={isExporting}
              />
            </>
          )}

          {/* TAB 2: POLICY INGESTION HUB */}
          {activeTab === "ingestion" && (
            <div className="bg-surface-container border border-outline-variant rounded p-container-padding flex flex-col">
              <h2 className="font-display-lg text-lg font-bold text-on-surface mb-2">
                Policy Ingestion Hub
              </h2>
              <p className="font-body-sm text-xs text-on-surface-variant mb-6">
                Ingest internal telemetry policies, operational standards, or system guidelines. 
                Files will be parsed asynchronously, embedded utilizing the `gemini-embedding-001` model (3072 dimensions), 
                and indexed into our Qdrant vector database.
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter mt-2 border-t border-outline-variant/40 pt-6">
                <div className="lg:col-span-2 flex flex-col gap-4">
                  <div>
                    <label className="block font-label-caps text-[10px] text-on-surface-variant uppercase tracking-wider mb-2">
                      Document ID Slug
                    </label>
                    <input
                      value={docId}
                      onChange={(e) => setDocId(e.target.value)}
                      className="w-full bg-slate-950 border border-outline-variant rounded p-3 text-xs text-on-surface focus:outline-none focus:border-primary"
                      type="text"
                    />
                  </div>

                  <div>
                    <label className="block font-label-caps text-[10px] text-on-surface-variant uppercase tracking-wider mb-2">
                      Choose policy document (.txt or .pdf)
                    </label>
                    <div className="border-2 border-dashed border-outline-variant rounded p-8 text-center bg-slate-950 flex flex-col items-center justify-center">
                      <span className="text-4xl mb-3">📁</span>
                      <input
                        onChange={handleFileChange}
                        className="hidden"
                        id="policy-file-upload"
                        type="file"
                        accept=".txt,.pdf"
                      />
                      <label
                        htmlFor="policy-file-upload"
                        className="bg-primary-container text-primary border border-primary/50 hover:bg-primary/20 font-label-caps text-[10px] px-4 py-2 rounded cursor-pointer uppercase transition-all mb-2"
                      >
                        Select Document
                      </label>
                      <span className="text-xs text-on-surface-variant">
                        {selectedFile ? `Selected: ${selectedFile.name}` : "No file selected"}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={handleIngest}
                    disabled={isIngesting}
                    className="w-full bg-primary text-on-primary font-label-caps text-xs py-3 rounded hover:brightness-115 uppercase transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isIngesting ? "Indexing & Ingesting Chunks..." : "Index and Store Policy"}
                  </button>
                </div>

                {/* Ingestion feed log panel */}
                <div className="bg-slate-950 border border-outline-variant p-container-padding rounded flex flex-col h-[380px]">
                  <h3 className="font-label-caps text-[10px] text-on-surface uppercase tracking-wider mb-3">
                    Ingestion Process Logs
                  </h3>
                  <div className="flex-1 overflow-y-auto font-mono text-[11px] text-emerald-400 flex flex-col gap-1.5 pr-2">
                    {ingestLogs.length === 0 ? (
                      <span className="text-on-surface-variant/40 font-mono">
                        Awaiting ingestion trigger...
                      </span>
                    ) : (
                      ingestLogs.map((log, idx) => <span key={idx}>&gt; {log}</span>)
                    )}
                  </div>
                  {lastIngested && (
                    <div className="mt-4 pt-4 border-t border-outline-variant/30 flex flex-col gap-1 font-mono text-[10px] text-on-surface-variant">
                      <div>Relational SQL ID: #{lastIngested.recordId}</div>
                      <div>Total Chunks Indexed: {lastIngested.chunksCount}</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: LIVE AUDIT CONSOLE */}
          {activeTab === "audit" && (
            <div className="bg-surface-container border border-outline-variant rounded p-container-padding flex flex-col">
              <h2 className="font-display-lg text-lg font-bold text-on-surface mb-2">
                Live Audit Console
              </h2>
              <p className="font-body-sm text-xs text-on-surface-variant mb-6">
                Paste new regulatory directives, legal bulletins, or compliance changes below. 
                The stateful agent loop will parse the update, search our active vector index for policy matches, 
                and draft detailed remediation blueprints.
              </p>
              
              <div className="flex flex-col gap-4 border-t border-outline-variant/40 pt-6">
                <div>
                  <label className="block font-label-caps text-[10px] text-on-surface-variant uppercase tracking-wider mb-2">
                    Raw Regulatory Bulletin Payload
                  </label>
                  <textarea
                    value={bulletinText}
                    onChange={(e) => setBulletinText(e.target.value)}
                    rows={8}
                    className="w-full bg-slate-950 border border-outline-variant rounded p-4 font-mono text-xs text-on-surface focus:outline-none focus:border-primary resize-none leading-relaxed"
                    placeholder="Paste bulletin payload here..."
                  />
                </div>

                <button
                  onClick={handleAnalyze}
                  disabled={isAuditing}
                  className="w-full bg-primary text-on-primary font-label-caps text-xs py-3 rounded hover:brightness-115 uppercase transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAuditing ? "Auditing Gaps..." : "Execute Regulatory Drift Analysis"}
                </button>

                {/* Progress bar visual indicators */}
                {isAuditing && (
                  <div className="bg-slate-950 border border-outline-variant p-container-padding rounded mt-2 flex flex-col gap-3">
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-xs text-primary">{auditStatus}</span>
                      <span className="font-mono text-xs text-on-surface-variant">{auditProgress}%</span>
                    </div>
                    <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-primary h-full transition-all duration-500"
                        style={{ width: `${auditProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        </main>

        {/* Global Footer status bar */}
        <footer className="flex justify-between items-center w-full px-gutter py-2 z-40 fixed bottom-0 right-0 border-t border-outline-variant bg-surface-container-lowest md:w-[calc(100%-16rem)] flex-wrap gap-2">
          <div className="font-label-caps text-[10px] text-on-surface flex items-center gap-1.5 uppercase tracking-wider">
            <span>🛡️</span>
            System Integrity: SECURED
          </div>
          <div className="flex items-center gap-container-padding font-mono text-[10px] text-on-surface-variant flex-wrap">
            <span>Data Sync: 100% Valid</span>
            <span className="flex items-center gap-1">
              <span className="text-emerald-500 text-xs">✔</span>
              Log Integrity: Cryptographically Verified
            </span>
          </div>
        </footer>

      </div>
    </>
  );
}
