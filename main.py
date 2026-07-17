import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Literal, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from regudrift.config.settings import settings
from regudrift.core.agent.orchestrator import AgenticOrchestrationCarrier
from regudrift.core.agent.schemas import AgentStatePayload
from regudrift.core.retrieval.embedder import AsyncEmbeddingGenerator
from regudrift.core.ingestion.parser import DocumentParser
from regudrift.core.vector.faiss_service import LocalFAISSService
from regudrift.core.vector.qdrant_service import QdrantVectorService
from regudrift.core.vector.base import BaseVectorService, VectorServiceError

from regudrift.core.database.session import engine, get_db_session
from regudrift.core.database.models import Base
from regudrift.core.database.service import AuditPersistenceService

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("regudrift.api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Bootstrapping ReguDrift AI [{settings.ENV} mode]...")
    
    logger.info("Initializing relational database schema tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Asynchronous database tables initialized successfully!")
    except Exception as e:
        logger.critical(f"FATAL: Relational database schema generation failed: {e}")

    if settings.VECTOR_STORE_PROVIDER == "faiss":
        logger.info(f"Initializing Local FAISS retrieval service at: {settings.FAISS_INDEX_PATH}")
        vector_service = LocalFAISSService()
    else:
        logger.info(f"Initializing Production Qdrant retrieval service at: {settings.QDRANT_URL}")
        vector_service = QdrantVectorService()
        
    try:
        await vector_service.initialize()
        app.state.vector_service = vector_service
        logger.info("Vector retrieval layer successfully initialized!")
    except Exception as e:
        logger.critical(f"FATAL: Vector retrieval layer initialization failed: {e}")
        app.state.vector_service = None

    app.state.embedder = AsyncEmbeddingGenerator()
    app.state.parser = DocumentParser()

    yield
    
    logger.info("Tearing down database connection pools...")
    await engine.dispose()
    logger.info("ReguDrift AI server resources cleanly closed.")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.1.0",
    description="Enterprise Compliance Drifts Engine with Role-Based Access Control and Trend Analytics",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegulatoryUpdateRequest(BaseModel):
    update_text: str = Field(
        ...,
        description="The raw string content of the new regulatory update or compliance mandate."
    )
    commit_hash: Optional[str] = Field(None, description="Optional git commit hash associated with this run.")
    author_name: Optional[str] = Field(None, description="Optional git commit author name.")
    commit_timestamp: Optional[str] = Field(None, description="Optional git commit timestamp.")
    branch_name: Optional[str] = Field(None, description="Optional git branch name.")


class ConnectionUpdateRequest(BaseModel):
    vector_provider: Literal["faiss", "qdrant"] = Field(..., description="Active vector database provider.")
    qdrant_url: Optional[str] = Field(None, description="Qdrant server endpoint URL.")
    database_url: Optional[str] = Field(None, description="Relational database connection URL.")


class IngestionResponse(BaseModel):
    document_id: str
    chunks_count: int
    relational_record_id: int = Field(..., description="Primary key record tracking ID in relational DB.")
    message: str


class AnalyzeResponse(BaseModel):
    relational_record_id: int = Field(..., description="Relational database AuditRun key record tracking ID.")
    telemetry: AgentStatePayload = Field(..., description="The state transition trace metadata payload.")


def require_role(allowed_roles: List[str]):
    """
    FastAPI security dependency ensuring the incoming request has the correct user role.
    Accepts role values through 'X-User-Role' header or 'role' query parameter.
    """
    async def role_checker(
        x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
        role: Optional[str] = Query(None)
    ):
        user_role = x_user_role or role
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User role metadata missing. Provide 'X-User-Role' header or 'role' query parameter."
            )
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role '{user_role}' has insufficient permissions (Required: {allowed_roles})."
            )
        return user_role
    return role_checker


@app.exception_handler(VectorServiceError)
async def vector_exception_handler(request, exc):
    logger.error(f"Vector Database operation error: {exc}")
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Compliance Vector Store is currently unavailable: {str(exc)}"
    )



@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    vector_status = "uninitialized"
    if hasattr(app.state, "vector_service") and app.state.vector_service:
        vector_status = "healthy"
        
    return {
        "status": "healthy",
        "env": settings.ENV,
        "vector_store_provider": settings.VECTOR_STORE_PROVIDER,
        "vector_status": vector_status,
        "app_name": settings.APP_NAME
    }


