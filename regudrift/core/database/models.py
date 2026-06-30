from datetime import datetime
from typing import List
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    SQLAlchemy unified ORM declarative base class.
    """
    pass


class DocumentRecord(Base):
    """
    ORM Model tracking internal ingested policies, filenames, 
    and vector database storage coordinates.
    """
    __tablename__ = "document_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_coordinates: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<DocumentRecord id={self.id} doc_id='{self.document_id}' filename='{self.filename}'>"


class AuditRun(Base):
    """
    ORM Model logging historical regulatory drift analysis loop tasks, 
    consolidated metadata, and executive summaries.
    """
    __tablename__ = "audit_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    regulatory_update_text: Mapped[str] = mapped_column(Text, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    overall_status: Mapped[str] = mapped_column(String(50), nullable=False)
    timeline_weeks: Mapped[int] = mapped_column(Integer, nullable=False)

    # Core relationship cascading down to individual compliance drift gaps
    drifts: Mapped[List["ComplianceDrift"]] = relationship(
        "ComplianceDrift",
        back_populates="audit_run",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AuditRun id={self.id} status='{self.overall_status}' timeline={self.timeline_weeks}w>"


class ComplianceDrift(Base):
    """
    ORM Model housing granular regulatory gaps, threat severity scales, 
    and exact engineering remediation instructions.
    """
    __tablename__ = "compliance_drifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("audit_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    clause_at_risk: Mapped[str] = mapped_column(Text, nullable=False)
    severity_rating: Mapped[str] = mapped_column(String(20), nullable=False)
    clarity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    technical_remediation_blueprint: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Direct relational link to parent AuditRun
    audit_run: Mapped["AuditRun"] = relationship("AuditRun", back_populates="drifts")

    def __repr__(self) -> str:
        return f"<ComplianceDrift id={self.id} run_id={self.audit_run_id} severity='{self.severity_rating}'>"
