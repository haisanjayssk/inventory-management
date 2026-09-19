def test_organizations_crud(client, admin_token):
    # 1. Get all organizations
    res = client.get("/api/v1/organizations", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert len(res.json["data"]) >= 1
    assert any(o["code"] == "ORG-001" for o in res.json["data"])

    # 2. Create new organization
    res_create = client.post("/api/v1/organizations", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "code": "ORG-TEST",
        "name": "Test Plant Facility",
        "country": "Germany",
        "site": [{"site_id": "SITE-GER-1", "site_name": "Berlin Plant"}],
        "status": "ACTIVE"
    })
    assert res_create.status_code == 201
    org_id = res_create.json["data"]["_id"]

    # 3. Update organization
    res_update = client.put(f"/api/v1/organizations/{org_id}", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "Updated Berlin Facility"
    })
    assert res_update.status_code == 200
    assert res_update.json["data"]["name"] == "Updated Berlin Facility"

def test_projects_crud(client, admin_token):
    # 1. List projects
    res = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert any(p["project_id"] == "PRJ-001" for p in res.json["data"])

    # 2. Create project
    res_create = client.post("/api/v1/projects", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "project_id": "PRJ-TEST-002",
        "project_desc": "High Voltage Pack Module Production",
        "responsible_person": "admin"
    })
    assert res_create.status_code == 201
    pid = res_create.json["data"]["_id"]

    # 3. Update project
    res_update = client.put(f"/api/v1/projects/{pid}", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "project_desc": "Updated HV Module Production Line"
    })
    assert res_update.status_code == 200
    assert res_update.json["data"]["project_desc"] == "Updated HV Module Production Line"

    # 4. Delete project
    res_del = client.delete(f"/api/v1/projects/{pid}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_del.status_code == 200

def test_items_and_item_types(client, admin_token):
    # 1. Create item type
    res_type = client.post("/api/v1/item-types", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "code": "RELAY",
        "name": "High Power Relay",
        "tracking_mode": "QUANTITY",
        "fields": [
            {"field_name": "Coil Voltage", "field_key": "coil_voltage", "data_type": "DECIMAL", "unit": "V", "required": True},
            {"field_name": "Contact Rating", "field_key": "contact_rating", "data_type": "DECIMAL", "unit": "A", "required": True}
        ]
    })
    assert res_type.status_code == 201
    it_id = res_type.json["data"]["_id"]

    # 2. Create item
    res_item = client.post("/api/v1/items", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "item_type_id": it_id,
        "code": "RELAY-12V-40A",
        "name": "12V 40A Automotive Relay",
        "description": "Sealed automotive SPST power relay",
        "attributes": {
            "coil_voltage": 12.0,
            "contact_rating": 40.0
        }
    })
    assert res_item.status_code == 201
    item_id = res_item.json["data"]["_id"]

    # 3. Query item
    res_get = client.get(f"/api/v1/items/{item_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_get.status_code == 200
    assert res_get.json["data"]["code"] == "RELAY-12V-40A"
    assert res_get.json["data"]["attributes"]["coil_voltage"] == 12.0

    # 4. Export items
    res_export = client.get("/api/v1/items/export?format=csv", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_export.status_code == 200
    assert "text/csv" in res_export.headers["Content-Type"]

def test_reports_and_unified_inventory(client, admin_token):
    # 1. Reports: stock by part/item
    res_report = client.get("/api/v1/reports/stock-by-part", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_report.status_code == 200
    assert len(res_report.json["data"]) >= 1

    # 2. Reports: location occupancy
    res_loc = client.get("/api/v1/reports/location-occupancy", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_loc.status_code == 200
    assert len(res_loc.json["data"]) >= 1

    # 3. Unified inventory query
    res_inv = client.get("/api/v1/inventory", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_inv.status_code == 200
    assert res_inv.json["data"]["total"] >= 1
