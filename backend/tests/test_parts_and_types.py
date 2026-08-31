def test_part_types_list(client):
    res = client.get("/api/v1/part-types")
    assert res.status_code == 200
    types = [pt["part_type_name"] for pt in res.json["data"]]
    assert "RESISTOR" in types
    assert "CELL" in types

def test_create_dynamic_part_type_and_part(client, admin_token):
    # 1. Create a custom part type "FUSE"
    res = client.post("/api/v1/part-types", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "part_type_name": "FUSE",
        "description": "Protection fuses",
        "fields": [
            {"field_name": "Current Rating", "field_key": "current_rating", "data_type": "DECIMAL", "unit": "A", "required": True},
            {"field_name": "Blow Speed", "field_key": "blow_speed", "data_type": "STRING", "unit": None, "required": False}
        ]
    })
    assert res.status_code == 201
    pt_id = res.json["data"]["_id"]

    # 2. Try creating part without required dynamic attribute -> Should fail
    res_fail = client.post("/api/v1/parts", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "part_type_id": pt_id,
        "part_code": "FUSE-10A-SMD",
        "part_name": "10A Fast Acting Fuse",
        "tracking_type": "QUANTITY",
        "attributes": {}
    })
    assert res_fail.status_code == 400

    # 3. Create with required attribute -> Should succeed
    res_ok = client.post("/api/v1/parts", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "part_type_id": pt_id,
        "part_code": "FUSE-10A-SMD",
        "part_name": "10A Fast Acting Fuse",
        "tracking_type": "QUANTITY",
        "attributes": {
            "current_rating": 10.0,
            "blow_speed": "FAST"
        }
    })
    assert res_ok.status_code == 201
    assert res_ok.json["data"]["part_code"] == "FUSE-10A-SMD"
