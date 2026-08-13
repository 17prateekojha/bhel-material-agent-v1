from database.models import Material, MaterialEvent


def add_material(session, data):
    material_id = data.get("material_id")

    if not material_id:
        last_material = (
            session.query(Material)
            .order_by(Material.id.desc())
            .first()
        )

        if last_material and last_material.material_id:
            try:
                last_number = int(
                    last_material.material_id.split("-")[-1]
                )
                material_id = f"MAT-{last_number + 1:06d}"
            except (ValueError, IndexError):
                material_id = "MAT-000001"
        else:
            material_id = "MAT-000001"

    material = Material(
        material_id=material_id,
        po_no=data["po_no"],
        item_code=data["item_code"],
        description=data["description"],
        quantity_received=data.get("quantity_received", 0),
        receipt_date=data["receipt_date"],
        grn_no=data["grn_no"],
        store_location=data["store_location"],
        supplier=data["supplier"],
        remarks=data.get("remarks", ""),
    )

    session.add(material)
    session.flush()

    return material


def add_event(
    session,
    material_id,
    event_date,
    event_type,
    quantity,
    party="",
    reference_no="",
    remarks="",
):
    material = (
        session.query(Material)
        .filter(Material.material_id == material_id)
        .first()
    )

    if material is None:
        raise ValueError(
            f"Material {material_id} not found"
        )

    event = MaterialEvent(
        material_id=material.id,
        event_date=event_date,
        event_type=event_type,
        quantity=quantity,
        party=party,
        reference_no=reference_no,
        remarks=remarks,
    )

    session.add(event)
    session.flush()

    return event

def material_balance(session, material):
    events = (
        session.query(MaterialEvent)
        .filter_by(material_id=material.id)
        .all()
    )

    # Initial receipt comes from the Material master record.
    received = material.quantity_received or 0

    handed_over = sum(
        e.quantity for e in events
        if e.event_type == "HANDOVER"
    )

    damaged = sum(
        e.quantity for e in events
        if e.event_type == "DAMAGE"
    )

    shortage = sum(
        e.quantity for e in events
        if e.event_type == "SHORTAGE"
    )

    accounted = handed_over + damaged + shortage
    store = received - accounted
    difference = received - accounted

    return {
        "received": received,
        "handed_over": handed_over,
        "damaged": damaged,
        "shortage": shortage,
        "accounted": accounted,
        "store": store,
        "difference": difference,
    }


def get_all_materials(session):
    return (
        session.query(Material)
        .order_by(
            Material.receipt_date.desc(),
            Material.id.desc(),
        )
        .all()
    )