from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base

class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    po_no: Mapped[str] = mapped_column(String(100), index=True)
    item_code: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text)
    quantity_received: Mapped[float] = mapped_column(Float, default=0)
    receipt_date: Mapped[date] = mapped_column(Date, index=True)
    grn_no: Mapped[str] = mapped_column(String(100), index=True)
    store_location: Mapped[str] = mapped_column(String(150))
    supplier: Mapped[str] = mapped_column(String(200))
    remarks: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("MaterialEvent", back_populates="material", cascade="all, delete-orphan")
    claims = relationship("InsuranceClaim", back_populates="material", cascade="all, delete-orphan")
    surveys = relationship("Survey", back_populates="material", cascade="all, delete-orphan")

class MaterialEvent(Base):
    __tablename__ = "material_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), index=True)
    event_date: Mapped[date] = mapped_column(Date, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0)
    party: Mapped[str] = mapped_column(String(200), default="")
    reference_no: Mapped[str] = mapped_column(String(100), default="")
    remarks: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="events")

class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), index=True)
    claim_required: Mapped[bool] = mapped_column(Boolean, default=True)
    claim_no: Mapped[str] = mapped_column(String(100), default="")
    claim_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    remarks: Mapped[str] = mapped_column(Text, default="")

    material = relationship("Material", back_populates="claims")

class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), index=True)
    survey_required: Mapped[bool] = mapped_column(Boolean, default=True)
    survey_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    surveyor: Mapped[str] = mapped_column(String(200), default="")
    report_no: Mapped[str] = mapped_column(String(100), default="")
    remarks: Mapped[str] = mapped_column(Text, default="")

    material = relationship("Material", back_populates="surveys")
