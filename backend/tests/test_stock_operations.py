def test_receive_and_issue_and_transfer_resistors(client, operator_token):
    # 1. Receive Resistors into E11-1A
    res_parts = client.get("/api/v1/parts")
    res_part = next(p for p in res_parts.json["data"] if p["part_code"] == "RES-10K-0603")
    
    receive_res = client.post("/api/v1/stock/receive", headers={"Authorization": f"Bearer {operator_token}"}, json={
        "part_id": res_part["_id"],
        "lot_batch_no": "TEST-LOT-001",
        "location_code": "E11-1A",
        "quantity": 5000,
        "reference_id": "PO-TEST-01"
    })
    assert receive_res.status_code == 201
    lot_id = receive_res.json["data"]["lot_id"]

    # 2. Issue 1,000 PCS from E11-1A
    issue_res = client.post("/api/v1/stock/issue", headers={"Authorization": f"Bearer {operator_token}"}, json={
        "part_id": res_part["_id"],
        "lot_id": lot_id,
        "location_code": "E11-1A",
        "quantity": 1000,
        "reference_id": "WO-TEST-01"
    })
    assert issue_res.status_code == 200
    assert issue_res.json["data"]["remaining_quantity"] == 4000

    # 3. Transfer 2,000 PCS from E11-1A to E11-1B
    transfer_res = client.post("/api/v1/stock/transfer", headers={"Authorization": f"Bearer {operator_token}"}, json={
        "part_id": res_part["_id"],
        "lot_id": lot_id,
        "from_location_code": "E11-1A",
        "to_location_code": "E11-1B",
        "quantity": 2000,
        "reference_id": "TR-TEST-01"
    })
    assert transfer_res.status_code == 200
    assert transfer_res.json["data"]["quantity"] == 2000

    # 4. Attempt to over-issue -> Should fail with INSUFFICIENT_STOCK
    over_issue = client.post("/api/v1/stock/issue", headers={"Authorization": f"Bearer {operator_token}"}, json={
        "part_id": res_part["_id"],
        "lot_id": lot_id,
        "location_code": "E11-1A",
        "quantity": 99999
    })
    assert over_issue.status_code == 400
    assert "INSUFFICIENT_STOCK" in over_issue.json["message"]

def test_reserve_and_release_flow(client, admin_token):
    res_parts = client.get("/api/v1/parts")
    res_part = next(p for p in res_parts.json["data"] if p["part_code"] == "RES-10K-0603")
    
    # Receive 1000 items
    rec = client.post("/api/v1/stock/receive", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "part_id": res_part["_id"],
        "lot_batch_no": "RES-LOT-RESERVE",
        "location_code": "E11-2B",
        "quantity": 1000
    })
    lot_id = rec.json["data"]["lot_id"]

    # Reserve 400 for WO-999
    res_reserve = client.post("/api/v1/stock/reserve", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "part_id": res_part["_id"],
        "lot_id": lot_id,
        "location_id": rec.json["data"]["location_id"],
        "quantity": 400,
        "reserved_for": "WO-999"
    })
    assert res_reserve.status_code == 200
    assert res_reserve.json["data"]["reserved_quantity"] == 400

    # Release 150
    res_release = client.post("/api/v1/stock/release", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "part_id": res_part["_id"],
        "lot_id": lot_id,
        "location_id": rec.json["data"]["location_id"],
        "quantity": 150
    })
    assert res_release.status_code == 200
    assert res_release.json["data"]["remaining_reserved"] == 250
