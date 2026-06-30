import logging
from contextlib import asynccontextmanager
from typing import Dict, Literal, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Core Imports
from regudrift.config.settings import settings
from regudrift.core.agent.orchestrator import AgenticOrchestrationCarrier
from regudrift.core.agent.schemas import AgentStatePayload
from regudrift.core.retrieval.embedder import AsyncEmbeddingGenerator
from regudrift.core.ingestion.parser import DocumentParser
from regudrift.core.vector.faiss_service import LocalFAISSService
from regudrift.core.vector.qdrant_service import QdrantVectorService
from regudrift.core.vector.base import BaseVectorService, VectorServiceError

# Database Imports
from regudrift.core.database.session import engine, get_db_session
from regudrift.core.database.models import Base
from regudrift.core.database.service import AuditPersistenceService

# Configure structured logging formats
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("regudrift.api.main")


# Lifespan manager for database table generation and bootstrap
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Bootstrapping ReguDrift AI [{settings.ENV} mode]...")
    
    # 1. Asynchronously auto-generate database schema tables on startup
    logger.info("Initializing relational database schema tables...")
    try:
        async with engine.begin() as conn:
            # Recreates tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Asynchronous database tables initialized successfully!")
    except Exception as e:
        logger.critical(f"FATAL: Relational database schema generation failed: {e}")
        # Allow bootstrap to proceed but log the critical blocker

    # 2. Initialize Vector Service dependency based on active settings provider
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

    # 3. Initialize Embedder & Document Parser
    app.state.embedder = AsyncEmbeddingGenerator()
    app.state.parser = DocumentParser()

    yield
    
    # Teardown database connections on shutdown
    logger.info("Tearing down database connection pools...")
    await engine.dispose()
    logger.info("ReguDrift AI server resources cleanly closed.")


# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise Asynchronous AI Compliance and Relational Persistence Carrier",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input & Output Schemas
class RegulatoryUpdateRequest(BaseModel):
    update_text: str = Field(
        ...,
        description="The raw string content of the new regulatory update or compliance mandate."
    )


class IngestionResponse(BaseModel):
    document_id: str
    chunks_count: int
    relational_record_id: int = Field(..., description="Primary key record tracking ID in relational DB.")
    message: str


class AnalyzeResponse(BaseModel):
    relational_record_id: int = Field(..., description="Relational database AuditRun key record tracking ID.")
    telemetry: AgentStatePayload = Field(..., description="The state transition trace metadata payload.")


# Global Exception mapping
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
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingestion stream endpoint: parses uploaded internal policies, generates semantic legal chunks,
    extracts chapter/section hierarchies, computes embeddings, and indexes them.
    Saves a persistent DocumentRecord tracking coordinate history.
    """
    if not app.state.vector_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector service uninitialized or failing to connect."
        )

    try:
        content_bytes = await file.read()
        filename = file.filename or "policy.txt"
        
        # 1. Parse content according to file extensions
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

        # 2. Extract texts and generate embeddings asynchronously
        logger.info(f"Generating embeddings for {len(parsed_doc.chunks)} chunks...")
        chunk_contents = [c.content for c in parsed_doc.chunks]
        embeddings = await app.state.embedder.generate_embeddings(chunk_contents)

        # 3. Add to the active vector database
        logger.info("Indexing structured chunks into the vector store...")
        added_hashes = await app.state.vector_service.add_documents(
            chunks=parsed_doc.chunks,
            embeddings=embeddings
        )

        # 4. Save policy coordinate details to the relational database persistence layer
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
    db: AsyncSession = Depends(get_db_session)
):
    """
    Compliance Drift Assessment endpoint.
    Orchestrates the multi-stage Agentic loop using the modern Google GenAI SDK,
    programmatically searches internal policy vectors, and saves execution results
    to relational database tables as historical audit trails.
    """
    if not app.state.vector_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Compliance Vector Service is currently uninitialized."
        )

    try:
        # Instantiate dynamic Agentic Orchestration Carrier
        carrier = AgenticOrchestrationCarrier(
            vector_service=app.state.vector_service,
            embedder=app.state.embedder
        )
        
        # Execute the main transition audit loop
        final_state = await carrier.execute_analysis_loop(
            raw_regulatory_update=payload.update_text
        )

        # Ensure that if the final loop reached the synthesis phase, we save details
        if final_state.report:
            logger.info("Persisting drift audit execution run to SQL historical log...")
            db_service = AuditPersistenceService(db)
            audit_record = await db_service.persist_audit_run(
                raw_regulatory_update=payload.update_text,
                report=final_state.report
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


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}...")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
