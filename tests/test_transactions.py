from datetime import date

import pytest

from database.db import Base, engine, SessionLocal
from services.material_service import (
    add_material,
    add_event,
    material_balance,
)


def test_transaction_balance():

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:

        material = add_material(
            session,
            {
                "po_no": "PO1",
                "item_code": "ITEM1",
                "description": "Test Material",
                "quantity_received": 100,
                "receipt_date": date.today(),
                "grn_no": "GRN1",
                "store_location": "S1",
                "supplier": "SUP1",
                "remarks": "",
            },
        )

        add_event(
            session,
            material.material_id,
            date.today(),
            "HANDOVER",
            30,
            "Contractor A",
        )

        add_event(
            session,
            material.material_id,
            date.today(),
            "DAMAGE",
            10,
        )

        balance = material_balance(
            session,
            material,
        )

        assert balance["received"] == 100
        assert balance["handed_over"] == 30
        assert balance["damaged"] == 10
        assert balance["shortage"] == 0
        assert balance["store"] == 60


def test_transaction_cannot_exceed_stock():

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:

        material = add_material(
            session,
            {
                "po_no": "PO2",
                "item_code": "ITEM2",
                "description": "Test Cable",
                "quantity_received": 50,
                "receipt_date": date.today(),
                "grn_no": "GRN2",
                "store_location": "S1",
                "supplier": "SUP2",
            },
        )

        with pytest.raises(ValueError):

            add_event(
                session,
                material.material_id,
                date.today(),
                "HANDOVER",
                51,
                "Contractor B",
            )


def test_material_id_is_generated():

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:

        material = add_material(
            session,
            {
                "po_no": "PO3",
                "item_code": "ITEM3",
                "description": "Generated ID Material",
                "quantity_received": 20,
                "receipt_date": date.today(),
                "grn_no": "GRN3",
                "store_location": "S1",
                "supplier": "SUP3",
            },
        )

        assert material.material_id.startswith("MAT-")
        assert len(material.material_id) == 10