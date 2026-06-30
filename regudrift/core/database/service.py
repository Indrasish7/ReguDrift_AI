import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from regudrift.core.agent.schemas import FinalReport
from regudrift.core.database.models import AuditRun, ComplianceDrift, DocumentRecord

logger = logging.getLogger("regudrift.database.service")


class AuditPersistenceService:
    """
    Asynchronous service managing relational database persistence for ReguDrift AI.
    Executes transaction boundaries to log policies and compliance analytical runs.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document_record(
        self,
        document_id: str,
        filename: str,
        storage_coordinates: str
    ) -> DocumentRecord:
        """
        Logs or overwrites an ingested company policy document track in the database.
        
        Args:
            document_id: Unique slug/identifier of the policy.
            filename: Original file name.
            storage_coordinates: Vector database coordinates (collection/path).
            
        Returns:
            The created or updated DocumentRecord ORM model.
        """
        try:
            # Query existing track
            query = select(DocumentRecord).where(DocumentRecord.document_id == document_id)
            result = await self.db.execute(query)
            existing_record = result.scalar_one_or_none()
            
            if existing_record:
                logger.info(f"Updating existing DocumentRecord document_id='{document_id}'")
                existing_record.filename = filename
                existing_record.storage_coordinates = storage_coordinates
                record = existing_record
            else:
                logger.info(f"Creating new DocumentRecord document_id='{document_id}'")
                record = DocumentRecord(
                    document_id=document_id,
                    filename=filename,
                    storage_coordinates=storage_coordinates
                )
                self.db.add(record)
                
            await self.db.commit()
            await self.db.refresh(record)
            return record
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save DocumentRecord '{document_id}': {e}")
            raise

    async def persist_audit_run(
        self,
        raw_regulatory_update: str,
        report: FinalReport
    ) -> AuditRun:
        """
        Transactional routine converting the final compliance Agent analysis report
        into a relational log. Bulk-inserts sub-drift gaps dynamically mapping overall states.
        
        Args:
            raw_regulatory_update: Original regulatory raw update.
            report: The final validated Compliance FinalReport payload.
            
        Returns:
            The persisted AuditRun model including loaded drifts.
        """
        try:
            # Dynamically resolve overall compliance status based on drift findings
            statuses = [mapping.status.value for mapping in report.compliance_drift_matrix]
            if "Non-Compliant" in statuses:
                overall_status = "Non-Compliant"
            elif "Partial" in statuses:
                overall_status = "Partial"
            else:
                overall_status = "Compliant"

            # 1. Instantiate and add parent AuditRun record
            audit_run = AuditRun(
                regulatory_update_text=raw_regulatory_update,
                executive_summary=report.executive_summary,
                overall_status=overall_status,
                timeline_weeks=report.remediation_timeline_weeks
            )
            self.db.add(audit_run)
            await self.db.flush()  # Flushes to DB to populate audit_run.id
            
            # 2. Iterate and associate child ComplianceDrift rows
            drifts = []
            for blueprint in report.drift_remediation_blueprints:
                drift = ComplianceDrift(
                    audit_run_id=audit_run.id,
                    clause_at_risk=blueprint.clause_at_risk,
                    severity_rating=blueprint.severity_rating.value,
                    clarity_score=blueprint.clarity_score,
                    technical_remediation_blueprint=blueprint.technical_remediation_blueprint
                )
                drifts.append(drift)
                
            self.db.add_all(drifts)
            await self.db.commit()
            
            # Refresh to load relationships cleanly
            await self.db.refresh(audit_run)
            logger.info(f"AuditRun persisted successfully! Record ID: {audit_run.id}")
            return audit_run
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to persist compliance AuditRun transaction: {e}")
            raise
