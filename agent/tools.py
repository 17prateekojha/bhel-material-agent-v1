from langchain_core.tools import tool
from database.db import SessionLocal
from services.material_service import material_balance
from services.reconciliation import reconcile_all

@tool
def search_material(material_id: str) -> str:
    """Find a material by Material ID and return its current balance."""
    from database.models import Material
    with SessionLocal() as session:
        m = session.query(Material).filter_by(material_id=material_id.strip()).first()
        if not m:
            return f"No material found for {material_id}."
        b = material_balance(session, m)
        return (
            f"{m.material_id}: PO={m.po_no}, Item={m.item_code}, "
            f"Description={m.description}, Received={b['received']}, "
            f"Handed Over={b['handed_over']}, Damaged={b['damaged']}, "
            f"Shortage={b['shortage']}, Store Balance={b['store']}."
        )

@tool
def find_reconciliation_exceptions() -> str:
    """Find all material reconciliation exceptions."""
    with SessionLocal() as session:
        rows = [r for r in reconcile_all(session) if r["Status"] == "EXCEPTION"]
        if not rows:
            return "No reconciliation exceptions found."
        return "\n".join(
            f"{r['Material ID']} | received={r['Received']} | "
            f"handed_over={r['Handed Over']} | damaged={r['Damaged']} | "
            f"shortage={r['Shortage']} | difference={r['Difference']}"
            for r in rows
        )

@tool
def search_by_description(keyword: str) -> str:
    """Search materials by description, item code, PO number, or supplier."""
    from sqlalchemy import or_
    from database.models import Material
    with SessionLocal() as session:
        like = f"%{keyword.strip()}%"
        rows = session.query(Material).filter(
            or_(
                Material.description.ilike(like),
                Material.item_code.ilike(like),
                Material.po_no.ilike(like),
                Material.supplier.ilike(like),
            )
        ).limit(50).all()
        if not rows:
            return "No matching materials found."
        return "\n".join(
            f"{m.material_id} | PO={m.po_no} | Item={m.item_code} | "
            f"{m.description} | Supplier={m.supplier}"
            for m in rows
        )
@tool
def search_materials_received_today() -> str:
    """Find all materials whose receipt date is today."""
    from datetime import date
    from database.models import Material

    today = date.today()

    with SessionLocal() as session:
        rows = (
            session.query(Material)
            .filter(Material.receipt_date == today)
            .order_by(Material.receipt_date, Material.material_id)
            .limit(100)
            .all()
        )

        if not rows:
            return f"No materials were received on {today}."

        return "\n".join(
            f"{m.material_id} | PO={m.po_no} | Item={m.item_code} | "
            f"{m.description} | Supplier={m.supplier} | "
            f"Received Qty={m.quantity_received} | "
            f"Receipt Date={m.receipt_date} | GRN={m.grn_no}"
            for m in rows
        )