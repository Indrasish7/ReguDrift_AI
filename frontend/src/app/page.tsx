"use client";

import React, { useState, useEffect } from "react";
import { api, TelemetryPayload, AnalyticsHistoryPoint } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import MetricCards from "@/components/MetricCards";
import Remediation from "@/components/Remediation";

interface MockCommit {
  hash: string;
  author: string;
  branch: string;
  timestamp: string;
  status: "Compliant" | "Partial" | "Non-Compliant";
  health: number;
}

export default function CisoDashboard() {
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [role, setRole] = useState<string>("SecOps_Admin");

  const [docId, setDocId] = useState<string>("policy_telemetry_v3");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestLogs, setIngestLogs] = useState<string[]>([]);
  const [lastIngested, setLastIngested] = useState<{
    docId: string;
    recordId: number;
    chunksCount: number;
  } | null>(null);

  const [bulletinText, setBulletinText] = useState<string>(
    `SEBI CYBERSECURITY DIRECTIVE: REFORMATTED AUDIT AND TRACE LOG MANAGEMENT 2026\nCHAPTER III: REPOSITORY INTEGRITY AND CRYPTOGRAPHIC SAFEGUARDS\nSection 4.2: Cryptographical Log Protection\nTo prevent insider tampering, all core transaction and system access log aggregates must be cryptographically protected from unauthorized alterations.\n(a) Centralized log streams must be signed at the application level using HMAC-SHA256 signatures before being written to disk.\n(b) Storage buckets containing log aggregates must utilize dedicated Customer-Managed Keys (CMK) via Key Management Services (KMS) with automated annual rotation enabled. Default provider-managed keys are no longer sufficient for compliance.`
  );
  
  const initialCommits: MockCommit[] = [
    { hash: "a1b2c3d4e5f67890", author: "Dev DevOps", branch: "release/v1.1", timestamp: "2026-07-17T12:00:00Z", status: "Non-Compliant", health: 45 },
    { hash: "f8b9c0d1e2f3a4b5", author: "Alice Auditor", branch: "main", timestamp: "2026-07-16T15:30:00Z", status: "Compliant", health: 100 },
    { hash: "e4f5a6b7c8d9e0f1", author: "Bob Builder", branch: "feature/logging", timestamp: "2026-07-15T09:15:00Z", status: "Partial", health: 75 },
    { hash: "cd78ef90ab12cd34", author: "Charlie Coder", branch: "patch/rotation", timestamp: "2026-07-14T17:45:00Z", status: "Non-Compliant", health: 60 }
  ];

  const initialTelemetry: Record<string, TelemetryPayload> = {
    "a1b2c3d4e5f67890": {
      state: "FinalReport",
      plan: null,
      context: null,
      analysis: null,
      report: {
        executive_summary: "Critical compliance gaps detected regarding SEBI Clause 4.2 directive for transaction log management. AWS RDS storage volume encryption is disabled and log stream signatures are missing.",
        compliance_drift_matrix: [
          {
            regulatory_clause: "Clause 4.2(a): Core transaction access logs must be cryptographically signed at the application level.",
            internal_policy_reference: "sebi_logs_policy_test: Section 2",
            status: "Non-Compliant",
            delta_evidence: "AWS infrastructure telemetry registers database log storage has no active application-level cryptographic signing configuration active."
          },
          {
            regulatory_clause: "Clause 4.2(b): Log storage volumes must utilize dedicated KMS CMK with annual auto-rotation.",
            internal_policy_reference: "sebi_logs_policy_test: Section 3",
            status: "Non-Compliant",
            delta_evidence: "AWS RDS database cluster configuration registers storage_encrypted=false and kms_key_id=null. No customer-managed key is utilized."
          }
        ],
        drift_remediation_blueprints: [
          {
            clause_at_risk: "Clause 4.2(a): Application level log signing",
            severity_rating: "HIGH" as any,
            clarity_score: 85,
            technical_remediation_blueprint: "import hmac\nimport hashlib\nimport os\n\ndef sign_log_payload(payload: str) -> str:\n    # Computes HMAC-SHA256 log signature before write\n    signature = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256)\n    return f'SIG={signature.hexdigest()} | MSG={payload}'",
            commit_hash: "a1b2c3d4e5f67890",
            author_name: "Dev DevOps",
            branch_name: "release/v1.1"
          },
          {
            clause_at_risk: "Clause 4.2(b): KMS CMK log storage",
            severity_rating: "CRITICAL" as any,
            clarity_score: 95,
            technical_remediation_blueprint: "resource \"aws_kms_key\" \"telemetry_encryption\" {\n  description             = \"KMS key for financial telemetry DB\"\n  enable_key_rotation     = true\n}\n\nresource \"aws_rds_cluster\" \"financial_telemetry\" {\n  cluster_identifier      = \"aurora-telemetry-cluster\"\n  storage_encrypted     = true\n  kms_key_id            = aws_kms_key.telemetry_encryption.arn\n}",
            commit_hash: "a1b2c3d4e5f67890",
            author_name: "Dev DevOps",
            branch_name: "release/v1.1"
          }
        ],
        remediation_timeline_weeks: 2,
        compliance_health_score: 75
      }
    },
    "f8b9c0d1e2f3a4b5": {
      state: "FinalReport",
      plan: null,
      context: null,
      analysis: null,
      report: {
        executive_summary: "Comprehensive compliance audit registers zero active security drifts or non-compliances. Internal controls match all regulatory requirements perfectly.",
        compliance_drift_matrix: [
          {
            regulatory_clause: "Clause 4.2(a): Centralized log streams must be signed at the application level.",
            internal_policy_reference: "sebi_logs_policy_test: Section 2",
            status: "Compliant",
            delta_evidence: "Telemetry logs verify active SHA-256 signatures are generated and verified on every write."
          }
        ],
        drift_remediation_blueprints: [],
        remediation_timeline_weeks: 0,
        compliance_health_score: 100
      }
    },
    "e4f5a6b7c8d9e0f1": {
      state: "FinalReport",
      plan: null,
      context: null,
      analysis: null,
      report: {
        executive_summary: "Partial compliance verified. Network isolation controls are fully implemented, but hardware-backed multi-factor authentication (MFA) is missing for console logins.",
        compliance_drift_matrix: [
          {
            regulatory_clause: "Clause 4.1.2: Enforce hardware-backed MFA keys for admin operations.",
            internal_policy_reference: "access_policy: Section 1",
            status: "Partial",
            delta_evidence: "Admin console login logs verify software MFA is active, but hardware-backed security keys are not enforced."
          },
          {
            regulatory_clause: "Clause 4.1.4: Strictly segment the network to isolate the core transaction database.",
            internal_policy_reference: "network_policy: Section 5",
            status: "Compliant",
            delta_evidence: "VPC flow registers database subnet is isolated with zero public ingress routes."
          }
        ],
        drift_remediation_blueprints: [
          {
            clause_at_risk: "Clause 4.1.2: Multi-Factor Authentication",
            severity_rating: "MEDIUM" as any,
            clarity_score: 90,
            technical_remediation_blueprint: "# Configure AWS IAM policy to enforce MFA with WebAuthn hardware keys\nresource \"aws_iam_policy\" \"enforce_mfa_webauthn\" {\n  name        = \"EnforceWebAuthnMFA\"\n  description = \"Only allow admin operations when authenticated with FIDO/WebAuthn MFA keys\"\n  policy      = jsonencode({\n    Version = \"2012-10-17\"\n    Statement = [{\n      Sid    = \"BlockNonMFA\"\n      Effect = \"Deny\"\n      Action = \"*\"\n      Resource = \"*\"\n      Condition = {\n        Null = { \"aws:MultiFactorAuthPresent\" = \"true\" }\n      }\n    }]\n  })\n}",
            commit_hash: "e4f5a6b7c8d9e0f1",
            author_name: "Bob Builder",
            branch_name: "feature/logging"
          }
        ],
        remediation_timeline_weeks: 1,
        compliance_health_score: 75
      }
    },
    "cd78ef90ab12cd34": {
      state: "FinalReport",
      plan: null,
      context: null,
      analysis: null,
      report: {
        executive_summary: "Critical compliance failure. Direct database public access is open to all internet traffic, and transaction logs are stored unencrypted in public buckets.",
        compliance_drift_matrix: [
          {
            regulatory_clause: "Clause 4.1.3: Sensitive transaction logs must be encrypted using dedicated customer-managed keys (CMK).",
            internal_policy_reference: "storage_policy: Section 4",
            status: "Non-Compliant",
            delta_evidence: "S3 buckets 'regudrift-transaction-logs' do not have default encryption active, exposing raw log streams in plaintext."
          },
          {
            regulatory_clause: "Clause 4.1.4: Strictly segment network to isolate database.",
            internal_policy_reference: "network_policy: Section 5",
            status: "Non-Compliant",
            delta_evidence: "VPC security group 'db-sg' allows inbound port 5432 directly from 0.0.0.0/0 (public internet)."
          }
        ],
        drift_remediation_blueprints: [
          {
            clause_at_risk: "Clause 4.1.3: Data Encryption at Rest",
            severity_rating: "HIGH" as any,
            clarity_score: 85,
            technical_remediation_blueprint: "# Enable default encryption for S3 buckets using KMS CMK\nresource \"aws_s3_bucket_server_side_encryption_configuration\" \"logs_encryption\" {\n  bucket = \"regudrift-transaction-logs\"\n  rule {\n    apply_server_side_encryption_by_default {\n      kms_master_key_id = \"arn:aws:kms:us-east-1:123456789012:key/your-key\"\n      sse_algorithm     = \"aws:kms\"\n    }\n  }\n}",
            commit_hash: "cd78ef90ab12cd34",
            author_name: "Charlie Coder",
            branch_name: "patch/rotation"
          },
          {
            clause_at_risk: "Clause 4.1.4: Database Network Isolation",
            severity_rating: "CRITICAL" as any,
            clarity_score: 95,
            technical_remediation_blueprint: "# Remove public ingress and isolate DB security group\nresource \"aws_security_group_rule\" \"restrict_db_ingress\" {\n  type              = \"ingress\"\n  from_port         = 5432\n  to_port           = 5432\n  protocol          = \"tcp\"\n  security_group_id = \"sg-db123456\"\n  cidr_blocks       = [\"10.0.1.0/24\"] # Only allow private app subnet range\n}",
            commit_hash: "cd78ef90ab12cd34",
            author_name: "Charlie Coder",
            branch_name: "patch/rotation"
          }
        ],
        remediation_timeline_weeks: 3,
        compliance_health_score: 60
      }
    }
  };

  const [commits, setCommits] = useState<MockCommit[]>(initialCommits);
  const [selectedCommit, setSelectedCommit] = useState<MockCommit>(initialCommits[0]);
  const [gitHash, setGitHash] = useState<string>(initialCommits[0].hash);
  const [gitAuthor, setGitAuthor] = useState<string>(initialCommits[0].author);
  const [gitBranch, setGitBranch] = useState<string>(initialCommits[0].branch);
  
  const [isAuditing, setIsAuditing] = useState<boolean>(false);
  const [auditProgress, setAuditProgress] = useState<number>(0);
  const [auditStatus, setAuditStatus] = useState<string>("");
  
  const [telemetryMap, setTelemetryMap] = useState<Record<string, TelemetryPayload>>(initialTelemetry);
  const [telemetry, setTelemetry] = useState<TelemetryPayload | null>(initialTelemetry["a1b2c3d4e5f67890"]);
  const [recordId, setRecordId] = useState<number>(-1);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [historyData, setHistoryData] = useState<AnalyticsHistoryPoint[]>([]);
  const [healthInfo, setHealthInfo] = useState<any>(null);

  const handleSelectCommit = (commit: MockCommit) => {
    setSelectedCommit(commit);
    setGitHash(commit.hash);
    setGitAuthor(commit.author);
    setGitBranch(commit.branch);
    
    const key = Object.keys(telemetryMap).find(
      (k) => k.substring(0, 8) === commit.hash.substring(0, 8) || k === commit.hash
    );
    if (key && telemetryMap[key]) {
      setTelemetry(telemetryMap[key]);
    } else {
      setTelemetry(null);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await api.getComplianceHistory(role);
      setHistoryData(response.data);
    } catch (err) {
      console.error("Failed to fetch compliance history trend", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [role]);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const info = await api.getHealth();
        setHealthInfo(info);
      } catch (err) {
        console.error("Failed to fetch API health info", err);
      }
    };
    fetchHealth();
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
      const response = await api.ingestPolicy(docId, selectedFile, role);
      setIngestLogs((prev) => [
        ...prev,
        "Computing deterministic SHA-256 chunk hashes...",
        `Generating embeddings for ${response.chunks_count} clauses...`,
        "Indexing embedded dimensions into Qdrant...",
        `Relational DB Record saved ID #${response.relational_record_id}!`,
      ]);
      setLastIngested({
        docId: response.document_id,
        recordId: response.relational_record_id,
        chunksCount: response.chunks_count,
      });
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || err;
      setIngestLogs((prev) => [...prev, `RBAC/Ingestion error: ${errorMsg}`]);
      alert(`Ingestion failed: ${errorMsg}`);
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
      const response = await api.analyzeCompliance(bulletinText, role, {
        commit_hash: gitHash,
        author_name: gitAuthor,
        commit_timestamp: new Date().toISOString(),
        branch_name: gitBranch
      });
      
      setTimeout(() => {
        setAuditProgress(100);
        setAuditStatus("Analysis complete!");
        setTelemetry(response.telemetry);
        setTelemetryMap((prevMap) => ({
          ...prevMap,
          [gitHash]: response.telemetry
        }));
        setRecordId(response.relational_record_id);
        
        const matrix = response.telemetry?.report?.compliance_drift_matrix || [];
        const statuses = matrix.map((m: any) => m.status);
        let newStatus: "Compliant" | "Partial" | "Non-Compliant" = "Compliant";
        if (statuses.includes("Non-Compliant")) {
          newStatus = "Non-Compliant";
        } else if (statuses.includes("Partial")) {
          newStatus = "Partial";
        }

        const newHealth = response.telemetry?.report?.compliance_health_score !== undefined
          ? response.telemetry.report.compliance_health_score
          : 100;

        const updatedCommit = {
          hash: gitHash,
          author: gitAuthor,
          branch: gitBranch,
          timestamp: new Date().toISOString(),
          status: newStatus,
          health: newHealth
        };

        setCommits((prevCommits) => {
          const index = prevCommits.findIndex(
            (c) => c.hash.substring(0, 8) === gitHash.substring(0, 8) || c.hash === gitHash
          );
          if (index !== -1) {
            const newCommits = [...prevCommits];
            newCommits[index] = updatedCommit;
            return newCommits;
          } else {
            return [updatedCommit, ...prevCommits];
          }
        });
        setSelectedCommit(updatedCommit);

        setIsAuditing(false);
        fetchHistory();
        setActiveTab("dashboard");
      }, 3000);
    } catch (err: any) {
      setIsAuditing(false);
      setAuditStatus("Analysis failed.");
      const errorMsg = err.response?.data?.detail || err.message;
      alert(`Audit failed: ${errorMsg}`);
    }
  };

  const handleClearDrifts = async () => {
    if (confirm("Are you sure you want to clear all compliance drifts and historical runs?")) {
      try {
        await api.clearComplianceDrifts(role);
        setTelemetry(null);
        setRecordId(-1);
        fetchHistory();
        alert("All active compliance drifts and historical logs cleared successfully.");
      } catch (err: any) {
        alert(`Clear failed: ${err.response?.data?.detail || err.message}`);
      }
    }
  };

  const handleExportPdf = () => {
    if (!telemetry || !telemetry.report) {
      alert("No active compliance telemetry report to export. Please run the live audit analysis first.");
      return;
    }

    setIsExporting(true);
    const report = telemetry.report;

    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      alert("Pop-up blocker prevented opening report. Please allow popups for this site.");
      setIsExporting(false);
      return;
    }

    const dateStr = new Date().toLocaleString();
    const mappingsHtml = report.compliance_drift_matrix
      .map((m, idx) => {
        const bp = report.drift_remediation_blueprints.find(b => b.clause_at_risk === m.regulatory_clause || m.regulatory_clause.includes(b.clause_at_risk));
        return `
          <div class="card" style="border-left: 5px solid ${
            m.status === "Non-Compliant" ? "#F43F5E" : m.status === "Partial" ? "#FBBC05" : "#10B981"
          };">
            <div class="card-header">Reference Mapping #${idx + 1}</div>
            <div class="field"><span class="label">Regulatory Clause:</span> ${m.regulatory_clause}</div>
            <div class="field"><span class="label">Internal Policy Ref:</span> ${m.internal_policy_reference}</div>
            <div class="field"><span class="label">Alignment Status:</span> <span class="badge ${m.status.toLowerCase()}">${m.status.toUpperCase()}</span></div>
            <div class="field"><span class="label">Delta Evidence:</span> <span class="evidence">${m.delta_evidence}</span></div>
            ${bp?.commit_hash ? `
              <div class="field font-mono" style="font-size: 11px; margin-top: 6px; color: #94a3b8;">
                <strong>Git Commit:</strong> ${bp.commit_hash.substring(0, 8)} | <strong>Author:</strong> ${bp.author_name || "N/A"} | <strong>Branch:</strong> ${bp.branch_name || "N/A"}
              </div>
            ` : ""}
          </div>
        `;
      })
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
          ${b.commit_hash ? `
            <div style="margin-bottom: 8px; font-size: 11px; color: #94a3b8;">
              <strong>Commit:</strong> ${b.commit_hash} | <strong>Author:</strong> ${b.author_name} | <strong>Branch:</strong> ${b.branch_name}
            </div>
          ` : ""}
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
            font-family: Arial, sans-serif;
            background-color: #030712;
            color: #f8fafc;
            margin: 40px;
            font-size: 14px;
            line-height: 1.6;
          }
          header {
            border-bottom: 2px solid #00f0ff;
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
            color: #00f0ff;
          }
          .date {
            font-size: 11px;
            color: #94a3b8;
          }
          .cover-meta {
            background-color: #090f1c;
            border: 1px solid #1e293b;
            padding: 20px;
            border-radius: 12px;
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
            color: #94a3b8;
            width: 180px;
          }
          h2 {
            font-size: 18px;
            color: #00f0ff;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 6px;
            margin-top: 30px;
          }
          .summary-box {
            background-color: #090f1c;
            border-left: 4px solid #8b5cf6;
            padding: 15px;
            font-style: italic;
            margin-bottom: 25px;
          }
          .card {
            background: #090f1c;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            page-break-inside: avoid;
          }
          .card-header {
            font-weight: bold;
            color: #00f0ff;
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
            color: #94a3b8;
            display: inline-block;
            width: 140px;
          }
          .badge {
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 11px;
          }
          .badge.non-compliant, .badge.critical, .badge.high {
            background-color: #4c0519;
            color: #fda4af;
          }
          .badge.partial, .badge.medium {
            background-color: #451a03;
            color: #fde047;
          }
          .badge.compliant, .badge.low {
            background-color: #064e3b;
            color: #6ee7b7;
          }
          .evidence {
            color: #cbd5e1;
          }
          .blueprint-section {
            margin-bottom: 25px;
            page-break-inside: avoid;
          }
          pre {
            font-family: monospace;
            background-color: #030712;
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
            border: 1px solid #1e293b;
          }
          footer {
            margin-top: 50px;
            border-top: 1px solid #1e293b;
            padding-top: 10px;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
          }
          @media print {
            body {
              margin: 0;
              padding-bottom: 60px;
            }
            @page {
              margin-top: 15mm;
              margin-bottom: 20mm;
              margin-left: 15mm;
              margin-right: 15mm;
            }
            footer {
              position: fixed;
              bottom: 0;
              left: 0;
              right: 0;
              border-top: 1px solid #1e293b;
              padding-top: 5px;
              text-align: center;
              background-color: #030712;
            }
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
              <td>${healthInfo?.vector_store_provider?.toUpperCase() === "FAISS" ? "FAISS Local Vector Store" : "QDRANT Vector DB Core"}</td>
            </tr>
            <tr>
              <td class="label">System Boundary:</td>
              <td>${healthInfo?.env === "local" ? "DEVELOPMENT - Local Workstation" : "PRODUCTION - Secure Docker Enclave"}</td>
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

  const getOverallStatus = () => {
    if (!telemetry || !telemetry.report) return selectedCommit.status;
    const statuses = telemetry.report.compliance_drift_matrix.map((m) => m.status);
    if (statuses.includes("Non-Compliant")) return "Non-Compliant";
    if (statuses.includes("Partial")) return "Partial";
    return "Compliant";
  };

  const getOverallHealth = () => {
    if (!telemetry || !telemetry.report) return selectedCommit.health;
    return telemetry.report.compliance_health_score !== undefined
      ? telemetry.report.compliance_health_score
      : selectedCommit.health;
  };

  const renderSonarScanner = () => {
    const health = getOverallHealth();
    const statusCol = health >= 90 ? "stroke-[#10B981]" : health >= 70 ? "stroke-[#FBBC05]" : "stroke-[#F43F5E]";
    return (
      <div className="flex flex-col items-center justify-center p-4 h-full relative">
        <div className="relative w-36 h-36 flex items-center justify-center bg-background rounded-full border border-outline-variant shadow-[0_0_20px_rgba(0,240,255,0.05)]">
          <div className="absolute inset-3 border border-outline-variant/30 rounded-full"></div>
          <div className="absolute inset-8 border border-outline-variant/20 rounded-full"></div>
          <div className="absolute inset-14 border border-outline-variant/10 rounded-full"></div>
          <div className="absolute top-0 bottom-0 left-1/2 w-[1px] bg-outline-variant/25"></div>
          <div className="absolute left-0 right-0 top-1/2 h-[1px] bg-outline-variant/25"></div>

          {}
          <div className={`absolute inset-0 animate-radar-sweep ${isAuditing ? "" : "opacity-30"}`}>
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <line x1="50" y1="50" x2="50" y2="0" stroke="#00F0FF" strokeWidth="1.5" />
              <path d="M50 50 L50 0 A50 50 0 0 1 85 15 Z" fill="url(#radarGradient)" />
              <defs>
                <linearGradient id="radarGradient" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#00F0FF" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {}
          <div className="absolute flex flex-col items-center justify-center z-10 bg-surface/90 border border-outline-variant w-16 h-16 rounded-full shadow-md">
            <span className="text-xl font-bold font-mono text-on-surface">{health}%</span>
            <span className="text-[7px] text-on-surface-variant uppercase font-mono tracking-widest mt-0.5">HEALTH</span>
          </div>
        </div>
      </div>
    );
  };

  const renderGitGraph = () => {
    return (
      <div className="flex flex-col h-full">
        <div className="flex justify-between items-center pb-2 border-b border-outline-variant mb-3">
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-mono font-bold text-secondary uppercase tracking-widest">Commit Graph</span>
            {role === "SecOps_Admin" && (
              <button
                onClick={handleClearDrifts}
                className="text-[8px] font-mono text-error hover:text-red-400 transition-colors px-2 py-0.5 border border-error/30 rounded bg-error/5 hover:bg-error/10 focus:outline-none"
              >
                Clear Logs
              </button>
            )}
          </div>
          <span className="text-[9px] font-mono text-on-surface-variant">Click to blame</span>
        </div>
        <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-2 relative">
          
          {}
          <div className="absolute left-[13px] top-4 bottom-4 w-[2px] bg-outline-variant/60"></div>
          
          {commits.map((commit, idx) => {
            const isSelected = selectedCommit.hash === commit.hash;
            const nodeColor = commit.status === "Compliant" ? "bg-success shadow-[0_0_8px_#10B981]" : commit.status === "Partial" ? "bg-warning shadow-[0_0_8px_#FBBC05]" : "bg-error shadow-[0_0_8px_#F43F5E]";
            return (
              <div
                key={idx}
                onClick={() => handleSelectCommit(commit)}
                className={`pl-8 pr-3 py-2 rounded-lg cursor-pointer transition-all duration-200 border text-left relative flex flex-col ${
                  isSelected
                    ? "bg-[#121B2E]/60 border-primary shadow-[0_0_10px_rgba(0,240,255,0.05)]"
                    : "bg-background border-outline-variant/60 hover:bg-surface-bright hover:border-outline-variant"
                }`}
              >
                {}
                <div className={`absolute left-[9px] top-[15px] w-2.5 h-2.5 rounded-full z-10 ${nodeColor} ${isSelected ? "scale-125 animate-ping" : ""}`}></div>
                <div className={`absolute left-[9px] top-[15px] w-2.5 h-2.5 rounded-full z-20 ${nodeColor} ${isSelected ? "scale-125" : ""}`}></div>

                <div className="flex justify-between items-center mb-1">
                  <span className="font-mono text-[10px] font-bold text-on-surface">
                    {commit.hash.substring(0, 8)}
                  </span>
                  <span className="text-[8px] font-mono text-on-surface-variant font-medium">
                    {commit.branch}
                  </span>
                </div>
                <div className="flex justify-between text-[9px] text-on-surface-variant">
                  <span>{commit.author}</span>
                  <span className={`font-bold ${commit.status === "Compliant" ? "text-success" : commit.status === "Partial" ? "text-warning" : "text-error"}`}>
                    {commit.status.toUpperCase()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="flex bg-background text-on-surface h-screen w-screen overflow-hidden font-sans">
      
      {}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} role={role} setRole={setRole} />

        {}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-background pb-16">
          
          {}
          {activeTab === "dashboard" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              
              {}
              <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-4 flex flex-col shadow-md lg:col-span-1">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[9px] font-mono font-bold tracking-widest text-primary uppercase">Audit Radar Scanner</span>
                  <span className="text-xs">🔄</span>
                </div>
                <div className="flex-grow flex items-center justify-center min-h-[170px]">
                  {renderSonarScanner()}
                </div>
              </div>

              {}
              <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-4 flex flex-col shadow-md lg:col-span-1 h-[250px]">
                {renderGitGraph()}
              </div>

              {}
              <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-4 flex flex-col shadow-md lg:col-span-1 h-[250px]">
                <div className="flex justify-between items-center pb-2 border-b border-outline-variant mb-2">
                  <span className="text-[9px] font-mono font-bold text-primary uppercase tracking-widest">Global Health Trend</span>
                  <span className="text-[9px] font-mono text-on-surface-variant">Time-Series</span>
                </div>
                <div className="flex-grow flex flex-col justify-center">
                  <MetricCards
                    healthScore={getOverallHealth()}
                    activeGuidelines={142}
                    criticalGaps={telemetry?.report?.drift_remediation_blueprints?.length || 12}
                    statusText={getOverallStatus()}
                    hasAudited={!!telemetry}
                    historyData={historyData}
                  />
                </div>
              </div>

              {}
              <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-4 flex flex-col shadow-md md:col-span-2 lg:col-span-3">
                <div className="flex justify-between items-center pb-2 border-b border-outline-variant mb-3">
                  <span className="text-[10px] font-mono font-bold text-primary uppercase tracking-widest">Live Compliance Drift Inspector</span>
                  <span className="text-[9px] font-mono text-on-surface-variant">Comparative Diff Panel</span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {}
                  <div className="bg-[#030712]/50 border border-outline-variant/60 rounded-xl p-4 h-[300px] overflow-y-auto">
                    <div className="text-[9px] font-mono text-secondary mb-2 uppercase tracking-widest">Regulatory Directive Bulletin</div>
                    {telemetry && telemetry.report ? (
                      <div className="flex flex-col gap-2">
                        {telemetry.analysis?.target_clauses_evaluated.map((clause, idx) => (
                          <div key={idx} className="p-3 bg-surface border border-outline-variant/50 rounded-lg">
                            <span className="text-primary font-bold font-mono text-[10px]">Clause {idx + 1}:</span>
                            <p className="mt-1 text-on-surface/90 text-xs">{clause}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-on-surface-variant/80">
                        <p className="mb-3">4.1.2 Enforce hardware-backed multi-factor authentication (MFA) keys for admin operations.</p>
                        <div className="p-3 bg-error/5 border border-error/20 rounded-lg text-on-surface relative">
                          <p className="font-bold text-xs text-error font-mono mb-1 uppercase tracking-wider">⚠️ Clause 4.1.3: Data Encryption at Rest</p>
                          <p className="text-[11px] text-on-surface-variant leading-relaxed">
                            "Sensitive financial telemetry and transaction logs must be encrypted at rest using AES-256 or equivalent cryptographic standards managed by a Key Management Service (KMS)."
                          </p>
                        </div>
                        <p className="mt-3">4.1.4 Strictly segment the network to isolate the core transaction processing environment.</p>
                      </div>
                    )}
                  </div>

                  {}
                  <div className="bg-[#030712]/50 border border-outline-variant/60 rounded-xl p-4 h-[300px] overflow-y-auto">
                    <div className="text-[9px] font-mono text-secondary mb-2 uppercase tracking-widest">Internal Telemetry & Gaps</div>
                    {telemetry && telemetry.report ? (
                      <div className="flex flex-col gap-2">
                        {telemetry.report.compliance_drift_matrix.map((mapping, idx) => {
                          const isCritical = mapping.status === "Non-Compliant";
                          const isWarning = mapping.status === "Partial";
                          
                          const bp = telemetry.report?.drift_remediation_blueprints?.find(
                            (b) => b.clause_at_risk === mapping.regulatory_clause || mapping.regulatory_clause.includes(b.clause_at_risk)
                          );
                          const cHash = bp?.commit_hash || gitHash;
                          const cAuthor = bp?.author_name || gitAuthor;
                          const cBranch = bp?.branch_name || gitBranch;

                          return (
                            <div
                              key={idx}
                              className={`p-3 rounded-lg border-l-4 ${
                                isCritical
                                  ? "bg-error/5 border-error"
                                  : isWarning
                                  ? "bg-warning/5 border-warning"
                                  : "bg-success/5 border-success"
                              }`}
                            >
                              <div className="flex justify-between items-center mb-1">
                                <span className="font-bold text-on-surface text-xs font-mono">Ref: {mapping.internal_policy_reference}</span>
                                <span className={`px-2 py-0.5 rounded-full text-[8px] font-mono font-bold ${
                                  isCritical ? "bg-error/15 text-error" : isWarning ? "bg-warning/15 text-warning" : "bg-success/15 text-success"
                                }`}>
                                  {mapping.status.toUpperCase()}
                                </span>
                              </div>
                              <p className="text-[11px] text-on-surface-variant font-mono mt-1">{mapping.delta_evidence}</p>

                              {}
                              {(isCritical || isWarning) && (
                                <div className="flex flex-wrap gap-1 mt-2.5 pt-1.5 border-t border-outline-variant/30 font-mono text-[9px]">
                                  <span className="bg-[#030712] border border-outline-variant/60 text-secondary px-2 py-0.5 rounded-full">
                                    <strong>HASH:</strong> {cHash.substring(0, 8)}
                                  </span>
                                  <span className="bg-[#030712] border border-outline-variant/60 text-secondary px-2 py-0.5 rounded-full">
                                    <strong>AUTHOR:</strong> {cAuthor}
                                  </span>
                                  <span className="bg-[#030712] border border-outline-variant/60 text-secondary px-2 py-0.5 rounded-full">
                                    <strong>BRANCH:</strong> {cBranch}
                                  </span>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="font-mono text-[11px] text-on-surface-variant/80">
                        <div># Snapshot: telemetry-organization-root</div>
                        <div className="mb-3"># AWS Region: eu-west-1</div>
                        <div className="pl-2 border-l-2 border-outline-variant mb-3">
                          <div className="text-success">Resource: aws_iam_role.admin_gateway</div>
                          <div className="pl-4">mfa_enforced = <span className="text-success">true</span></div>
                        </div>
                        <div className="p-3 bg-error/5 border border-error/30 rounded-lg relative">
                          <div className="text-error font-bold font-mono">Resource: aws_rds_cluster.financial_telemetry</div>
                          <div className="pl-4 mt-1">engine = "aurora-postgresql"</div>
                          <div className="pl-4">
                            storage_encrypted = <span className="text-error bg-error/15 px-1 rounded font-bold">false</span>
                            <span className="text-error/40 ml-2"># DRIFT DETECTED</span>
                          </div>
                          
                          {}
                          <div className="flex flex-wrap gap-1 mt-3 pt-2 border-t border-outline-variant/30 font-mono text-[9px]">
                            <span className="bg-[#030712] border border-outline-variant/60 text-secondary px-2 py-0.5 rounded-full">
                              <strong>HASH:</strong> {gitHash.substring(0, 8)}
                            </span>
                            <span className="bg-[#030712] border border-outline-variant/60 text-secondary px-2 py-0.5 rounded-full">
                              <strong>AUTHOR:</strong> {gitAuthor}
                            </span>
                            <span className="bg-[#030712] border border-outline-variant/60 text-secondary px-2 py-0.5 rounded-full">
                              <strong>BRANCH:</strong> {gitBranch}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {}
              <div className="lg:col-span-3">
                <Remediation
                  blueprints={telemetry?.report?.drift_remediation_blueprints}
                  onExportPdf={handleExportPdf}
                  isExportingPdf={isExporting}
                />
              </div>

            </div>
          )}

          {}
          {activeTab === "ingestion" && (
            <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-container-padding flex flex-col shadow-md">
              <h2 className="text-sm font-bold text-on-surface mb-1">
                Policy Ingestion Console
              </h2>
              <p className="text-xs text-on-surface-variant mb-6 font-mono">
                Asynchronous chunking, embedding generation, and Qdrant vector store indexing.
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter mt-2 border-t border-outline-variant pt-6">
                <div className="lg:col-span-2 flex flex-col gap-4">
                  <div>
                    <label className="block text-[10px] font-mono text-on-surface-variant uppercase tracking-wider mb-2">
                      Document ID Slug
                    </label>
                    <input
                      value={docId}
                      onChange={(e) => setDocId(e.target.value)}
                      className="w-full bg-[#030712] border border-outline-variant rounded-lg p-3 text-xs text-on-surface focus:outline-none focus:border-primary"
                      type="text"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-mono text-on-surface-variant uppercase tracking-wider mb-2">
                      Choose policy document (.txt or .pdf)
                    </label>
                    <div className="border-2 border-dashed border-outline-variant rounded-lg p-8 text-center bg-[#030712] flex flex-col items-center justify-center transition-all hover:bg-[#030712]/50">
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
                        className="bg-surface border border-outline-variant hover:border-primary/50 text-on-surface-variant font-mono text-[9px] px-4 py-2 rounded-full cursor-pointer uppercase transition-all mb-2 shadow-sm"
                      >
                        Choose File
                      </label>
                      <span className="text-xs text-on-surface-variant font-medium">
                        {selectedFile ? `Selected: ${selectedFile.name}` : "No file selected"}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={handleIngest}
                    disabled={isIngesting}
                    className="w-full bg-primary text-background font-mono text-xs py-3 rounded-full hover:brightness-110 uppercase transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed tracking-wide shadow-md"
                  >
                    {isIngesting ? "Indexing & Ingesting Chunks..." : "Index and Store Policy"}
                  </button>
                </div>

                <div className="bg-[#030712]/50 border border-outline-variant p-container-padding rounded-xl flex flex-col h-[380px] shadow-inner">
                  <h3 className="text-[10px] font-mono text-on-surface uppercase tracking-wider mb-3">
                    Ingestion Process Logs
                  </h3>
                  <div className="flex-1 overflow-y-auto font-mono text-[11px] text-success flex flex-col gap-1.5 pr-2">
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

          {}
          {activeTab === "audit" && (
            <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-container-padding flex flex-col shadow-md">
              <h2 className="text-sm font-bold text-on-surface mb-1">
                Live Audit Console
              </h2>
              <p className="text-xs text-on-surface-variant mb-6 font-mono">
                Paste regulatory bulletin payloads and inject active Git CI/CD tracking metrics.
              </p>
              
              <div className="flex flex-col gap-4 border-t border-outline-variant pt-6">
                
                {}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-[#030712]/60 border border-outline-variant p-4 rounded-xl shadow-sm">
                  <div className="md:col-span-3 pb-2 border-b border-outline-variant/40 flex justify-between">
                    <span className="text-[10px] text-primary font-mono uppercase font-bold tracking-widest">Git Commit Blamer Context</span>
                    <span className="text-on-surface-variant font-mono text-[10px]">CI/CD Metadata</span>
                  </div>
                  <div>
                    <label className="block text-[9px] font-mono text-on-surface-variant uppercase tracking-wider mb-1">Commit Hash</label>
                    <input
                      value={gitHash}
                      onChange={(e) => setGitHash(e.target.value)}
                      className="w-full bg-[#030712] border border-outline-variant rounded-lg px-3 py-2 text-xs text-on-surface focus:outline-none focus:border-primary font-mono"
                      type="text"
                    />
                  </div>
                  <div>
                    <label className="block text-[9px] font-mono text-on-surface-variant uppercase tracking-wider mb-1">Author Name</label>
                    <input
                      value={gitAuthor}
                      onChange={(e) => setGitAuthor(e.target.value)}
                      className="w-full bg-[#030712] border border-outline-variant rounded-lg px-3 py-2 text-xs text-on-surface focus:outline-none focus:border-primary font-mono"
                      type="text"
                    />
                  </div>
                  <div>
                    <label className="block text-[9px] font-mono text-on-surface-variant uppercase tracking-wider mb-1">Target Branch</label>
                    <input
                      value={gitBranch}
                      onChange={(e) => setGitBranch(e.target.value)}
                      className="w-full bg-[#030712] border border-outline-variant rounded-lg px-3 py-2 text-xs text-on-surface focus:outline-none focus:border-primary font-mono"
                      type="text"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-mono text-on-surface-variant uppercase tracking-wider mb-2">
                    Raw Regulatory Bulletin Payload
                  </label>
                  <textarea
                    value={bulletinText}
                    onChange={(e) => setBulletinText(e.target.value)}
                    rows={8}
                    className="w-full bg-[#030712] border border-outline-variant rounded-lg p-4 font-mono text-xs text-on-surface focus:outline-none focus:border-primary resize-none leading-relaxed"
                    placeholder="Paste bulletin payload here..."
                  />
                </div>

                <button
                  onClick={handleAnalyze}
                  disabled={isAuditing}
                  className="w-full bg-primary text-background font-mono text-xs py-3 rounded-full hover:brightness-110 uppercase transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed tracking-wide shadow-md"
                >
                  {isAuditing ? "Auditing Gaps..." : "Execute Regulatory Drift Analysis"}
                </button>

                {}
                {isAuditing && (
                  <div className="bg-[#030712]/50 border border-outline-variant p-container-padding rounded-xl mt-2 flex flex-col gap-3 shadow-inner">
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-xs text-primary font-bold">{auditStatus}</span>
                      <span className="font-mono text-xs text-on-surface-variant font-semibold">{auditProgress}%</span>
                    </div>
                    <div className="w-full bg-surface h-2 rounded-full overflow-hidden">
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

        {}
        <footer className="flex justify-between items-center w-full px-gutter py-2 z-40 fixed bottom-0 right-0 border-t border-outline-variant bg-surface flex-wrap gap-2 shadow-md">
          <div className="font-mono text-[9px] text-on-surface-variant flex items-center gap-1.5 uppercase tracking-widest">
            <span className="text-secondary">●</span>
            System Integrity: SECURED
          </div>
          <div className="flex items-center gap-container-padding font-mono text-[9px] text-on-surface-variant flex-wrap uppercase">
            <span>Data Sync: 100% Valid</span>
            <span className="flex items-center gap-1">
              <span className="text-success text-xs">✔</span>
              Log Integrity: Cryptographically Verified
            </span>
          </div>
        </footer>

      </div>
    </div>
  );
}
