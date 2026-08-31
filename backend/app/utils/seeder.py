import logging
from datetime import datetime, timezone
from app.config.database import Database
from app.models.counter import SequenceCounter
from app.security.auth import hash_password
from app.services.location_service import LocationService

logger = logging.getLogger(__name__)

def seed_database():
    db = Database.get_db()
    if db is None:
        return

    logger.info("Checking database seed status...")

    # 1. Seed Users
    if db.users.count_documents({}) == 0:
        logger.info("Seeding default users...")
        users = [
            {
                "_id": SequenceCounter.get_next_id("user"),
                "username": "admin",
                "email": "admin@mes.com",
                "full_name": "System Administrator",
                "password_hash": hash_password("Admin@123"),
                "role": "ADMIN",
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": SequenceCounter.get_next_id("user"),
                "username": "manager",
                "email": "manager@mes.com",
                "full_name": "Inventory Manager",
                "password_hash": hash_password("Manager@123"),
                "role": "INVENTORY_MANAGER",
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": SequenceCounter.get_next_id("user"),
                "username": "operator",
                "email": "operator@mes.com",
                "full_name": "Store Operator",
                "password_hash": hash_password("Operator@123"),
                "role": "STORE_OPERATOR",
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": SequenceCounter.get_next_id("user"),
                "username": "viewer",
                "email": "viewer@mes.com",
                "full_name": "Audit & Quality Viewer",
                "password_hash": hash_password("Viewer@123"),
                "role": "VIEWER",
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        db.users.insert_many(users)

    # 2. Seed Part Types & Dynamic Fields
    if db.part_types.count_documents({}) == 0:
        logger.info("Seeding standard part types and dynamic fields...")
        part_types_config = [
            {
                "name": "RESISTOR",
                "desc": "Surface mount & through-hole resistors",
                "fields": [
                    {"name": "Resistance", "key": "resistance", "type": "DECIMAL", "unit": "OHM", "required": True},
                    {"name": "Tolerance", "key": "tolerance", "type": "DECIMAL", "unit": "%", "required": True},
                    {"name": "Power Rating", "key": "power_rating", "type": "DECIMAL", "unit": "W", "required": True},
                    {"name": "Temperature Coeff", "key": "temp_coeff", "type": "STRING", "unit": "ppm/C", "required": False}
                ]
            },
            {
                "name": "DIODE",
                "desc": "Schottky, Zener, Rectifier and TVS Diodes",
                "fields": [
                    {"name": "Forward Voltage", "key": "forward_voltage", "type": "DECIMAL", "unit": "V", "required": True},
                    {"name": "Forward Current", "key": "forward_current", "type": "DECIMAL", "unit": "mA", "required": True},
                    {"name": "Reverse Voltage", "key": "reverse_voltage", "type": "DECIMAL", "unit": "V", "required": True}
                ]
            },
            {
                "name": "CAPACITOR",
                "desc": "Ceramic, Electrolytic and Tantalum Capacitors",
                "fields": [
                    {"name": "Capacitance", "key": "capacitance", "type": "DECIMAL", "unit": "uF", "required": True},
                    {"name": "Voltage Rating", "key": "voltage_rating", "type": "DECIMAL", "unit": "V", "required": True},
                    {"name": "Dielectric", "key": "dielectric", "type": "STRING", "unit": None, "required": False}
                ]
            },
            {
                "name": "CELL",
                "desc": "Cylindrical and Prismatic Lithium-Ion Battery Cells",
                "fields": [
                    {"name": "Nominal Voltage", "key": "nominal_voltage", "type": "DECIMAL", "unit": "V", "required": True},
                    {"name": "Nominal Capacity", "key": "capacity", "type": "DECIMAL", "unit": "mAh", "required": True},
                    {"name": "Chemistry", "key": "chemistry", "type": "SELECT", "options": ["NMC", "LFP", "LTO", "NCA"], "required": True},
                    {"name": "Form Factor", "key": "form_factor", "type": "STRING", "unit": None, "required": True}
                ]
            },
            {
                "name": "BUSBAR",
                "desc": "High current electrical interconnect bus bars",
                "fields": [
                    {"name": "Material", "key": "material", "type": "SELECT", "options": ["Copper", "Aluminum", "Nickel Plated Copper"], "required": True},
                    {"name": "Length", "key": "length", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Width", "key": "width", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Thickness", "key": "thickness", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Current Rating", "key": "current_rating", "type": "DECIMAL", "unit": "A", "required": True}
                ]
            },
            {
                "name": "CONNECTOR",
                "desc": "Wire-to-board and board-to-board connectors",
                "fields": [
                    {"name": "Pin Count", "key": "pin_count", "type": "NUMBER", "unit": None, "required": True},
                    {"name": "Pitch", "key": "pitch", "type": "DECIMAL", "unit": "mm", "required": True},
                    {"name": "Current Rating", "key": "current_rating", "type": "DECIMAL", "unit": "A", "required": False}
                ]
            },
            {
                "name": "IC",
                "desc": "Integrated circuits, microcontrollers, and drivers",
                "fields": [
                    {"name": "Package", "key": "package", "type": "STRING", "unit": None, "required": True},
                    {"name": "Pin Count", "key": "pin_count", "type": "NUMBER", "unit": None, "required": False},
                    {"name": "Supply Voltage", "key": "supply_voltage", "type": "DECIMAL", "unit": "V", "required": False}
                ]
            },
            {
                "name": "MECHANICAL",
                "desc": "Screws, brackets, enclosures, and structural parts",
                "fields": [
                    {"name": "Material", "key": "material", "type": "STRING", "unit": None, "required": False},
                    {"name": "Finish", "key": "finish", "type": "STRING", "unit": None, "required": False}
                ]
            }
        ]

        now = datetime.now(timezone.utc).isoformat()
        for pt_cfg in part_types_config:
            pt_id = SequenceCounter.get_next_id("part_type")
            db.part_types.insert_one({
                "_id": pt_id,
                "part_type_name": pt_cfg["name"],
                "description": pt_cfg["desc"],
                "created_by": "admin",
                "created_at": now,
                "updated_at": now
            })

            for f in pt_cfg["fields"]:
                db.part_type_fields.insert_one({
                    "_id": SequenceCounter.get_next_id("part_type_field"),
                    "part_type_id": pt_id,
                    "field_name": f["name"],
                    "field_key": f["key"],
                    "data_type": f["type"],
                    "unit": f.get("unit"),
                    "options": f.get("options", []),
                    "required": f.get("required", False),
                    "active": True,
                    "created_at": now,
                    "updated_at": now
                })

    # 3. Seed Vendors
    if db.vendors.count_documents({}) == 0:
        logger.info("Seeding sample vendors...")
        vendors = [
            {
                "_id": SequenceCounter.get_next_id("vendor"),
                "vendor_name": "Yageo Electronics",
                "contact": "+91-44-28901234",
                "email": "sales@yageo.example.com",
                "address": "Electronics City, Chennai",
                "country": "India",
                "status": "ACTIVE",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": SequenceCounter.get_next_id("vendor"),
                "vendor_name": "Samsung SDI",
                "contact": "+82-31-8008-1114",
                "email": "battery@samsung.example.com",
                "address": "Yongin-si, Gyeonggi-do",
                "country": "South Korea",
                "status": "ACTIVE",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": SequenceCounter.get_next_id("vendor"),
                "vendor_name": "Wurth Elektronik",
                "contact": "+91-80-49120000",
                "email": "orders@we-online.example.com",
                "address": "Whitefield, Bengaluru",
                "country": "India",
                "status": "ACTIVE",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        db.vendors.insert_many(vendors)

    # 4. Seed Warehouse Locations (EMS Structure)
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
        })

    # 5. Seed Initial Parts and Stock
    if db.parts.count_documents({}) == 0:
        logger.info("Seeding sample parts and inventory...")
        pt_resistor = db.part_types.find_one({"part_type_name": "RESISTOR"})
        pt_cell = db.part_types.find_one({"part_type_name": "CELL"})
        pt_cap = db.part_types.find_one({"part_type_name": "CAPACITOR"})
        pt_busbar = db.part_types.find_one({"part_type_name": "BUSBAR"})
        
        v_yageo = db.vendors.find_one({"vendor_name": "Yageo Electronics"})
        v_samsung = db.vendors.find_one({"vendor_name": "Samsung SDI"})
        v_wurth = db.vendors.find_one({"vendor_name": "Wurth Elektronik"})

        now = datetime.now(timezone.utc).isoformat()

        # Part 1: Resistor
        part_res_id = SequenceCounter.get_next_id("part")
        db.parts.insert_one({
            "_id": part_res_id,
            "part_type_id": pt_resistor["_id"],
            "part_code": "RES-10K-0603",
            "part_name": "10K Ohm SMD Resistor 0603",
            "package": "0603",
            "vendor_id": v_yageo["_id"],
            "description": "10K resistor 1% 0.1W",
            "mfr": "Yageo",
            "mpn": "RC0603FR-0710KL",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_type": "QUANTITY",
            "attributes": {
                "resistance": 10000,
                "tolerance": 1.0,
                "power_rating": 0.1
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        })

        # Part 2: Battery Cell
        part_cell_id = SequenceCounter.get_next_id("part")
        db.parts.insert_one({
            "_id": part_cell_id,
            "part_type_id": pt_cell["_id"],
            "part_code": "CELL-21700",
            "part_name": "21700 5000mAh High Energy Li-Ion Cell",
            "package": "21700",
            "vendor_id": v_samsung["_id"],
            "description": "Cylindrical 50E 21700 battery cell",
            "mfr": "Samsung SDI",
            "mpn": "INR21700-50E",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_type": "SERIAL",
            "attributes": {
                "nominal_voltage": 3.6,
                "capacity": 5000,
                "chemistry": "NMC",
                "form_factor": "21700"
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        })

        # Part 3: Capacitor
        part_cap_id = SequenceCounter.get_next_id("part")
        db.parts.insert_one({
            "_id": part_cap_id,
            "part_type_id": pt_cap["_id"],
            "part_code": "CAP-10UF-0805",
            "part_name": "10uF 25V X7R Ceramic Capacitor",
            "package": "0805",
            "vendor_id": v_wurth["_id"],
            "description": "Ceramic MLCC 10uF 25V",
            "mfr": "Wurth",
            "mpn": "885012207072",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_type": "QUANTITY",
            "attributes": {
                "capacitance": 10.0,
                "voltage_rating": 25.0,
                "dielectric": "X7R"
            },
            "active": True,
            "created_at": now,
            "updated_at": now
        })

        # Part 4: Bus Bar
        part_bus_id = SequenceCounter.get_next_id("part")
        db.parts.insert_one({
            "_id": part_bus_id,
            "part_type_id": pt_busbar["_id"],
            "part_code": "BB-CU-120A",
            "part_name": "Copper Bus Bar 120A 150mm",
            "package": "CUSTOM",
            "vendor_id": v_wurth["_id"],
            "description": "Solid electrolytic copper interconnect",
            "mfr": "Wurth",
            "mpn": "BB-CU-150-120A",
            "rohs": "YES",
            "static_sensitive": "NO",
            "msl": "NA",
            "unit_of_measure": "PCS",
            "tracking_type": "QUANTITY",
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
        })

        # Seed Sample Stock
        loc_e11_1a = db.locations.find_one({"location_code": "E11-1A"})
        loc_e11_1b = db.locations.find_one({"location_code": "E11-1B"})
        loc_e11_2a = db.locations.find_one({"location_code": "E11-2A"})

        # Lot 1: Resistor Lot
        lot_res_id = SequenceCounter.get_next_id("lot")
        db.lots.insert_one({
            "_id": lot_res_id,
            "part_id": part_res_id,
            "lot_batch_no": "YG20260831",
            "vendor_id": v_yageo["_id"],
            "manufacturing_date": "2026-08-01",
            "received_date": "2026-08-31",
            "created_at": now,
            "updated_at": now
        })

        # Inventory 1: 10,000 Resistors at E11-1A (500 reserved for WO-1001)
        inv_res_id = SequenceCounter.get_next_id("inventory")
        db.inventory.insert_one({
            "_id": inv_res_id,
            "part_id": part_res_id,
            "lot_id": lot_res_id,
            "location_id": loc_e11_1a["_id"],
            "quantity": 10000,
            "available_quantity": 9500,
            "reserved_quantity": 500,
            "reserved_by": "admin",
            "reserved_for": "WO-1001",
            "status": "AVAILABLE",
            "created_at": now,
            "updated_at": now
        })

        # Receive Transaction for Resistors
        db.transactions.insert_one({
            "_id": SequenceCounter.get_next_id("transaction"),
            "part_id": part_res_id,
            "lot_id": lot_res_id,
            "cell_id": None,
            "transaction_type": "RECEIVE",
            "quantity": 10000,
            "from_location_id": None,
            "to_location_id": loc_e11_1a["_id"],
            "user_id": "admin",
            "reference_id": "PO-10001",
            "timestamp": now,
            "description": "Initial material receipt of 10,000 resistors"
        })

        # Lot 2: Cell Lot
        lot_cell_id = SequenceCounter.get_next_id("lot")
        db.lots.insert_one({
            "_id": lot_cell_id,
            "part_id": part_cell_id,
            "lot_batch_no": "CELLLOT-001",
            "vendor_id": v_samsung["_id"],
            "manufacturing_date": "2026-08-20",
            "received_date": "2026-08-31",
            "created_at": now,
            "updated_at": now
        })

        # Seed 50 individual cells CELL-2026-000001 to CELL-2026-000050 at E11-2A
        cell_docs = []
        cinv_docs = []
        c_ids = SequenceCounter.get_next_batch_ids("cell", 50)
        cinv_ids = SequenceCounter.get_next_batch_ids("cell_inventory", 50)

        for i in range(50):
            serial = f"CELL-2026-{str(i + 1).zfill(6)}"
            cid = c_ids[i]
            cinv_id = cinv_ids[i]

            cell_docs.append({
                "_id": cid,
                "cell_serial_no": serial,
                "part_id": part_cell_id,
                "lot_id": lot_cell_id,
                "manufacturing_date": "2026-08-20",
                "date_code": "2620",
                "status": "AVAILABLE",
                "created_at": now,
                "updated_at": now
            })

            cinv_docs.append({
                "_id": cinv_id,
                "cell_id": cid,
                "location_id": loc_e11_2a["_id"],
                "status": "AVAILABLE",
                "stored_at": now,
                "updated_at": now
            })

        db.cells.insert_many(cell_docs)
        db.cell_inventory.insert_many(cinv_docs)

        # Receive Transaction for Cells
        db.transactions.insert_one({
            "_id": SequenceCounter.get_next_id("transaction"),
            "part_id": part_cell_id,
            "lot_id": lot_cell_id,
            "cell_id": None,
            "transaction_type": "RECEIVE",
            "quantity": 50,
            "from_location_id": None,
            "to_location_id": loc_e11_2a["_id"],
            "user_id": "admin",
            "reference_id": "PO-10002",
            "timestamp": now,
            "description": "Initial receipt of 50 cells (CELL-2026-000001 to CELL-2026-000050)"
        })

    logger.info("Database seeding check completed successfully.")
