import streamlit as st
from datetime import date

from sqlalchemy import or_

from agent.graph import ask_agent

from agent.tools import search_materials_received_today
from services.reconciliation import exceptions

from database.db import SessionLocal, init_db
from database.models import Material

# Initialize database before any database query
init_db()

from services.material_service import (
    add_material,
    add_event,
    material_balance,
)




# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BHEL Material Management",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# HEADER
# =========================================================

st.title("📦 BHEL Material Management Portal")

st.caption(
    "BHEL TBG HVDC Nagpur | Material Receipt, Store Balance, "
    "Handover & Reconciliation"
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "🤖 AI Assistant",
        "📊 Dashboard",
        "📦 Materials",
        "➕ Material Receipt",
        "🔄 Material Movement",
        "📅 Today's Receipts",
        "⚠️ Reconciliation",
    ],
)

st.sidebar.divider()

if st.sidebar.button("🔄 Refresh Application"):
    st.rerun()


# =========================================================
# AI ASSISTANT
# =========================================================

if page == "🤖 AI Assistant":

    st.header("🤖 Material Management AI Assistant")

    st.write(
        "Ask questions about materials, receipts, suppliers, "
        "POs, GRNs, store balances and reconciliation."
    )

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example: Show details for material MAT-000002."
        ),
        height=120,
    )

    if st.button("Ask Agent", type="primary"):

        if not question.strip():
            st.warning("Please enter a question.")

        else:

            with st.spinner("AI Agent is processing..."):

                try:

                    answer = ask_agent(question)

                    st.subheader("Answer")
                    st.write(answer)

                except Exception as exc:

                    st.error("Agent error")
                    st.exception(exc)


# =========================================================
# DASHBOARD
# =========================================================

elif page == "📊 Dashboard":

    st.header("📊 Material Management Dashboard")

    with SessionLocal() as session:

        materials = session.query(Material).all()

        total_materials = len(materials)

        total_received = 0
        total_handed_over = 0
        total_damaged = 0
        total_shortage = 0
        total_store = 0

        dashboard_rows = []

        for material in materials:

            balance = material_balance(
                session,
                material,
            )

            total_received += balance["received"]
            total_handed_over += balance["handed_over"]
            total_damaged += balance["damaged"]
            total_shortage += balance["shortage"]
            total_store += balance["store"]

            dashboard_rows.append(
                {
                    "Material ID": material.material_id,
                    "Description": material.description,
                    "Supplier": material.supplier,
                    "Received": balance["received"],
                    "Handed Over": balance["handed_over"],
                    "Damaged": balance["damaged"],
                    "Shortage": balance["shortage"],
                    "Store Balance": balance["store"],
                }
            )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Materials",
            total_materials,
        )

    with c2:
        st.metric(
            "Total Received",
            f"{total_received:,.2f}",
        )

    with c3:
        st.metric(
            "Current Store Balance",
            f"{total_store:,.2f}",
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        st.metric(
            "Total Handed Over",
            f"{total_handed_over:,.2f}",
        )

    with c5:
        st.metric(
            "Total Damaged",
            f"{total_damaged:,.2f}",
        )

    with c6:
        st.metric(
            "Total Shortage",
            f"{total_shortage:,.2f}",
        )

    st.divider()

    # -----------------------------------------------------
    # MATERIAL BALANCE
    # -----------------------------------------------------

    st.subheader("📦 Material-wise Store Balance")

    if dashboard_rows:

        st.dataframe(
            dashboard_rows,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No material records found.")

    st.divider()

    # -----------------------------------------------------
    # SUMMARY CHART
    # -----------------------------------------------------

    st.subheader("📊 Quantity Movement Summary")

    chart_data = {
        "Category": [
            "Received",
            "Handed Over",
            "Damaged",
            "Shortage",
            "Store Balance",
        ],
        "Quantity": [
            total_received,
            total_handed_over,
            total_damaged,
            total_shortage,
            total_store,
        ],
    }

    st.bar_chart(
        chart_data,
        x="Category",
        y="Quantity",
    )


# =========================================================
# MATERIAL REGISTER
# =========================================================

elif page == "📦 Materials":

    st.header("📦 Material Register")

    search = st.text_input(
        "🔍 Search Material ID / PO / Item Code / "
        "Description / Supplier"
    )

    with SessionLocal() as session:

        query = session.query(Material)

        if search.strip():

            value = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    Material.material_id.ilike(value),
                    Material.po_no.ilike(value),
                    Material.item_code.ilike(value),
                    Material.description.ilike(value),
                    Material.supplier.ilike(value),
                )
            )

        materials = (
            query
            .order_by(
                Material.receipt_date.desc(),
                Material.id.desc(),
            )
            .limit(500)
            .all()
        )

        rows = []

        for material in materials:

            balance = material_balance(
                session,
                material,
            )

            rows.append(
                {
                    "Material ID": material.material_id,
                    "PO": material.po_no,
                    "Item Code": material.item_code,
                    "Description": material.description,
                    "Supplier": material.supplier,
                    "Received": balance["received"],
                    "Handed Over": balance["handed_over"],
                    "Damaged": balance["damaged"],
                    "Shortage": balance["shortage"],
                    "Store Balance": balance["store"],
                    "Receipt Date": material.receipt_date,
                    "GRN": material.grn_no,
                    "Store": material.store_location,
                }
            )

    if rows:

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No materials found.")


