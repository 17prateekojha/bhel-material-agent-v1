from datetime import date, datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    Date,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.db import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    material_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True
    )

    po_no: Mapped[str] = mapped_column(String)
    item_code: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    quantity_received: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    receipt_date: Mapped[date] = mapped_column(Date)

    grn_no: Mapped[str] = mapped_column(String)
    store_location: Mapped[str] = mapped_column(String)
    supplier: Mapped[str] = mapped_column(String)

    remarks: Mapped[str] = mapped_column(
        String,
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    events: Mapped[list["MaterialEvent"]] = relationship(
        back_populates="material",
        cascade="all, delete-orphan"
    )


class MaterialEvent(Base):
    __tablename__ = "material_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id")
    )

    event_date: Mapped[date] = mapped_column(Date)

    event_type: Mapped[str] = mapped_column(String)

    quantity: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    party: Mapped[str] = mapped_column(
        String,
        default=""
    )

    reference_no: Mapped[str] = mapped_column(
        String,
        default=""
    )

    remarks: Mapped[str] = mapped_column(
        String,
        default=""
    )

    material: Mapped["Material"] = relationship(
        back_populates="events"
    )