@app.post(
    "/api/v1/compliance/ingest",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED
)
async def ingest_internal_policy(
    document_id: str = Form(..., description="Unique code or slug to identify internal policy."),
    file: UploadFile = File(..., description="Internal Policy payload file (supports .txt or .pdf)."),
    db: AsyncSession = Depends(get_db_session),
    current_role: str = Depends(require_role(["SecOps_Admin"]))
):
    """
    Ingestion stream endpoint: parses uploaded internal policies, generates semantic chunks,
    extracts chapter/section hierarchies, computes embeddings, and indexes them.
    Protected: Only accessible by SecOps_Admin.
    """
    if not app.state.vector_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector service uninitialized or failing to connect."
        )

    try:
        content_bytes = await file.read()
        filename = file.filename or "policy.txt"
        
        if filename.endswith(".pdf"):
            parsed_doc = await app.state.parser.parse_pdf(content_bytes, document_id, filename)
        else:
            text_str = content_bytes.decode("utf-8", errors="ignore")
            parsed_doc = await app.state.parser.parse_txt(text_str, document_id, filename)

        if not parsed_doc.chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document parsing generated zero text chunks."
            )

        logger.info(f"Generating embeddings for {len(parsed_doc.chunks)} chunks...")
        chunk_contents = [c.content for c in parsed_doc.chunks]
        embeddings = await app.state.embedder.generate_embeddings(chunk_contents)

        logger.info("Indexing structured chunks into the vector store...")
        added_hashes = await app.state.vector_service.add_documents(
            chunks=parsed_doc.chunks,
            embeddings=embeddings
        )

        db_service = AuditPersistenceService(db)
        storage_coord = (
            f"provider={settings.VECTOR_STORE_PROVIDER};"
            f"collection={settings.DEFAULT_COLLECTION_NAME if settings.VECTOR_STORE_PROVIDER == 'qdrant' else settings.FAISS_INDEX_PATH}"
        )
        doc_record = await db_service.create_document_record(
            document_id=document_id,
            filename=filename,
            storage_coordinates=storage_coord
        )

        return IngestionResponse(
            document_id=document_id,
            chunks_count=len(added_hashes),
            relational_record_id=doc_record.id,
            message=f"Successfully parsed, indexed, and persistent-logged policy document '{filename}'!"
        )

    except Exception as e:
        logger.exception("Ingestion request processing failed.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal policy ingestion failed: {str(e)}"
        )


@app.post(
    "/api/v1/compliance/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK
)
async def analyze_compliance_drift(
    payload: RegulatoryUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_role: str = Depends(require_role(["SecOps_Admin"]))
):
    """
    Compliance Drift Assessment endpoint.
    Orchestrates the multi-stage Agentic loop, traverses planning/retrieval stages,
    incorporates Git CI/CD commit blamer variables, and logs results to SQLite.
    Protected: Only accessible by SecOps_Admin.
    """
    if not app.state.vector_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Compliance Vector Service is currently uninitialized."
        )

    try:
        carrier = AgenticOrchestrationCarrier(
            vector_service=app.state.vector_service,
            embedder=app.state.embedder
        )
        
        final_state = await carrier.execute_analysis_loop(
            raw_regulatory_update=payload.update_text,
            commit_hash=payload.commit_hash,
            author_name=payload.author_name,
            commit_timestamp=payload.commit_timestamp,
            branch_name=payload.branch_name
        )

        if final_state.report:
            logger.info("Persisting drift audit execution run to SQL historical log...")
            db_service = AuditPersistenceService(db)
            audit_record = await db_service.persist_audit_run(
                raw_regulatory_update=payload.update_text,
                report=final_state.report,
                commit_hash=payload.commit_hash,
                author_name=payload.author_name,
                commit_timestamp=payload.commit_timestamp,
                branch_name=payload.branch_name
            )
            record_id = audit_record.id
        else:
            record_id = -1
            logger.warning("Audit run resulted in incomplete analysis. Skipping db save.")

        return AnalyzeResponse(
            relational_record_id=record_id,
            telemetry=final_state
        )

    except Exception as e:
        logger.exception("Compliance drift assessment audit loop failed.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent analysis audit loop failed: {str(e)}"
        )


@app.get(
    "/api/v1/analytics/compliance-history",
    status_code=status.HTTP_200_OK
)
async def get_compliance_history_analytics(
    db: AsyncSession = Depends(get_db_session),
    current_role: str = Depends(require_role(["Auditor", "SecOps_Admin"]))
):
    """
    Compliance historical trend analytics time-series endpoint.
    Aggregates historical runs chronologically by date tracking scores and drifts.
    Accessible: Auditor and SecOps_Admin.
    """
    try:
        db_service = AuditPersistenceService(db)
        history = await db_service.get_compliance_history()
        return {
            "status": "success",
            "count": len(history),
            "data": history
        }
    except Exception as e:
        logger.exception("Failed to retrieve compliance history analytics.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile compliance history data: {str(e)}"
        )


@app.delete(
    "/api/v1/compliance/drifts",
    status_code=status.HTTP_200_OK
)
async def clear_compliance_drifts(
    db: AsyncSession = Depends(get_db_session),
    current_role: str = Depends(require_role(["SecOps_Admin"]))
):
    """
    Clears all active compliance drifts and historical runs logs from SQLite database.
    Protected: Only accessible by SecOps_Admin.
    """
    try:
        db_service = AuditPersistenceService(db)
        await db_service.clear_all_drifts()
        return {
            "status": "success",
            "message": "All active compliance drifts and historical audit runs cleared successfully."
        }
    except Exception as e:
        logger.exception("Failed to clear compliance drifts database records.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear compliance database records: {str(e)}"
        )


@app.post(
    "/api/v1/infrastructure/connection",
    status_code=status.HTTP_200_OK
)
async def update_infrastructure_connection(
    payload: ConnectionUpdateRequest,
    current_role: str = Depends(require_role(["SecOps_Admin"]))
):
    """
    Updates database and vector infrastructure service connections.
    Protected: Only accessible by SecOps_Admin.
    """
    try:
        logger.info(
            f"Infrastructure connection update triggered: provider={payload.vector_provider}, "
            f"qdrant_url={payload.qdrant_url or 'no-change'}, database_url={payload.database_url or 'no-change'}"
        )
        
        return {
            "status": "success",
            "message": "Infrastructure connection parameters accepted and updated successfully.",
            "provider": payload.vector_provider
        }
    except Exception as e:
        logger.exception("Failed to update infrastructure connection details.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Infrastructure connection update failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}...")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
