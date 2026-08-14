from datetime import date

from database.models import Material, MaterialEvent


VALID_EVENT_TYPES = {
    "RECEIVED",
    "HANDOVER",
    "DAMAGE",
    "SHORTAGE",
}


def _next_material_id(session):
    """Generate the next MAT-000001 style Material ID."""

    materials = (
        session.query(Material)
        .filter(Material.material_id.like("MAT-%"))
        .all()
    )

    numbers = []

    for material in materials:
        try:
            numbers.append(int(material.material_id.split("-")[-1]))
        except (ValueError, AttributeError):
            continue

    next_number = max(numbers, default=0) + 1

    return f"MAT-{next_number:06d}"


def material_balance(session, material):
    """Calculate the current material balance from transaction events."""

    events = (
        session.query(MaterialEvent)
        .filter_by(material_id=material.id)
        .all()
    )

    received = sum(
        e.quantity
        for e in events
        if e.event_type == "RECEIVED"
    )

    handed_over = sum(
        e.quantity
        for e in events
        if e.event_type == "HANDOVER"
    )

    damaged = sum(
        e.quantity
        for e in events
        if e.event_type == "DAMAGE"
    )

    shortage = sum(
        e.quantity
        for e in events
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


def add_material(session, data):
    """
    Create a material and its initial RECEIVED transaction.

    material_id is optional. If omitted, MAT-000001 style numbering
    is generated automatically.
    """

    material_id = data.get("material_id")

    if not material_id:
        material_id = _next_material_id(session)

    existing = (
        session.query(Material)
        .filter_by(material_id=material_id)
        .first()
    )

    if existing:
        raise ValueError(
            f"Material ID {material_id} already exists."
        )

    quantity_received = float(
        data.get("quantity_received", 0) or 0
    )

    if quantity_received < 0:
        raise ValueError(
            "Received quantity cannot be negative."
        )

    material = Material(
        material_id=material_id,
        po_no=data["po_no"],
        item_code=data["item_code"],
        description=data["description"],
        quantity_received=quantity_received,
        receipt_date=data["receipt_date"],
        grn_no=data["grn_no"],
        store_location=data["store_location"],
        supplier=data["supplier"],
        remarks=data.get("remarks", ""),
    )

    session.add(material)
    session.flush()

    # Initial receipt is recorded as an event.
    if quantity_received > 0:
        event = MaterialEvent(
            material_id=material.id,
            event_date=data["receipt_date"],
            event_type="RECEIVED",
            quantity=quantity_received,
            party=data.get("supplier", ""),
            reference_no=data.get("grn_no", ""),
            remarks="Initial material receipt",
        )

        session.add(event)

    session.commit()
    session.refresh(material)

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
    """
    Add a material transaction.

    Prevents HANDOVER/DAMAGE/SHORTAGE from exceeding available stock.
    """

    event_type = event_type.strip().upper()

    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Invalid event type: {event_type}. "
            f"Allowed values: {', '.join(sorted(VALID_EVENT_TYPES))}"
        )

    quantity = float(quantity)

    if quantity <= 0:
        raise ValueError(
            "Transaction quantity must be greater than zero."
        )

    material = (
        session.query(Material)
        .filter_by(material_id=material_id.strip())
        .first()
    )

    if not material:
        raise ValueError(
            f"Material {material_id} not found."
        )

    balance = material_balance(session, material)

    if event_type == "RECEIVED":
        # A new receipt increases available stock.
        material.quantity_received = (
            float(material.quantity_received or 0)
            + quantity
        )

    else:
        available = balance["store"]

        if quantity > available:
            raise ValueError(
                f"Insufficient store balance for {material_id}. "
                f"Available: {available}, requested: {quantity}."
            )

    event = MaterialEvent(
        material_id=material.id,
        event_date=event_date,
        event_type=event_type,
        quantity=quantity,
        party=party or "",
        reference_no=reference_no or "",
        remarks=remarks or "",
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


def get_all_materials(session):
    return (
        session.query(Material)
        .order_by(
            Material.receipt_date.desc(),
            Material.id.desc()
        )
        .all()
    )