# =========================================================
# MATERIAL RECEIPT
# =========================================================

elif page == "➕ Material Receipt":

    st.header("➕ Add Material Receipt")

    st.info(
        "Register a new material received at the Nagpur Store."
    )

    with st.form("material_receipt_form"):

        col1, col2 = st.columns(2)

        with col1:

            po_no = st.text_input("PO Number")

            item_code = st.text_input("Item Code")

            description = st.text_input("Description")

            quantity_received = st.number_input(
                "Received Quantity",
                min_value=0.0,
                step=1.0,
            )

            receipt_date = st.date_input(
                "Receipt Date",
                value=date.today(),
            )

        with col2:

            grn_no = st.text_input("GRN Number")

            store_location = st.text_input(
                "Store Location",
                value="Nagpur Store",
            )

            supplier = st.text_input("Supplier")

            remarks = st.text_area("Remarks")

        submitted = st.form_submit_button(
            "Create Material",
            type="primary",
        )

    if submitted:

        if not po_no or not description:

            st.warning(
                "PO Number and Description are required."
            )

        else:

            try:

                with SessionLocal() as session:

                    material = add_material(
                        session,
                        {
                            "po_no": po_no,
                            "item_code": item_code,
                            "description": description,
                            "quantity_received": quantity_received,
                            "receipt_date": receipt_date,
                            "grn_no": grn_no,
                            "store_location": store_location,
                            "supplier": supplier,
                            "remarks": remarks,
                        },
                    )

                    # Create RECEIVED event
                    add_event(
                        session,
                        material.material_id,
                        receipt_date,
                        "RECEIVED",
                        quantity_received,
                        supplier,
                        grn_no,
                        remarks,
                    )

                    session.commit()

                    st.success(
                        f"Material {material.material_id} "
                        "created successfully."
                    )

                    st.info(
                        f"Material ID: {material.material_id}"
                    )

            except Exception as exc:

                st.error("Unable to create material.")
                st.exception(exc)


# =========================================================
# MATERIAL MOVEMENT
# =========================================================

elif page == "🔄 Material Movement":

    st.header("🔄 Material Movement")

    st.write(
        "Record material handover, damage or shortage."
    )

    with SessionLocal() as session:

        materials = (
            session.query(Material)
            .order_by(Material.material_id)
            .all()
        )

        material_options = {
            m.material_id: m
            for m in materials
        }

    if not material_options:

        st.info("No materials available.")

    else:

        selected_id = st.selectbox(
            "Material ID",
            list(material_options.keys()),
        )

        selected_material = material_options[
            selected_id
        ]

        with SessionLocal() as session:

            db_material = (
                session.query(Material)
                .filter_by(
                    material_id=selected_id
                )
                .first()
            )

            balance = material_balance(
                session,
                db_material,
            )

        st.info(
            f"Current Store Balance: "
            f"{balance['store']:,.2f}"
        )

        with st.form("movement_form"):

            event_type = st.selectbox(
                "Movement Type",
                [
                    "HANDOVER",
                    "DAMAGE",
                    "SHORTAGE",
                ],
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                step=1.0,
            )

            party = st.text_input(
                "Party / Contractor"
            )

            reference_no = st.text_input(
                "Reference Number"
            )

            remarks = st.text_area(
                "Remarks"
            )

            submitted = st.form_submit_button(
                "Record Movement",
                type="primary",
            )

        if submitted:

            if quantity <= 0:

                st.warning(
                    "Quantity must be greater than zero."
                )

            elif quantity > balance["store"]:

                st.error(
                    f"Quantity exceeds available store balance "
                    f"({balance['store']:,.2f})."
                )

            else:

                try:

                    with SessionLocal() as session:

                        add_event(
                            session,
                            selected_id,
                            date.today(),
                            event_type,
                            quantity,
                            party,
                            reference_no,
                            remarks,
                        )

                        session.commit()

                    st.success(
                        f"{event_type} event recorded successfully."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        "Unable to record material movement."
                    )

                    st.exception(exc)


