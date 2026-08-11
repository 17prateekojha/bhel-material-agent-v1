from database.models import Material, MaterialEvent, InsuranceClaim, Survey
from services.material_service import material_balance

def reconcile_all(session):
    results = []
    for material in session.query(Material).all():
        b = material_balance(session, material)
        results.append({
            "Material ID": material.material_id,
            "PO No": material.po_no,
            "Item Code": material.item_code,
            "Description": material.description,
            "Received": b["received"],
            "Handed Over": b["handed_over"],
            "Damaged": b["damaged"],
            "Shortage": b["shortage"],
            "Store Balance": b["store"],
            "Difference": b["difference"],
            "Status": "OK" if b["store"] >= -0.000001 else "EXCEPTION",
        })
    return results

def exceptions(session):
    return [r for r in reconcile_all(session) if r["Status"] == "EXCEPTION"]
