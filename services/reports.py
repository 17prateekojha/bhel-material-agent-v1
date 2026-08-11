from pathlib import Path
import pandas as pd
from database.models import Material, MaterialEvent, InsuranceClaim, Survey
from services.material_service import material_balance

EXPORT_DIR = Path(__file__).resolve().parents[1] / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

def register_df(session):
    rows = []
    for m in session.query(Material).order_by(Material.receipt_date.desc()).all():
        b = material_balance(session, m)
        rows.append({
            "Material ID": m.material_id, "PO No": m.po_no, "Item Code": m.item_code,
            "Description": m.description, "Qty Received": m.quantity_received,
            "Receipt Date": m.receipt_date, "GRN No": m.grn_no,
            "Store": m.store_location, "Supplier": m.supplier,
            "Handed Over": b["handed_over"], "Damaged": b["damaged"],
            "Shortage": b["shortage"], "Store Balance": b["store"],
            "Remarks": m.remarks
        })
    return pd.DataFrame(rows)

def events_df(session):
    rows = []
    for e in session.query(MaterialEvent).order_by(MaterialEvent.event_date.desc()).all():
        rows.append({
            "Date": e.event_date, "Material ID": e.material.material_id,
            "PO No": e.material.po_no, "Item Code": e.material.item_code,
            "Description": e.material.description, "Event": e.event_type,
            "Quantity": e.quantity, "Party": e.party,
            "Reference No": e.reference_no, "Remarks": e.remarks
        })
    return pd.DataFrame(rows)

def claims_df(session):
    rows = []
    for c in session.query(InsuranceClaim).all():
        rows.append({
            "Material ID": c.material.material_id, "PO No": c.material.po_no,
            "Description": c.material.description, "Claim Required": c.claim_required,
            "Claim No": c.claim_no, "Claim Date": c.claim_date,
            "Status": c.status, "Remarks": c.remarks
        })
    return pd.DataFrame(rows)

def surveys_df(session):
    rows = []
    for s in session.query(Survey).all():
        rows.append({
            "Material ID": s.material.material_id, "PO No": s.material.po_no,
            "Description": s.material.description, "Survey Required": s.survey_required,
            "Survey Date": s.survey_date, "Status": s.status,
            "Surveyor": s.surveyor, "Report No": s.report_no, "Remarks": s.remarks
        })
    return pd.DataFrame(rows)

def create_workbook(session):
    path = EXPORT_DIR / "BHEL_HVDC_Nagpur_Material_Report.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        register_df(session).to_excel(writer, sheet_name="Material Register", index=False)
        events_df(session).to_excel(writer, sheet_name="Material Events", index=False)
        claims_df(session).to_excel(writer, sheet_name="Insurance Claims", index=False)
        surveys_df(session).to_excel(writer, sheet_name="Survey Status", index=False)
    return path
