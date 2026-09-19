import pytest

def test_full_indent_and_return_lifecycle(client, auth_headers):
    # 1. Fetch existing seeded part & location
    res_parts = client.get("/api/v1/parts", headers=auth_headers)
    assert res_parts.status_code == 200
    part = next(p for p in res_parts.json["data"] if p.get("part_code") == "RES-10K-0603")
    part_id = part["_id"]

    # Receive 100 units into E11-1A
    rcv_payload = {
        "part_id": part_id,
        "location_code": "E11-1A",
        "lot_batch_no": "IND-LOT-001",
        "quantity": 100,
        "remarks": "Initial stock for indent test"
    }
    r = client.post("/api/v1/stock/receive", json=rcv_payload, headers=auth_headers)
    assert r.status_code in [200, 201]

    # 2. Create Indent (Draft mode)
    draft_indent_payload = {
        "project_id": "PRJ-001",
        "project_head_id": "USER-001",
        "priority": "HIGH",
        "purpose": "Prototype build for MES battery pack",
        "status": "DRAFT",
        "items": [
            {
                "part_id": part_id,
                "requested_quantity": 25,
                "notes": "Precision resistors needed"
            }
        ]
    }
    r = client.post("/api/v1/indents", json=draft_indent_payload, headers=auth_headers)
    assert r.status_code == 201
    draft_indent = r.get_json()["data"]
    indent_id = draft_indent["_id"]
    assert draft_indent["status"] == "DRAFT"
    assert draft_indent["indent_number"].startswith("IND-")
    assert len(draft_indent["items"]) == 1

    # 3. Update Draft Indent
    update_payload = {
        "notes": "Updated urgent notes",
        "items": [
            {
                "part_id": part_id,
                "requested_quantity": 30,
                "notes": "Updated to 30 units"
            }
        ]
    }
    r = client.put(f"/api/v1/indents/{indent_id}", json=update_payload, headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["data"]["items"][0]["requested_quantity"] == 30

    # 4. Submit Draft Indent -> PENDING_APPROVAL
    r = client.post(f"/api/v1/indents/{indent_id}/submit", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["data"]["status"] == "PENDING_APPROVAL"

    # 5. List and filter Indents
    r = client.get("/api/v1/indents?status=PENDING_APPROVAL&project_id=PRJ-001", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["total"] >= 1

    # 6. Approve Indent
    approval_payload = {"comments": "Approved by Project Head for immediate dispatch"}
    r = client.post(f"/api/v1/indents/{indent_id}/approve", json=approval_payload, headers=auth_headers)
    assert r.status_code == 200
    approved_indent = r.get_json()["data"]
    assert approved_indent["status"] == "APPROVED"
    assert approved_indent["approval"]["comments"] == "Approved by Project Head for immediate dispatch"

    # 7. Partial Issue: Store issues 10 out of 30 units
    issue_payload_1 = {
        "items": [
            {
                "part_id": part_id,
                "location_code": "E11-1A",
                "lot_number": "IND-LOT-001",
                "issued_quantity": 10
            }
        ],
        "comments": "Partial batch 1"
    }
    r = client.post(f"/api/v1/indents/{indent_id}/issue", json=issue_payload_1, headers=auth_headers)
    assert r.status_code == 200
    partial_indent = r.get_json()["data"]
    assert partial_indent["status"] == "PARTIALLY_ISSUED"
    assert partial_indent["items"][0]["issued_quantity"] == 10

    # 8. Complete Issue: Store issues remaining 20 units
    issue_payload_2 = {
        "items": [
            {
                "part_id": part_id,
                "location_code": "E11-1A",
                "lot_number": "IND-LOT-001",
                "issued_quantity": 20
            }
        ],
        "comments": "Final batch 2"
    }
    r = client.post(f"/api/v1/indents/{indent_id}/issue", json=issue_payload_2, headers=auth_headers)
    assert r.status_code == 200
    full_indent = r.get_json()["data"]
    assert full_indent["status"] == "ISSUED"
    assert full_indent["items"][0]["issued_quantity"] == 30

    # 9. Create Material Return: Requester returns 5 unused good units
    return_payload = {
        "indent_id": indent_id,
        "items": [
            {
                "part_id": part_id,
                "returned_quantity": 5,
                "condition": "GOOD",
                "reason": "Unused surplus after assembly"
            }
        ],
        "reason": "Surplus material return"
    }
    r = client.post("/api/v1/indent-returns", json=return_payload, headers=auth_headers)
    assert r.status_code == 201
    ret_data = r.get_json()["data"]
    return_id = ret_data["_id"]
    assert ret_data["status"] == "PENDING_INSPECTION"
    assert ret_data["return_number"].startswith("RET-")

    # 10. Store incharge inspects & accepts the return into E11-1A
    accept_payload = {
        "status": "ACCEPTED",
        "inspection_notes": "All 5 resistors inspected and confirmed intact in original tape",
        "items": [
            {
                "part_id": part_id,
                "accepted_quantity": 5,
                "condition": "GOOD",
                "restock_location_code": "E11-1A",
                "lot_number": "IND-LOT-001"
            }
        ]
    }
    r = client.post(f"/api/v1/indent-returns/{return_id}/accept", json=accept_payload, headers=auth_headers)
    assert r.status_code == 200
    accepted_ret = r.get_json()["data"]
    assert accepted_ret["status"] == "ACCEPTED"

    # Verify indent item returned_quantity is updated to 5
    r = client.get(f"/api/v1/indents/{indent_id}", headers=auth_headers)
    assert r.status_code == 200
    updated_indent = r.get_json()["data"]
    assert updated_indent["items"][0]["returned_quantity"] == 5
    assert len(updated_indent["returns"]) >= 1

    # 11. Close Indent
    r = client.post(f"/api/v1/indents/{indent_id}/close", json={"notes": "Project work completed and closed"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["data"]["status"] == "CLOSED"

def test_indent_rejection_flow(client, auth_headers):
    res_parts = client.get("/api/v1/parts", headers=auth_headers)
    part = res_parts.json["data"][0]
    part_id = part["_id"]

    # Create an indent directly in PENDING_APPROVAL
    payload = {
        "project_id": "PRJ-001",
        "project_head_id": "USER-001",
        "purpose": "Rejected prototype test",
        "items": [
            {
                "part_id": part_id,
                "requested_quantity": 50
            }
        ]
    }
    r = client.post("/api/v1/indents", json=payload, headers=auth_headers)
    assert r.status_code == 201
    indent_id = r.get_json()["data"]["_id"]

    # Reject Indent
    reject_payload = {"reason": "Project budget exceeded for this month"}
    r = client.post(f"/api/v1/indents/{indent_id}/reject", json=reject_payload, headers=auth_headers)
    assert r.status_code == 200
    rejected = r.get_json()["data"]
    assert rejected["status"] == "REJECTED"
    assert rejected["rejection"]["reason"] == "Project budget exceeded for this month"

    # Ensure cannot issue stock for rejected indent
    issue_payload = {
        "items": [{"part_id": part_id, "location_code": "E11-1A", "issued_quantity": 10}]
    }
    r = client.post(f"/api/v1/indents/{indent_id}/issue", json=issue_payload, headers=auth_headers)
    assert r.status_code == 400
