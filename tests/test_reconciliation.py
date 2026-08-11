from datetime import date
from database.db import Base, engine, SessionLocal
from database.models import Material
from services.material_service import add_material, add_event
from services.reconciliation import reconcile_all

def test_material_reconciles():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        m = add_material(session, {
            "po_no": "PO1", "item_code": "ITEM1", "description": "Test",
            "quantity_received": 100, "receipt_date": date.today(),
            "grn_no": "GRN1", "store_location": "S1", "supplier": "SUP1",
            "remarks": ""
        })
        add_event(session, m.material_id, date.today(), "HANDOVER", 30, "Contractor A")
        add_event(session, m.material_id, date.today(), "DAMAGE", 10)
        rows = reconcile_all(session)
        assert rows[0]["Store Balance"] == 60
        assert rows[0]["Status"] == "OK"
