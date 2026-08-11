from datetime import date
from sqlalchemy import select
from database.models import Material, MaterialEvent, InsuranceClaim, Survey

def next_material_id(session):
    count = session.query(Material).count() + 1
    candidate = f"MAT-{count:06d}"
    while session.query(Material).filter_by(material_id=candidate).first():
        count += 1
        candidate = f"MAT-{count:06d}"
    return candidate

def add_material(session, data):
    material = Material(
        material_id=next_material_id(session),
        po_no=data["po_no"].strip(),
        item_code=data["item_code"].strip(),
        description=data["description"].strip(),
        quantity_received=float(data["quantity_received"]),
        receipt_date=data["receipt_date"],
        grn_no=data["grn_no"].strip(),
        store_location=data["store_location"].strip(),
        supplier=data["supplier"].strip(),
        remarks=data.get("remarks", "").strip(),
    )
    session.add(material)
    session.flush()
    session.add(MaterialEvent(
        material_id=material.id,
        event_date=material.receipt_date,
        event_type="RECEIVED",
        quantity=material.quantity_received,
        party=material.supplier,
        reference_no=material.grn_no,
        remarks="Initial receipt",
    ))
    session.commit()
    session.refresh(material)
    return material

def add_event(session, material_id, event_date, event_type, quantity=0, party="", reference_no="", remarks=""):
    material = session.query(Material).filter_by(material_id=material_id).first()
    if not material:
        raise ValueError(f"Material {material_id} not found")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    event = MaterialEvent(
        material_id=material.id,
        event_date=event_date,
        event_type=event_type,
        quantity=float(quantity),
        party=party.strip(),
        reference_no=reference_no.strip(),
        remarks=remarks.strip(),
    )
    session.add(event)
    session.commit()
    return event

def material_balance(session, material):
    events = session.query(MaterialEvent).filter_by(material_id=material.id).all()
    received = sum(e.quantity for e in events if e.event_type == "RECEIVED")
    handed_over = sum(e.quantity for e in events if e.event_type == "HANDOVER")
    damaged = sum(e.quantity for e in events if e.event_type == "DAMAGE")
    shortage = sum(e.quantity for e in events if e.event_type == "SHORTAGE")
    return {
        "received": received,
        "handed_over": handed_over,
        "damaged": damaged,
        "shortage": shortage,
        "accounted": handed_over + damaged + shortage,
        "store": received - handed_over - damaged - shortage,
        "difference": received - handed_over - damaged - shortage,
    }

def get_all_materials(session):
    return session.query(Material).order_by(Material.receipt_date.desc(), Material.id.desc()).all()
