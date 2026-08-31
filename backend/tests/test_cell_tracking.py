def test_bulk_cell_intake_and_transfer(client, operator_token):
    # 1. Find Cell Part
    res_parts = client.get("/api/v1/parts")
    cell_part = next(p for p in res_parts.json["data"] if p["part_code"] == "CELL-21700")

    # 2. Bulk receive 100 cells using Range Generator
    res_bulk = client.post("/api/v1/stock/receive", headers={"Authorization": f"Bearer {operator_token}"}, json={
        "part_id": cell_part["_id"],
        "lot_batch_no": "CELL-BATCH-AUTO",
        "location_code": "E11-1A",
        "quantity": 100,
        "serial_range_prefix": "CELL-TEST-",
        "serial_range_start": 1,
        "serial_range_end": 100,
        "manufacturing_date": "2026-08-30",
        "date_code": "2630"
    })
    assert res_bulk.status_code == 201
    assert res_bulk.json["data"]["cell_count"] == 100

    # 3. Lookup specific cell serial
    res_cell = client.get("/api/v1/cells/serial/CELL-TEST-000001")
    assert res_cell.status_code == 200
    assert res_cell.json["data"]["cell"]["cell_serial_no"] == "CELL-TEST-000001"
    assert res_cell.json["data"]["cell"]["location"]["location_code"] == "E11-1A"

    # 4. Transfer exact cell to E11-2B
    res_trans = client.post("/api/v1/cells/transfer", headers={"Authorization": f"Bearer {operator_token}"}, json={
        "cell_serial_no": "CELL-TEST-000001",
        "to_location_code": "E11-2B",
        "reference_id": "TR-CELL-001"
    })
    assert res_trans.status_code == 200

    # 5. Check cell location and history
    res_after = client.get("/api/v1/cells/serial/CELL-TEST-000001")
    assert res_after.json["data"]["cell"]["location"]["location_code"] == "E11-2B"
    # History contains at least TRANSFER
    txns = res_after.json["data"]["history"]
    assert any(t["transaction_type"] == "TRANSFER" for t in txns)
