import logging
from typing import List, Optional
from sqlalchemy import select, text
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
        report: FinalReport,
        commit_hash: Optional[str] = None,
        author_name: Optional[str] = None,
        commit_timestamp: Optional[str] = None,
        branch_name: Optional[str] = None
    ) -> AuditRun:
        """
        Transactional routine converting the final compliance Agent analysis report
        into a relational log. Bulk-inserts sub-drift gaps dynamically mapping overall states.
        
        Args:
            raw_regulatory_update: Original regulatory raw update.
            report: The final validated Compliance FinalReport payload.
            commit_hash: Git commit hash context.
            author_name: Git commit author context.
            commit_timestamp: Git commit timestamp context.
            branch_name: Git branch name context.
            
        Returns:
            The persisted AuditRun model including loaded drifts.
        """
        try:
            statuses = [mapping.status.value for mapping in report.compliance_drift_matrix]
            if "Non-Compliant" in statuses:
                overall_status = "Non-Compliant"
            elif "Partial" in statuses:
                overall_status = "Partial"
            else:
                overall_status = "Compliant"

            total_critical = 0
            score = 100
            for blueprint in report.drift_remediation_blueprints:
                sev = blueprint.severity_rating.value.upper()
                if sev == "CRITICAL":
                    total_critical += 1
                    score -= 15
                elif sev == "HIGH":
                    total_critical += 1
                    score -= 10
                elif sev == "MEDIUM":
                    score -= 5
                elif sev == "LOW":
                    score -= 2

            score = max(0, min(100, score))

            audit_run = AuditRun(
                regulatory_update_text=raw_regulatory_update,
                executive_summary=report.executive_summary,
                overall_status=overall_status,
                timeline_weeks=report.remediation_timeline_weeks,
                commit_hash=commit_hash,
                author_name=author_name,
                commit_timestamp=commit_timestamp,
                branch_name=branch_name,
                global_health_score=score,
                total_critical_drifts=total_critical
            )
            self.db.add(audit_run)
            await self.db.flush()
            
            drifts = []
            for blueprint in report.drift_remediation_blueprints:
                drift = ComplianceDrift(
                    audit_run_id=audit_run.id,
                    clause_at_risk=blueprint.clause_at_risk,
                    severity_rating=blueprint.severity_rating.value,
                    clarity_score=blueprint.clarity_score,
                    technical_remediation_blueprint=blueprint.technical_remediation_blueprint,
                    commit_hash=commit_hash,
                    author_name=author_name,
                    commit_timestamp=commit_timestamp,
                    branch_name=branch_name
                )
                drifts.append(drift)
                
            self.db.add_all(drifts)
            await self.db.commit()
            
            await self.db.refresh(audit_run)
            logger.info(f"AuditRun persisted successfully! Record ID: {audit_run.id}")
            return audit_run
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to persist compliance AuditRun transaction: {e}")
            raise

    async def get_compliance_history(self) -> List[dict]:
        """
        Queries and aggregates compliance audit runs chronologically by date.
        Returns a time-series ready list of data tracking health and drifts.
        """
        try:
            if "postgresql" in settings.DATABASE_URL:
                query = text("""
                    SELECT 
                        to_char(timestamp, 'YYYY-MM-DD') AS audit_date,
                        AVG(global_health_score) AS avg_health_score,
                        SUM(total_critical_drifts) AS total_critical,
                        MAX(timestamp) AS latest_timestamp
                    FROM audit_runs
                    GROUP BY audit_date
                    ORDER BY audit_date ASC
                """)
            else:
                query = text("""
                    SELECT 
                        strftime('%Y-%m-%d', timestamp) AS audit_date,
                        AVG(global_health_score) AS avg_health_score,
                        SUM(total_critical_drifts) AS total_critical,
                        MAX(timestamp) AS latest_timestamp
                    FROM audit_runs
                    GROUP BY audit_date
                    ORDER BY audit_date ASC
                """)
            result = await self.db.execute(query)
            rows = result.fetchall()
            return [
                {
                    "date": row[0],
                    "global_health_score": round(row[1], 1) if row[1] is not None else 100.0,
                    "total_critical_drifts": int(row[2]) if row[2] is not None else 0,
                    "timestamp": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to fetch compliance history trend: {e}")
            raise

    async def clear_all_drifts(self) -> None:
        """
        Deletes all ComplianceDrift and AuditRun entries in the database to clear active drifts.
        """
        try:
            await self.db.execute(text("DELETE FROM compliance_drifts"))
            await self.db.execute(text("DELETE FROM audit_runs"))
            await self.db.commit()
            logger.info("Cleared all compliance drifts and audit runs successfully.")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to clear compliance drifts: {e}")
            raise
