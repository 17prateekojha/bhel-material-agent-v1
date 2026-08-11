import streamlit as st
from datetime import date
from services.material_service import add_material

def render_material_entry(session):
    st.subheader("Daily Material Receipt")
    with st.form("material_entry"):
        c1,c2 = st.columns(2)
        po_no = c1.text_input("PO No *")
        item_code = c2.text_input("Item Code *")
        description = st.text_input("Material Description *")
        c1,c2,c3 = st.columns(3)
        qty = c1.number_input("Quantity *", min_value=0.0, step=1.0)
        receipt_date = c2.date_input("Receipt Date", value=date.today())
        grn_no = c3.text_input("GRN / Receipt No *")
        c1,c2 = st.columns(2)
        store = c1.text_input("Store Location *")
        supplier = c2.text_input("Supplier *")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Save Material", type="primary")

    if submitted:
        required = [po_no, item_code, description, grn_no, store, supplier]
        if not all(x.strip() for x in required):
            st.error("Please fill all mandatory fields.")
            return
        if qty <= 0:
            st.error("Quantity must be greater than zero.")
            return
        try:
            m = add_material(session, {
                "po_no": po_no, "item_code": item_code, "description": description,
                "quantity_received": qty, "receipt_date": receipt_date,
                "grn_no": grn_no, "store_location": store, "supplier": supplier,
                "remarks": remarks
            })
            st.success(f"Saved successfully: {m.material_id}")
        except Exception as exc:
            session.rollback()
            st.error(str(exc))
