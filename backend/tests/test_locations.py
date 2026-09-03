def test_location_by_code_and_nfc(client):
    # Retrieve E11-1A
    res = client.get("/api/v1/locations/code/E11-1A")
    assert res.status_code == 200
    assert res.json["data"]["location_code"] == "E11-1A"

    # Retrieve by NFC payload
    res_nfc = client.get("/api/v1/locations/nfc/inventory://location/E11-1A")
    assert res_nfc.status_code == 200
    assert res_nfc.json["data"]["location_code"] == "E11-1A"

def test_bulk_location_generator(client, admin_token):
    res = client.post("/api/v1/locations/bulk-generate", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "warehouse_name": "Battery Pack Store",
        "warehouse_code": "BP",
        "bays": ["1", "2"],
        "rows_count": 2,
        "racks_count": 2,
        "sections": ["A", "B"]
    })
    assert res.status_code == 201
    # 2 bays * 2 rows * 2 racks * 2 sections = 16 locations
    assert res.json["data"]["generated_count"] == 16

def test_bulk_location_generator_without_sections(client, admin_token):
    res = client.post("/api/v1/locations/bulk-generate", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "warehouse_name": "Single Rack Store",
        "warehouse_code": "SR",
        "bays": ["1"],
        "rows_count": 3,
        "racks_count": 2,
        "sections": [] # No sections
    })
    assert res.status_code == 201
    # 1 bay * 3 rows * 2 racks * 1 = 6 locations
    assert res.json["data"]["generated_count"] == 6
    locs = res.json["data"]["locations"]
    assert any(l["location_code"] == "SR11-1" for l in locs)
    assert any(l["location_code"] == "SR13-2" for l in locs)

