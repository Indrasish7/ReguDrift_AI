import asyncio
import logging
from typing import List, Optional
from google import genai
from google.genai import types

from regudrift.config.settings import settings
from regudrift.core.agent.schemas import (
    AgentStatePayload,
    ContextRetrieval,
    FinalReport,
    GapAnalysis,
    PlanCreation,
    StateEnum,
)
from regudrift.core.retrieval.embedder import AsyncEmbeddingGenerator
from regudrift.core.vector.base import BaseVectorService

logger = logging.getLogger("regudrift.agent.orchestrator")


def inline_refs(schema: dict, defs: dict) -> dict:
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"]
            def_name = ref_path.split("/")[-1]
            resolved = inline_refs(defs[def_name], defs)
            new_schema = dict(schema)
            new_schema.pop("$ref")
            new_schema.update(resolved)
            return new_schema
        return {k: inline_refs(v, defs) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [inline_refs(item, defs) for item in schema]
    return schema


def clean_schema_for_gemini(schema):
    if isinstance(schema, dict):
        cleaned = {}
        for k, v in schema.items():
            if k == "title":
                continue
            cleaned[k] = clean_schema_for_gemini(v)
        return cleaned
    elif isinstance(schema, list):
        return [clean_schema_for_gemini(item) for item in schema]
    return schema


def get_gemini_schema(model_class) -> dict:
    raw_schema = model_class.model_json_schema()
    defs = raw_schema.pop("$defs", {})
    inlined = inline_refs(raw_schema, defs)
    return clean_schema_for_gemini(inlined)


class AgenticOrchestrationCarrier:
    """
    Stateful compliance auditing agent carrier.
    Coordinates the Planner-Executor pattern, traversing State transitions:
    PlanCreation -> ContextRetrieval -> GapAnalysis -> FinalReport.
    
    Uses structured schema boundaries to validate all Gemini analytical outputs.
    """

    def __init__(
        self,
        vector_service: BaseVectorService,
        embedder: AsyncEmbeddingGenerator,
        model_name: str = "gemini-2.5-flash"
    ):
        self.vector_service = vector_service
        self.embedder = embedder
        self.model_name = model_name
        
        # Instantiate GenAI Client utilizing settings' SecretStr securely
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY.get_secret_value()
        )

    async def execute_analysis_loop(self, raw_regulatory_update: str) -> AgentStatePayload:
        """
        Runs the full asynchronous compliance assessment loop, driving the agent
        through state transitions and querying the vector store programmatically.
        
        Args:
            raw_regulatory_update: Raw string text of the new regulation mandate.
            
        Returns:
            An AgentStatePayload containing final reports and all state metrics.
        """
        logger.info("Initializing compliance audit loop...")
        
        # --- Stage 1: Plan Creation ---
        logger.info("Transitioning to State: PlanCreation")
        plan = await self._generate_plan(raw_regulatory_update)
        state_payload = AgentStatePayload(
            state=StateEnum.PLAN_CREATION,
            plan=plan
        )

        # --- Stage 2: Context Retrieval & Ingestion ---
        logger.info("Transitioning to State: ContextRetrieval")
        context = await self._ingest_policy_context(plan)
        state_payload.state = StateEnum.CONTEXT_RETRIEVAL
        state_payload.context = context

        # --- Stage 3: Gap Analysis Mapping ---
        logger.info("Transitioning to State: GapAnalysis")
        analysis = await self._run_gap_analysis(raw_regulatory_update, context)
        state_payload.state = StateEnum.GAP_ANALYSIS
        state_payload.analysis = analysis

        # --- Stage 4: Synthesis & Final Report ---
        logger.info("Transitioning to State: FinalReport")
        report = await self._generate_final_report(analysis)
        state_payload.state = StateEnum.FINAL_REPORT
        state_payload.report = report
        
        logger.info("Compliance audit loop completed successfully!")
        return state_payload

    async def _generate_plan(self, regulatory_update: str) -> PlanCreation:
        """
        Planner phase: Formulates goals and dynamic search queries.
        """
        prompt = (
            f"You are the Lead Fintech Compliance Officer at ReguDrift AI.\n"
            f"Analyze this new regulatory update raw payload:\n"
            f"\"\"\"\n{regulatory_update}\n\"\"\"\n\n"
            f"Formulate key compliance assessment objectives, list the critical information "
            f"we need to verify inside our internal policies, and generate 3 to 5 highly specific "
            f"search terms/queries to retrieve relevant policies from our vector database."
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=get_gemini_schema(PlanCreation),
                temperature=0.1
            )
        )
        # Parse Pydantic output natively
        # Google SDK returns types.GenerateContentResponse, response.text holds JSON string
        return PlanCreation.model_validate_json(response.text)

    async def _ingest_policy_context(self, plan: PlanCreation) -> ContextRetrieval:
        """
        Executor phase: Vector Search and Context Aggregation.
        """
        logger.info(f"Formulated {len(plan.search_queries)} search queries. Executing retrieval...")
        
        all_retrieved_chunks = []
        references = set()
        
        # Concurrently compute embeddings for all search queries to preserve efficiency
        query_embeddings = await self.embedder.generate_embeddings(plan.search_queries)
        
        # Execute FAISS/Qdrant vector queries sequentially or concurrently
        search_tasks = [
            self.vector_service.search(emb, limit=2)
            for emb in query_embeddings
        ]
        search_results_list = await asyncio.gather(*search_tasks)
        
        # Consolidate results, removing duplicate chunk contents
        seen_ids = set()
        for results in search_results_list:
            for res in results:
                if res.chunk.id not in seen_ids:
                    seen_ids.add(res.chunk.id)
                    all_retrieved_chunks.append(res.chunk)
                    
                    # Capture structural reference if present
                    hierarchy_path = res.chunk.metadata.get("parent_hierarchy", "Root")
                    references.add(hierarchy_path)

        # Prepare evidence text buffer to present to Gemini
        evidence_buffer = []
        for i, chunk in enumerate(all_retrieved_chunks):
            ref = chunk.metadata.get("parent_hierarchy", "General Policy")
            evidence_buffer.append(
                f"[Source Ref: {ref}]\nContent Excerpt: {chunk.content}\n"
            )
            
        retrieved_text = "\n---\n".join(evidence_buffer) if evidence_buffer else "No internal policy matches located."
        
        # Present matching details to Gemini to extract a unified context summary
        prompt = (
            f"Synthesize our retrieved internal policy materials into a standardized context summary.\n"
            f"List of queries executed: {plan.search_queries}\n\n"
            f"Raw Policy Matches Ingested:\n\"\"\"\n{retrieved_text}\n\"\"\"\n\n"
            f"Provide a clear, consolidated summary of internal controls currently active. "
            f"Map which references cover these items."
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=get_gemini_schema(ContextRetrieval),
                temperature=0.1
            )
        )
        return ContextRetrieval.model_validate_json(response.text)

    async def _run_gap_analysis(self, regulatory_update: str, context: ContextRetrieval) -> GapAnalysis:
        """
        Executor phase: Compares regulation to policy and highlights alignment or drift gaps.
        """
        prompt = (
            f"Perform a strict comparative compliance audit between the new regulation and internal policy.\n\n"
            f"New Regulatory Update:\n\"\"\"\n{regulatory_update}\n\"\"\"\n\n"
            f"Active Internal Policies Summary:\n\"\"\"\n{context.retrieved_evidence_summary}\n\"\"\"\n\n"
            f"List of Source References Checked: {context.retrieved_references}\n\n"
            f"Determine alignment status for each clause: Compliant, Partial, or Non-Compliant. "
            f"Detail explicit 'delta_evidence' outlining why alignment holds or where gaps exist."
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=get_gemini_schema(GapAnalysis),
                temperature=0.2
            )
        )
        return GapAnalysis.model_validate_json(response.text)

    async def _generate_final_report(self, analysis: GapAnalysis) -> FinalReport:
        """
        Synthesis phase: Drafts actionable mitigation blueprints and estimates timelines.
        """
        prompt = (
            f"Synthesize the final audit report for compliance drift remediation.\n"
            f"Map all analyzed evaluated sections here:\n"
            f"\"\"\"\n{analysis.model_dump_json(indent=2)}\n\"\"\"\n\n"
            f"Create a DriftRemediationBlueprint for every identified compliance gap ('Partial' or 'Non-Compliant'). "
            f"Each blueprint MUST explicitly capture:\n"
            f"- clause_at_risk: Target clause/section.\n"
            f"- severity_rating: LOW, MEDIUM, HIGH, CRITICAL.\n"
            f"- clarity_score: Clarity score (0-100).\n"
            f"- technical_remediation_blueprint: Explicit database schema updates, system changes, or policy edits.\n\n"
            f"Summarize the findings in an executive summary and evaluate the engineering timeline in weeks."
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=get_gemini_schema(FinalReport),
                temperature=0.2
            )
        )
        return FinalReport.model_validate_json(response.text)
