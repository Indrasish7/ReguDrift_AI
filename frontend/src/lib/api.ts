import axios from "axios";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    if (hostname.includes("localhost") || hostname.includes("127.0.0.1")) {
      return "http://localhost:8000";
    }
    if (hostname.includes("regudrift-console-")) {
      return `${window.location.protocol}//${hostname.replace("regudrift-console-", "regudrift-web-")}`;
    }
    return process.env.NEXT_PUBLIC_API_URL || `${window.location.protocol}//${hostname}`;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

const API_BASE_URL = getBaseUrl();


const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface IngestResponse {
  document_id: string;
  chunks_count: number;
  relational_record_id: number;
  message: string;
}

export interface ComplianceGapMapping {
  regulatory_clause: string;
  internal_policy_reference: string;
  status: "Compliant" | "Partial" | "Non-Compliant";
  delta_evidence: string;
}

export interface DriftRemediationBlueprint {
  clause_at_risk: string;
  severity_rating: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  clarity_score: number;
  technical_remediation_blueprint: string;
  commit_hash?: string;
  author_name?: string;
  commit_timestamp?: string;
  branch_name?: string;
}

export interface TelemetryPayload {
  state: string;
  plan: {
    analysis_objectives: string[];
    information_needs: string[];
    search_queries: string[];
  } | null;
  context: {
    queries_executed: string[];
    retrieved_evidence_summary: string;
    retrieved_references: string[];
  } | null;
  analysis: {
    target_clauses_evaluated: string[];
    compliance_gaps: ComplianceGapMapping[];
  } | null;
  report: {
    executive_summary: string;
    compliance_drift_matrix: ComplianceGapMapping[];
    drift_remediation_blueprints: DriftRemediationBlueprint[];
    remediation_timeline_weeks: number;
    compliance_health_score?: number;
  } | null;
}

export interface AnalyzeResponse {
  relational_record_id: number;
  telemetry: TelemetryPayload;
}

export interface AnalyticsHistoryPoint {
  date: string;
  global_health_score: number;
  total_critical_drifts: number;
  timestamp: string;
}

export const api = {
  
  async ingestPolicy(documentId: string, file: File, role: string): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append("document_id", documentId);
    formData.append("file", file);

    const response = await axios.post<IngestResponse>(
      `${API_BASE_URL}/api/v1/compliance/ingest`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          "X-User-Role": role
        },
      }
    );
    return response.data;
  },

  
  async analyzeCompliance(
    updateText: string,
    role: string,
    gitMeta?: {
      commit_hash?: string;
      author_name?: string;
      commit_timestamp?: string;
      branch_name?: string;
    }
  ): Promise<AnalyzeResponse> {
    const payload = {
      update_text: updateText,
      commit_hash: gitMeta?.commit_hash,
      author_name: gitMeta?.author_name,
      commit_timestamp: gitMeta?.commit_timestamp,
      branch_name: gitMeta?.branch_name,
    };
    const response = await apiClient.post<AnalyzeResponse>("/compliance/analyze", payload, {
      headers: {
        "X-User-Role": role
      }
    });
    return response.data;
  },

  
  async getHealth(): Promise<{ status: string; env: string; vector_store_provider: string }> {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  
  async getComplianceHistory(role: string): Promise<{ data: AnalyticsHistoryPoint[] }> {
    const response = await apiClient.get("/analytics/compliance-history", {
      headers: {
        "X-User-Role": role
      }
    });
    return response.data;
  },

  
  async clearComplianceDrifts(role: string): Promise<{ message: string }> {
    const response = await apiClient.delete("/compliance/drifts", {
      headers: {
        "X-User-Role": role
      }
    });
    return response.data;
  },

  
  async updateConnection(
    role: string,
    provider: "faiss" | "qdrant",
    qdrantUrl?: string,
    databaseUrl?: string
  ): Promise<any> {
    const response = await apiClient.post("/infrastructure/connection", {
      vector_provider: provider,
      qdrant_url: qdrantUrl,
      database_url: databaseUrl
    }, {
      headers: {
        "X-User-Role": role
      }
    });
    return response.data;
  }
};
