from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    PARTIAL = "Partial"
    NON_COMPLIANT = "Non-Compliant"


class SeverityRating(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StateEnum(str, Enum):
    PLAN_CREATION = "PlanCreation"
    CONTEXT_RETRIEVAL = "ContextRetrieval"
    GAP_ANALYSIS = "GapAnalysis"
    FINAL_REPORT = "FinalReport"


class PlanCreation(BaseModel):
    """
    Objectives and search query strategies formulated based on the regulatory update.
    """
    analysis_objectives: List[str] = Field(
        ...,
        description="Core compliance and operational assessment objectives derived from the update."
    )
    information_needs: List[str] = Field(
        ...,
        description="Missing internal policy information needed to verify compliance."
    )
    search_queries: List[str] = Field(
        ...,
        description="Optimized search phrases to run against internal policy vector stores."
    )


class ContextRetrieval(BaseModel):
    """
    Synthesized overview of internal policies retrieved to match regulatory requirements.
    """
    queries_executed: List[str] = Field(..., description="The search terms run against the vector DB.")
    retrieved_evidence_summary: str = Field(
        ...,
        description="Comprehensive summary of retrieved internal controls and procedures."
    )
    retrieved_references: List[str] = Field(
        ...,
        description="Source identifier references (e.g. Chapter I > Section 2) of matching clauses."
    )


class ComplianceGapMapping(BaseModel):
    """
    Granular comparison showing where an internal policy aligns or drifts from a regulatory clause.
    """
    regulatory_clause: str = Field(..., description="The target clause or section of the new regulation.")
    internal_policy_reference: str = Field(..., description="Matching section or clause in internal policy.")
    status: ComplianceStatus = Field(..., description="Compliance alignment status.")
    delta_evidence: str = Field(
        ...,
        description="Direct mapping analysis detailing the alignment or the missing gap."
    )


class GapAnalysis(BaseModel):
    """
    Consolidated compliance gap assessments.
    """
    target_clauses_evaluated: List[str] = Field(..., description="List of regulatory sections analyzed.")
    compliance_gaps: List[ComplianceGapMapping] = Field(..., description="Detailed mappings for all evaluated sections.")


class DriftRemediationBlueprint(BaseModel):
    """
    Technical and operational guide to remediate compliance drift for a specific clause.
    Includes Git blamer metadata tracking fields.
    """
    clause_at_risk: str = Field(
        ...,
        description="The regulatory clause or internal section that requires remediation."
    )
    severity_rating: SeverityRating = Field(
        ...,
        description="Impact severity if this gap remains unaddressed: LOW, MEDIUM, HIGH, CRITICAL."
    )
    clarity_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Subjective clarity of the regulatory mandate (0 = highly ambiguous, 100 = crystal clear)."
    )
    technical_remediation_blueprint: str = Field(
        ...,
        description="Explicit step-by-step engineering, data flow, or process modifications required."
    )

    commit_hash: Optional[str] = Field(None, description="Git commit hash associated with this drift.")
    author_name: Optional[str] = Field(None, description="Git commit author name.")
    commit_timestamp: Optional[str] = Field(None, description="Git commit ISO/unix timestamp.")
    branch_name: Optional[str] = Field(None, description="Git branch name.")


class FinalReport(BaseModel):
    """
    Synthesized regulatory drift audit report containing remediation blue prints.
    """
    executive_summary: str = Field(..., description="High-level summary of the drift audit findings.")
    compliance_drift_matrix: List[ComplianceGapMapping] = Field(
        ...,
        description="Granular matrix showing alignment state."
    )
    drift_remediation_blueprints: List[DriftRemediationBlueprint] = Field(
        ...,
        description="Remediation steps for each identified compliance gap."
    )
    remediation_timeline_weeks: int = Field(
        ...,
        description="Estimated overall engineering effort to resolve all gaps in weeks."
    )


class AgentStatePayload(BaseModel):
    """
    State payload tracing the progress of ReguDrift AI's compliance orchestrator loop.
    """
    state: StateEnum = Field(..., description="The current active stage of analysis.")
    plan: Optional[PlanCreation] = Field(None, description="Plan generated in stage 1.")
    context: Optional[ContextRetrieval] = Field(None, description="Consolidated context from stage 2.")
    analysis: Optional[GapAnalysis] = Field(None, description="Gap analysis from stage 3.")
    report: Optional[FinalReport] = Field(None, description="Synthesized remediation report from stage 4.")
