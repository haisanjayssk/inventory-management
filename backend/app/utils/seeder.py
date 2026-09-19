import logging
from datetime import datetime, timezone
from app.config.database import Database
from app.security.auth import hash_password
from app.services.location_service import LocationService

logger = logging.getLogger(__name__)

def seed_database():
    db = Database.get_db()
    if db is None:
        return

    logger.info("Checking database seed status...")
    now = datetime.now(timezone.utc).isoformat()
    org_id = "ORG-001"
    site_id = "SITE-001"

    # 1. Seed Organization
    if db.organizations.count_documents({}) == 0:
        logger.info("Seeding default organization...")
        db.organizations.insert_one({
            "_id": org_id,
            "code": org_id,
            "name": "EMS Manufacturing",
            "country": "India",
            "site": [
                {
                    "site_id": site_id,
                    "site_name": "Main Manufacturing Plant",
                    "location": "Chennai"
                }
            ],
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now
        })

    # 2. Seed Projects
    if db.projects.count_documents({}) == 0:
        logger.info("Seeding default projects...")
        db.projects.insert_one({
            "_id": "PRJ-001",
            "project_id": "PRJ-001",
            "project_desc": "EV Battery Pack Assembly Line 1",
            "responsible_person": "admin",
            "organization_id": org_id,
            "created_at": now,
            "updated_at": now
        })

    # 3. Seed Users
    if db.users.count_documents({}) == 0:
        logger.info("Seeding default users...")
        users = [
            {
                "_id": "USER-001",
                "organization_id": org_id,
                "site_id": site_id,
                "username": "admin",
                "email": "admin@mes.com",
                "name": "System Administrator",
                "full_name": "System Administrator",
                "password_hash": hash_password("Admin@123"),
                "role": "ADMIN",
                "status": "ACTIVE",
                "active": True,
                "created_at": now,
                "updated_at": now
            },
            {
                "_id": "USER-002",
                "organization_id": org_id,
                "site_id": site_id,
                "username": "manager",
                "email": "manager@mes.com",
                "name": "Inventory Manager",
                "full_name": "Inventory Manager",
                "password_hash": hash_password("Manager@123"),
                "role": "INVENTORY_MANAGER",
                "status": "ACTIVE",
                "active": True,
                "created_at": now,
                "updated_at": now
            },
            {
                "_id": "USER-003",
                "organization_id": org_id,
                "site_id": site_id,
                "username": "operator",
                "email": "operator@mes.com",
                "name": "Store Operator",
                "full_name": "Store Operator",
                "password_hash": hash_password("Operator@123"),
                "role": "STORE_OPERATOR",
                "status": "ACTIVE",
                "active": True,
                "created_at": now,
                "updated_at": now
            },
            {
                "_id": "USER-004",
                "organization_id": org_id,
                "site_id": site_id,
                "username": "viewer",
                "email": "viewer@mes.com",
                "name": "Audit & Quality Viewer",
                "full_name": "Audit & Quality Viewer",
                "password_hash": hash_password("Viewer@123"),
                "role": "VIEWER",
                "status": "ACTIVE",
                "active": True,
                "created_at": now,
                "updated_at": now
            }
        ]
        db.users.insert_many(users)

    # 4. Seed Item Types
    if db.item_types.count_documents({}) == 0:
        logger.info("Seeding standard item types and dynamic fields...")
        item_types_config = [
            {
                "id": "IT-001",
                "code": "RESISTOR",
                "name": "Resistor",
                "desc": "Surface mount & through-hole resistors",
                "tracking_mode": "QUANTITY",
                "fields": [
                    {"name": "Resistance", "key": "resistance", "type": "DECIMAL", "unit": "OHM", "required": True},
                    {"name": "Tolerance", "key": "tolerance", "type": "DECIMAL", "unit": "%", "required": True},
                    {"name": "Power Rating", "key": "power_rating", "type": "DECIMAL", "unit": "W", "required": True},
                    {"name": "Temperature Coeff", "key": "temp_coeff", "type": "STRING", "unit": "ppm/C", "required": False}
                ]
            },
            {
                "id": "IT-002",
                "code": "DIODE",
                "name": "Diode",
                "desc": "Schottky, Zener, Rectifier and TVS Diodes",
                "tracking_mode": "QUANTITY",
                "fields": [
                    {"name": "Forward Voltage", "key": "forward_voltage", "type": "DECIMAL", "unit": "V", "required": True},
                    {"name": "Forward Current", "key": "forward_current", "type": "DECIMAL", "unit": "mA", "required": True},
                    {"name": "Reverse Voltage", "key": "reverse_voltage", "type": "DECIMAL", "unit": "V", "required": True}
                ]
            },
            {
                "id": "IT-003",
                "code": "CAPACITOR",
                "name": "Capacitor",
                "desc": "Ceramic, Electrolytic and Tantalum Capacitors",
                "tracking_mode": "QUANTITY",
                "fields": [
                    {"name": "Capacitance", "key": "capacitance", "type": "DECIMAL", "unit": "uF", "required": True},
                    {"name": "Voltage Rating", "key": "voltage_rating", "type": "DECIMAL", "unit": "V", "required": True},
                    {"name": "Dielectric", "key": "dielectric", "type": "STRING", "unit": None, "required": False}
                ]
            },
            {
                "id": "IT-004",
                "code": "CELL",
                "name": "Battery Cell",
                "desc": "Cylindrical and Prismatic Lithium-Ion Battery Cells",
                "tracking_mode": "SERIAL",
                "fields": [
                    {"name": "Nominal Voltage", "key": "nominal_voltage", "type": "DECIMAL", "unit": "V", "required": True},
                    {"name": "Nominal Capacity", "key": "capacity", "type": "DECIMAL", "unit": "mAh", "required": True},
                    {"name": "Chemistry", "key": "chemistry", "type": "SELECT", "options": ["NMC", "LFP", "LTO", "NCA"], "required": True},
                    {"name": "Form Factor", "key": "form_factor", "type": "STRING", "unit": None, "required": True}
                ]
            },
            {
                "id": "IT-005",
                "code": "BUSBAR",
                "name": "Bus Bar",
                "desc": "High current electrical interconnect bus bars",
                "tracking_mode": "QUANTITY",
                "fields": [
                    {"name": "Material", "key": "material", "type": "SELECT", "options": ["Copper", "Aluminum", "Nickel Plated Copper"], "required": True},
                    {"name": "Length", "key": "length", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Width", "key": "width", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Thickness", "key": "thickness", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Current Rating", "key": "current_rating", "type": "DECIMAL", "unit": "A", "required": True}
                ]
            }
        ]

        for pt_cfg in item_types_config:
            doc = {
                "_id": pt_cfg["id"],
                "organization_id": org_id,
                "code": pt_cfg["code"],
                "name": pt_cfg["name"],
                "part_type_name": pt_cfg["name"],
                "description": pt_cfg["desc"],
                "tracking_mode": pt_cfg["tracking_mode"],
                "fields": pt_cfg["fields"],
                "site_id": site_id,
                "active": True,
                "created_at": now,
                "updated_at": now
            }
            db.item_types.insert_one(doc)

    # 5. Seed Vendors
    if db.vendors.count_documents({}) == 0:
        logger.info("Seeding sample vendors...")
        vendors = [
            {
                "_id": "VEN-001",
                "organization_id": org_id,
                "site_id": site_id,
                "code": "VEN-001",
                "name": "Yageo Electronics",
                "vendor_name": "Yageo Electronics",
                "types": ["MANUFACTURER", "SUPPLIER"],
                "contact": {"phone": "+91-44-28901234", "email": "sales@yageo.example.com"},
                "address": {"street": "Electronics City", "city": "Chennai", "country": "India"},
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now
            },
            {
                "_id": "VEN-002",
                "organization_id": org_id,
                "site_id": site_id,
                "code": "VEN-002",
                "name": "Samsung SDI",
                "vendor_name": "Samsung SDI",
                "types": ["MANUFACTURER"],
                "contact": {"phone": "+82-31-8008-1114", "email": "battery@samsung.example.com"},
                "address": {"street": "Yongin-si", "city": "Gyeonggi-do", "country": "South Korea"},
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now
            },
            {
                "_id": "VEN-003",
                "organization_id": org_id,
                "site_id": site_id,
                "code": "VEN-003",
                "name": "Wurth Elektronik",
                "vendor_name": "Wurth Elektronik",
                "types": ["MANUFACTURER", "DISTRIBUTOR"],
                "contact": {"phone": "+91-80-49120000", "email": "orders@we-online.example.com"},
                "address": {"street": "Whitefield", "city": "Bengaluru", "country": "India"},
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now
            }
        ]
        db.vendors.insert_many(vendors)

    # 6. Seed Warehouse Locations
    if db.locations.count_documents({}) == 0:
        logger.info("Seeding EMS Warehouse hierarchy locations...")
        loc_service = LocationService()
        loc_service.bulk_generate_locations({
            "warehouse_name": "EMS Warehouse",
            "warehouse_code": "E",
            "bays": ["1", "2"],
            "rows_count": 2,
            "racks_count": 2,
            "sections": ["A", "B", "C"]
        }, org_id=org_id, site_id=site_id)

    # 7. Seed Initial Items and Live Inventory
    if db.items.count_documents({}) == 0:
        logger.info("Seeding sample items and unified inventory...")
        pt_resistor = db.item_types.find_one({"code": "RESISTOR"}) or {"_id": "IT-001"}
        pt_cell = db.item_types.find_one({"code": "CELL"}) or {"_id": "IT-004"}
        pt_cap = db.item_types.find_one({"code": "CAPACITOR"}) or {"_id": "IT-003"}
        pt_busbar = db.item_types.find_one({"code": "BUSBAR"}) or {"_id": "IT-005"}

        v_yageo = db.vendors.find_one({"name": "Yageo Electronics"}) or {"_id": "VEN-001"}
        v_samsung = db.vendors.find_one({"name": "Samsung SDI"}) or {"_id": "VEN-002"}
        v_wurth = db.vendors.find_one({"name": "Wurth Elektronik"}) or {"_id": "VEN-003"}

        # Item 1: Resistor
        part_res_id = "ITEM-000001"
        item_res = {
            "_id": part_res_id,
            "organization_id": org_id,
            "site_id": site_id,
            "item_type_id": pt_resistor["_id"],
            "code": "RES-10K-0603",
            "name": "10K Ohm SMD Resistor 0603",
            "package": "0603",
            "vendor_id": v_yageo["_id"],
            "description": "10K resistor 1% 0.1W",
            "mfr": "Yageo",
            "mpn": "RC0603FR-0710KL",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_mode": "QUANTITY",
            "attributes": {
                "resistance": 10000,
                "tolerance": 1.0,
                "power_rating": 0.1
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        }
        db.items.insert_one(item_res)

        # Item 2: Battery Cell
        part_cell_id = "ITEM-000002"
        item_cell = {
            "_id": part_cell_id,
            "organization_id": org_id,
            "site_id": site_id,
            "item_type_id": pt_cell["_id"],
            "code": "CELL-21700",
            "name": "21700 5000mAh High Energy Li-Ion Cell",
            "package": "21700",
            "vendor_id": v_samsung["_id"],
            "description": "Cylindrical 50E 21700 battery cell",
            "mfr": "Samsung SDI",
            "mpn": "INR21700-50E",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_mode": "SERIAL",
            "attributes": {
                "nominal_voltage": 3.6,
                "capacity": 5000,
                "chemistry": "NMC",
                "form_factor": "21700"
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        }
        db.items.insert_one(item_cell)

        # Item 3: Capacitor
        part_cap_id = "ITEM-000003"
        item_cap = {
            "_id": part_cap_id,
            "organization_id": org_id,
            "site_id": site_id,
            "item_type_id": pt_cap["_id"],
            "code": "CAP-10UF-0805",
            "name": "10uF 25V X7R Ceramic Capacitor",
            "package": "0805",
            "vendor_id": v_wurth["_id"],
            "description": "Ceramic MLCC 10uF 25V",
            "mfr": "Wurth",
            "mpn": "885012207072",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_mode": "QUANTITY",
            "attributes": {
                "capacitance": 10.0,
                "voltage_rating": 25.0,
                "dielectric": "X7R"
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        }
        db.items.insert_one(item_cap)

        # Item 4: Bus Bar
        part_bus_id = "ITEM-000004"
        item_bus = {
            "_id": part_bus_id,
            "organization_id": org_id,
            "site_id": site_id,
            "item_type_id": pt_busbar["_id"],
            "code": "BB-CU-120A",
            "name": "Copper Bus Bar 120A 150mm",
            "package": "CUSTOM",
            "vendor_id": v_wurth["_id"],
            "description": "Solid electrolytic copper interconnect",
            "mfr": "Wurth",
            "mpn": "BB-CU-150-120A",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_mode": "QUANTITY",
            "attributes": {
                "material": "Copper",
                "length": 150.0,
                "width": 20.0,
                "thickness": 2.0,
                "current_rating": 120.0
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        }
        db.items.insert_one(item_bus)

        # Find locations
        loc_e11_1a = db.locations.find_one({"location_code": "E11-1A"}) or {"_id": "LOC-E11-1A"}
        loc_e11_2a = db.locations.find_one({"location_code": "E11-2A"}) or {"_id": "LOC-E11-2A"}

        # Inventory 1: 10,000 Resistors at E11-1A
        inv_res_id = "INV-000001"
        inv_res_doc = {
            "_id": inv_res_id,
            "organization_id": org_id,
            "site_id": site_id,
            "item_id": part_res_id,
            "lot_number": "YG20260831",
            "location_id": loc_e11_1a["_id"],
            "quantity": 10000,
            "available_quantity": 9500,
            "reserved_quantity": 500,
            "reserved_by": "admin",
            "reserved_for": "WO-1001",
            "vendor_id": v_yageo["_id"],
            "status": "AVAILABLE",
            "created_at": now,
            "updated_at": now
        }
        db.inventory.insert_one(inv_res_doc)

        # Receive Transaction for Resistors
        txn_res_id = "TXN-000001"
        txn_res = {
            "_id": txn_res_id,
            "t_id": txn_res_id,
            "organization_id": org_id,
            "item_id": part_res_id,
            "lot_number": "YG20260831",
            "transaction_type": "RECEIVE",
            "quantity": 10000,
            "from_location_id": None,
            "to_location_id": loc_e11_1a["_id"],
            "vendor_id": v_yageo["_id"],
            "performed_by": "admin",
            "reference": {"po_number": "PO-10001"},
            "timestamp": now,
            "remarks": "Initial material receipt of 10,000 resistors"
        }
        db.inventory_transactions.insert_one(txn_res)

        # Seed 50 Battery cells in Inventory
        cell_inv_docs = []
        for i in range(50):
            serial = f"CELL-2026-{str(i + 1).zfill(6)}"
            inv_id = f"INV-{str(i + 2).zfill(6)}"
            cell_inv_docs.append({
                "_id": inv_id,
                "organization_id": org_id,
                "site_id": site_id,
                "item_id": part_cell_id,
                "lot_number": "CELLLOT-001",
                "serial_number": serial,
                "location_id": loc_e11_2a["_id"],
                "quantity": 1,
                "available_quantity": 1,
                "reserved_quantity": 0,
                "vendor_id": v_samsung["_id"],
                "status": "AVAILABLE",
                "created_at": now,
                "updated_at": now
            })

        db.inventory.insert_many(cell_inv_docs)

        # Receive Transaction for Cells
        txn_cell_id = "TXN-000002"
        txn_cell = {
            "_id": txn_cell_id,
            "t_id": txn_cell_id,
            "organization_id": org_id,
            "item_id": part_cell_id,
            "lot_number": "CELLLOT-001",
            "transaction_type": "RECEIVE",
            "quantity": 50,
            "from_location_id": None,
            "to_location_id": loc_e11_2a["_id"],
            "vendor_id": v_samsung["_id"],
            "performed_by": "admin",
            "reference": {"po_number": "PO-10002"},
            "timestamp": now,
            "remarks": "Initial receipt of 50 cells (CELL-2026-000001 to CELL-2026-000050)"
        }
        db.inventory_transactions.insert_one(txn_cell)

    logger.info("Database seeding check completed successfully.")