# =========================================================
# TODAY'S RECEIPTS
# =========================================================

elif page == "📅 Today's Receipts":

    st.header("📅 Materials Received Today")

    st.caption(
        f"Receipt Date: {date.today()}"
    )

    try:

        result = (
            search_materials_received_today
            .invoke({})
        )

        if result.startswith("No materials"):

            st.info(result)

        else:

            st.text(result)

    except Exception as exc:

        st.error(
            "Unable to retrieve today's receipts."
        )

        st.exception(exc)

# ---------------------------------------------------------
# TRANSACTIONS
# ---------------------------------------------------------

elif page == "🔄 Transactions":

    st.header("🔄 Material Transaction Management")

    st.caption(
        "Record material handover, damage, shortage, or additional receipt."
    )

    with SessionLocal() as session:

        materials = (
            session.query(Material)
            .order_by(Material.material_id)
            .all()
        )

        if not materials:

            st.info(
                "No materials are available. "
                "Please add a material first."
            )

        else:

            material_options = {
                m.material_id: m
                for m in materials
            }

            selected_material_id = st.selectbox(
                "Material ID",
                options=list(material_options.keys()),
            )

            material = material_options[selected_material_id]

            balance = material_balance(
                session,
                material,
            )

            st.subheader("Current Balance")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Received",
                    balance["received"],
                )

            with col2:
                st.metric(
                    "Handed Over",
                    balance["handed_over"],
                )

            with col3:
                st.metric(
                    "Damaged",
                    balance["damaged"],
                )

            with col4:
                st.metric(
                    "Store Balance",
                    balance["store"],
                )

            st.divider()

            st.subheader("Record Transaction")

            event_type = st.selectbox(
                "Transaction Type",
                [
                    "HANDOVER",
                    "DAMAGE",
                    "SHORTAGE",
                    "RECEIVED",
                ],
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0.01,
                value=1.0,
                step=1.0,
            )

            event_date = st.date_input(
                "Transaction Date",
                value=date.today(),
            )

            party = st.text_input(
                "Party / Contractor / Recipient"
            )

            reference_no = st.text_input(
                "Reference No."
            )

            remarks = st.text_area(
                "Remarks"
            )

            available = balance["store"]

            if event_type != "RECEIVED":

                st.info(
                    f"Available store balance: {available}"
                )

                if quantity > available:

                    st.error(
                        f"Quantity exceeds available balance "
                        f"({available})."
                    )

            if st.button(
                "Save Transaction",
                type="primary",
                use_container_width=True,
            ):

                try:

                    event = add_event(
                        session=session,
                        material_id=selected_material_id,
                        event_date=event_date,
                        event_type=event_type,
                        quantity=quantity,
                        party=party,
                        reference_no=reference_no,
                        remarks=remarks,
                    )

                    st.success(
                        f"{event_type} transaction of "
                        f"{quantity} recorded successfully."
                    )

                    st.rerun()

                except ValueError as exc:

                    st.error(str(exc))

                except Exception as exc:

                    session.rollback()

                    st.error(
                        "Unable to save transaction."
                    )

                    st.exception(exc)

            st.divider()

            st.subheader("Transaction History")

            events = (
                session.query(MaterialEvent)
                .filter(
                    MaterialEvent.material_id == material.id
                )
                .order_by(
                    MaterialEvent.event_date.desc(),
                    MaterialEvent.id.desc(),
                )
                .all()
            )

            if events:

                transaction_data = [
                    {
                        "Date": e.event_date,
                        "Type": e.event_type,
                        "Quantity": e.quantity,
                        "Party": e.party,
                        "Reference": e.reference_no,
                        "Remarks": e.remarks,
                    }
                    for e in events
                ]

                st.dataframe(
                    transaction_data,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No transactions recorded."
                )
# =========================================================
# RECONCILIATION
# =========================================================

elif page == "⚠️ Reconciliation":

    st.header("⚠️ Reconciliation Exceptions")

    try:
        with SessionLocal() as session:
            rows = exceptions(session)

        if not rows:
            st.success("No reconciliation exceptions found.")
        else:
            st.error(f"{len(rows)} reconciliation exception(s) found.")

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

    except Exception as e:
        st.error("Unable to retrieve reconciliation data.")
        st.exception(e)