# Inventory Management Application — Development Specification

## 1. Objective

Build a production-ready Inventory Management Web Application that should supports an all devices like Android, Windows, POS devices, etc., for an electronics and battery manufacturing environment.

The application must manage:

- Resistors, diodes, capacitors, ICs, connectors and other electronic components
- Battery cells, Bus bars and mechanical/electrical components
- Vendors Details
- Lots / batches
- Individual cell serial-number tracking
- Warehouse locations
- Current inventory
- Stock reservations
- Receive / issue / transfer operations
- NFC-based location identification
- Transaction and audit history
- Search and traceability

The design must be ready for future MES integration.

---

## 2. Tracking Model

There are two inventory tracking models.

### Quantity-tracked parts

Examples:

- Resistor
- Diode
- Capacitor
- Connector
- Bus bar
- Screw
- Other bulk components

Flow:

`Part -> Lot -> Inventory -> Location -> Quantity`

### Individually tracked cells

Every physical cell must have a unique serial number.

Example:

```text
CELL-2026-000001
CELL-2026-000002
CELL-2026-000003
```

Flow:

`Part -> Lot -> Cell -> Cell Inventory -> Current Location -> Process/Transaction History`

The system must always be able to identify an exact cell.

---

## 3. Warehouse Structure

Initial physical structure:

```text
N number of Warehouses
  |
  +-- n number of Racks per Warehouse
        |
        +-- n number of Boxes per Rack
```

Total locations:


Each physical box/location has an NFC tag.

Example:
Storage structure format for EMS
E11-1A
E—----Warehouse name(EMS,MAIN,CELL) So if user add a new warehouse like MES it should verify if M already exist and take first 2 letters like ME
1—----Bay number(1,2,3,4,5,6,7,8,9)(A to Z)alphaNumerical
1—----row number(1,2,3,4,5)
1—---- rack number(1,2,3,4,5) 1 to 5 
A—-----each row divided into 3 section (A to C)

The web app must identify the physical location by NFC rather than requiring the operator to manually type warehouse/rack/box information.

The backend is the source of truth for the location hierarchy.

---

## 4. NFC Location Workflow

### Receive / Put-Away

1. Operator scans the NFC tag attached to the destination box.
2. The NFC reader obtains the location identifier.
3. Frontend sends the identifier to the backend.
5. Backend resolves and validates the location.
6. Frontend displays:

```text
Warehouse: E
Bay: 1
Row: 1
Rack: 1
Section: A
Location: E11-1A
Status: ACTIVE
```

7. Operator confirms.
8. Backend updates inventory.
9. Backend creates an immutable transaction record.

### Transfer

1. Scan source NFC.
2. Select/scan material.
3. Enter quantity, or select individual cells.
4. Scan destination NFC.
5. Backend validates both locations.
6. Execute the complete transfer atomically.
7. Create transaction history.

### Important NFC Rule

Do not store mutable inventory quantities inside the NFC tag.

NFC is only an identifier.

Recommended payload:

```text
inventory://location/E11-1A
```

The backend maps that identifier to the real location.

If browser NFC support is unavailable on the target device, provide fallback support for:

- Manual location code
- QR code
- Native Android NFC integration

The backend API must remain independent of the NFC technology.

---

# 5. Database

Use MongoDB.

Use Collections as:

part_types
vendors
parts
lots
cells
locations
inventory
cell_inventory
transactions


---

## 5.1 parts_type

{
  "_id": "PT-001",
  "part_type_name": "RESISTOR",
  "description": "Resistors",
  "created_by": "admin",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z"
}
Examples:
RESISTOR
DIODE
CAPACITOR
CELL
BUSBAR
CONNECTOR
IC
MECHANICAL


## 5.2 vendors

{
  "_id": "VEN-001",
  "vendor_name": "Example Vendor",
  "contact": "+91XXXXXXXXXX",
  "email": "vendor@example.com",
  "address": "Chennai",
  "country": "India",
  "status": "ACTIVE",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z"
}
Unique index:
vendor_name

---

## 5.3 part


{
  "_id": "PART-000001",
  "part_type_id": "PT-001",
  "part_code": "RES-10K-0603",
  "part_name": "10K Ohm Resistor",
  "package": "0603",
  "vendor_id": "VEN-001",
  "description": "10K resistor",
  "mfr": "Yageo",
  "mpn": "RC0603FR-0710KL",
  "rohs": "YES",
  "static_sensitive": "NO",
  "msl": "NA",
  "unit_of_measure": "PCS",
  "tracking_type": "QUANTITY",
  "active": true,
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z"
}
For cells:
{
  "_id": "PART-000010",
  "part_type_id": "PT-CELL",
  "part_code": "CELL-21700",
  "part_name": "21700 Lithium Ion Cell",
  "unit_of_measure": "PCS",
  "tracking_type": "SERIAL",
  "active": true
}
Important:
Do NOT store:
quantity, current_location, lot_batch_no


## 5.4 lots

Represents a supplier/manufacturing batch.
{
  "_id": "LOT-000001",
  "part_id": "PART-000001",
  "lot_batch_no": "YG20260831",
  "vendor_id": "VEN-001",
  "dop": "2026-08-01T00:00:00Z",
  "manufacturing_date": "2026-08-01",
  "received_date": "2026-08-31",
  "expiry_date": null,
  "created_at": "2026-08-31T10:00:00Z"
}
Create a unique compound index:
part_id + lot_batch_no

```

Do not store current inventory quantity in `lots`.

---

## 5.5 cells

{
  "_id": "CELL-ID-000001",
  "cell_serial_no": "CELL-2026-000001",
  "part_id": "PART-000010",
  "lot_id": "LOT-CELL-000001",
  "manufacturing_date": "2026-08-20",
  "date_code": "2620",
  "status": "AVAILABLE",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z"
}
Create a unique index on:
cell_serial_no
This guarantees that every physical cell has one unique identity.


---

## 5.6 locations

Physical warehouse/rack/box location.

```text
location_id          BIGINT PK
location_code        VARCHAR(100) UNIQUE NOT NULL
warehouse_code       VARCHAR(50) NOT NULL
rack_code            VARCHAR(50) NOT NULL
box_code             VARCHAR(50) NOT NULL
nfc_tag_uid          VARCHAR(100) UNIQUE
status               VARCHAR(30)
created_at           TIMESTAMP
updated_at           TIMESTAMP
```

Example:

```text
location_id   = 25
location_code = E11-1A
warehouse_code = E
Bay_number   = 1 
rack_code      = 1
columnnumber       = 1
column serparatenumber = A
nfc_tag_uid    = E11-1A
status         = ACTIVE
```

---

## 5.7 inventory

Current quantity-based inventory.

{
  "_id": "INV-000001",
  "part_id": "PART-000001",
  "lot_id": "LOT-000001",
  "location_id": "LOC-000025",
  "quantity": 10000,
  "available_quantity": 9500,
  "reserved_quantity": 500,
  "reserved_by": "USER-001",
  "reserved_for": "WO-1001",
  "status": "AVAILABLE",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z"
}
Create a unique compound index:
part_id + lot_id + location_id
This prevents duplicate inventory records for the same:
Part + Lot + Location

```

---

## 5.8 cell_inventory

{
  "_id": "CELL-INV-000001",
  "cell_id": "CELL-ID-000001",
  "location_id": "LOC-000025",
  "status": "AVAILABLE",
  "stored_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z"
}
Create a unique index on:
cell_id
Therefore:
CELL-2026-000001
        |
        v
E11-1A


## 5.9 transactions

{
  "_id": "TXN-000001",
  "part_id": "PART-000001",
  "lot_id": "LOT-000001",
  "cell_id": null,
  "transaction_type": "RECEIVE",
  "quantity": 10000,
  "from_location_id": null,
  "to_location_id": "LOC-000025",
  "user_id": "USER-001",
  "reference_id": "PO-10001",
  "timestamp": "2026-08-31T10:00:00Z",
  "description": "Initial material receipt"
}
Cell transaction:
{
  "_id": "TXN-000002",
  "part_id": "PART-000010",
  "lot_id": "LOT-CELL-000001",
  "cell_id": "CELL-ID-000001",
  "transaction_type": "TRANSFER",
  "quantity": 1,
  "from_location_id": "LOC-000001",
  "to_location_id": "LOC-000025",
  "user_id": "USER-001",
  "reference_id": "TRANSFER-1001",
  "timestamp": "2026-08-31T11:00:00Z",
  "description": "Cell transferred"
}
Transaction types:
RECEIVE
ISSUE
TRANSFER
ADJUSTMENT
RETURN
RESERVE
RELEASE
Transactions must NEVER be deleted or overwritten.

## Dynamic Part Fields

Part creation screen must support dynamic fields based on `part_type`.

For example:

### Resistor
- Resistance
- Tolerance
- Power Rating

### Diode
- Forward Voltage
- Forward Current
- Reverse Voltage

### Cell
- Nominal Voltage
- Capacity
- Chemistry

### Bus Bar
- Material
- Length
- Width
- Thickness

The user must be able to **Add / Edit / Delete custom fields** for each part type.

Example:

```text
Part Type: Resistor

Fields:
☑ Resistance
☑ Tolerance
☑ Power Rating
☐ Temperature Coefficient

[ + Add Field ]   [ Edit ]   [ Delete ]
When creating a part, the system must automatically show the fields configured for that part_type.
Example:
Select Part Type → Resistor

Part Name:       10K Resistor
Part Code:       RES-10K-0603

Resistance:      10K Ω
Tolerance:       1%
Power Rating:    0.1 W
For another part type:
Select Part Type → Diode

Forward Voltage: 1V
Forward Current: 150mA
Reverse Voltage: 100V
MongoDB
Create one additional collection:
part_type_fields
It stores which fields belong to each part_type.
Example:
{
  "_id": "PTF-001",
  "part_type_id": "PT-RESISTOR",
  "field_name": "Resistance",
  "field_key": "resistance",
  "data_type": "DECIMAL",
  "unit": "OHM",
  "required": true,
  "active": true
}
The actual values are stored inside the parts collection:
{
  "part_code": "RES-10K-0603",
  "part_type_id": "PT-RESISTOR",
  "attributes": {
    "resistance": 10000,
    "tolerance": 1,
    "power_rating": 0.1
  }
}
Important
Do not create separate collections for:
resistors
diodes
cells
busbars
capacitors
Use:
part_types
     ↓
part_type_fields
     ↓
parts
This allows new part types and fields to be added without changing the database structure.


# 6. Relationships

part_types
     |
     v
   parts
     |
     +--------> vendors
     |
     v
   lots
     |
     +--------> inventory
     |
     v
   cells
     |
     v
cell_inventory
     |
     v
 locations


parts
  |
  +----> inventory
  |
  +----> transactions

lots
  |
  +----> inventory
  |
  +----> transactions

cells
  |
  +----> transactions
---

# 7. Example: Receive 10,000 Resistors

Supplier:

```text
Element14
```

Material:

```text
Part: RES-10K-0603-vendor_id-datecode
MPN: RC0603FR-0710KL
Lot: YG20260831
Quantity: 10,000 PCS
```

Flow:

```text
Search part
    |
Verify vendor
    |
Create/select lot
    |
Scan destination NFC
    |
Resolve E11-1A
    |
Create/update inventory
    |
Create RECEIVE transaction
```

Current inventory becomes:

```text
RES-10K-0603
LOT-YG20260831
E11-1A
10,000 PCS
```

---

# 8. Example: Receive 1,000 Cells

Supplier sends:

```text
Part: CELL-21700
Lot: CELLLOT-001
Quantity: 1000
```

If individual serial numbers are available:

```text
CELL-000001
CELL-000002
...
CELL-001000
```

Create:

- One lot
- 1,000 cell records
- Cell inventory records for their current locations
- Receive transaction history

Example:

```text
CELL-000001 -> E11-1A
CELL-000002 ->  E11-2A
CELL-000003 ->  E11-3A
```

The system must be able to search any exact cell serial and show its current location and history.

---

# 9. Example: Cell Transfer

Move:

```text
CELL-000001
```

from:

```text
E11-1A
```

to:

```text
E11-3A
```

Flow:

```text
Scan source NFC
    |
Select/scan CELL-000001
    |
Scan destination NFC
    |
Backend validates source and destination
    |
Update cell_inventory
    |
Create TRANSFER transaction
```

Transaction:

```text
TRANSFER
cell_id = CELL-000001
quantity = 1
from =  E11-1A
to   =  E11-2A
```

---

# 10. Future Cell Traceability

The cell ID must remain the common traceability key for future MES processes.

Example:

```text
02KCBE516100DHFAH2300236
    |
    +--> CDC result
    |
    +--> Sorting result
    |
    +--> Compression
    |
    +--> MODULE-00001
    |
    +--> Welding
    |
    +--> Testing
    |
    +--> Final Battery
```

Do not implement all MES process tables in the first inventory version. Keep the inventory model ready for future integration.

---

# 11. Frontend

Use a clean professional enterprise/MES-style UI.

Main navigation:

```text
Dashboard
Inventory
Parts
Cells
Lots
Vendors
Locations
Transactions
Stock Operations
Reports
Settings
```

## Inventory screen

Support:

- Search
- Filters
- Part type filter
- Vendor filter
- Lot filter
- Location filter
- Status filter
- Sorting
- Pagination
- Current quantity
- Available quantity
- Reserved quantity
- Location details

## Cell screen

Support:

- Search by cell serial
- Scan/enter cell serial
- Current location
- Lot
- Status
- Manufacturing information
- Transaction history
- Process history placeholder for future MES integration

## Location screen

Show:

```text
Warehouse
Rack
Box
Location Code
NFC Tag
Status
Current inventory
```

Provide:

```text
Scan NFC
```

where supported.

---

# 12. Stock Operation Screens

## Receive

```text
Select Part
    |
Select/Create Lot
    |
Enter Quantity
    |
Scan NFC Location
    |
Review
    |
Confirm Receive
```

## Issue

```text
Select Part
    |
Select Lot
    |
Scan Location NFC
    |
Enter Quantity
    |
Confirm Issue
```

## Transfer

```text
Scan Source NFC
    |
Select Part / Scan Cell
    |
Enter Quantity / Select Cell
    |
Scan Destination NFC
    |
Review
    |
Confirm Transfer
```

For individual cells:

```text
Scan Source
    |
Scan Cell Serial
    |
Scan Destination
    |
Confirm
```

---

# 13. Backend

Recommended stack:

```text
Python , flask , pymongo and required library and tools
```

Architecture:


inventory-management/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── part.py
│   │   │   ├── vendor.py
│   │   │   ├── lot.py
│   │   │   ├── cell.py
│   │   │   ├── location.py
│   │   │   ├── inventory.py
│   │   │   └── transaction.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── part.py
│   │   │   ├── vendor.py
│   │   │   ├── lot.py
│   │   │   ├── cell.py
│   │   │   ├── location.py
│   │   │   └── inventory.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── part_repository.py
│   │   │   ├── inventory_repository.py
│   │   │   ├── cell_repository.py
│   │   │   └── transaction_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── part_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── cell_service.py
│   │   │   ├── location_service.py
│   │   │   └── transaction_service.py
│   │   │
│   │   ├── routers/
│   │   │   ├── parts.py
│   │   │   ├── vendors.py
│   │   │   ├── lots.py
│   │   │   ├── cells.py
│   │   │   ├── locations.py
│   │   │   ├── inventory.py
│   │   │   └── transactions.py
│   │   │
│   │   ├── security/
│   │   │   ├── auth.py
│   │   │   └── permissions.py
│   │   │
│   │   └── utils/
│   │       └── logger.py
│   │
│   ├── tests/
│   │
│   ├── requirements.txt
│   └── .env
│
└── frontend/

Suggested packages:


Do not expose JPA entities directly from APIs. Use DTOs.

---

# 14. REST API

## Part Types

```text
GET  /api/v1/part-types
POST /api/v1/part-types
PUT  /api/v1/part-types/{id}
```

## Vendors

```text
GET  /api/v1/vendors
POST /api/v1/vendors
PUT  /api/v1/vendors/{id}
```

## Parts

```text
GET    /api/v1/parts
GET    /api/v1/parts/{id}
POST   /api/v1/parts
PUT    /api/v1/parts/{id}
DELETE /api/v1/parts/{id}
```

## Lots

```text
GET  /api/v1/lots
GET  /api/v1/lots/{id}
POST /api/v1/lots
```

## Cells

```text
GET /api/v1/cells
GET /api/v1/cells/{id}
GET /api/v1/cells/serial/{serialNo}
POST /api/v1/cells
```

## Locations

```text
GET /api/v1/locations
GET /api/v1/locations/{id}
GET /api/v1/locations/code/{locationCode}
GET /api/v1/locations/nfc/{nfcTagUid}
POST /api/v1/locations
PUT /api/v1/locations/{id}
```

## Inventory

```text
GET /api/v1/inventory
GET /api/v1/inventory/part/{partId}
GET /api/v1/inventory/location/{locationId}
```

## Cell Inventory

```text
GET /api/v1/cell-inventory/cell/{cellId}
GET /api/v1/cell-inventory/location/{locationId}
```

## Transactions

```text
GET /api/v1/transactions
GET /api/v1/transactions/{id}
```

## Business Operations

Do not allow the frontend to directly update inventory quantities.

Use business endpoints:

```text
POST /api/v1/stock/receive
POST /api/v1/stock/issue
POST /api/v1/stock/transfer
POST /api/v1/stock/reserve
POST /api/v1/stock/release
POST /api/v1/cells/transfer
```

---

# 15. NFC API Flow

Example:

```text
GET /api/v1/locations/nfc/{nfcTagUid}
```


The frontend should use this response for the operation.

Never trust a location code supplied by the client without backend validation.

---

# 16. Transaction Safety

Receive, issue, reserve, release and transfer must be atomic database operations.

Example transfer:

```text
BEGIN

Validate user
Validate source
Validate destination
Validate material
Validate quantity
Decrease source
Increase destination
Update cell location if applicable
Create transaction record

COMMIT
```

On failure:

```text
ROLLBACK
```

Never allow negative stock.

---

# 17. Validation

### Part

- part_code required and unique
- part_type required
- MPN is VARCHAR
- vendor must exist if supplied

### Lot

- part must exist
- lot_batch_no required
- `(part_id, lot_batch_no)` unique

### Cell

- cell_serial_no required and unique
- part must exist
- lot must exist
- lot must belong to the same part

### Location

- location_code unique
- NFC UID unique
- location must be ACTIVE for stock movement

### Inventory

```text
quantity >= 0
available_quantity >= 0
reserved_quantity >= 0
available_quantity + reserved_quantity <= quantity
```

### Transfer

- source and destination cannot be the same
- sufficient stock required
- source must be active
- destination must be active

---

# 18. Audit

Every stock-changing operation must record:

```text
who
what
when
from where
to where
quantity
part
lot
cell if applicable
reference
```

Never silently change stock.

Every change must generate a transaction record.

---

# 19. Security

Implement authentication and role-based authorization.

Roles:

```text
ADMIN
INVENTORY_MANAGER
STORE_OPERATOR
VIEWER
```

Example:

### ADMIN

Everything.

### INVENTORY_MANAGER

- Manage parts
- Manage vendors
- Manage lots
- Receive
- Issue
- Transfer
- Reserve
- Reports

### STORE_OPERATOR

- Receive
- Issue
- Transfer
- NFC scanning
- View inventory

### VIEWER

Read-only.

---

# 20. Error Handling

Use consistent API errors.

Example:

```json
{
  "timestamp": "2026-08-31T10:30:00",
  "status": 400,
  "error": "INSUFFICIENT_STOCK",
  "message": "Requested quantity exceeds available quantity",
  "path": "/api/v1/stock/issue"
}
```

Do not expose stack traces to users.

---

# 21. Indexes

Create indexes for common searches:

```text
parts(part_code)
parts(mpn)

lots(lot_batch_no)
lots(part_id)

cells(cell_serial_no)
cells(part_id)
cells(lot_id)
cells(status)

locations(location_code)
locations(nfc_tag_uid)
locations(warehouse_code)

inventory(part_id)
inventory(lot_id)
inventory(location_id)

transactions(part_id)
transactions(lot_id)
transactions(cell_id)
transactions(from_location_id)
transactions(to_location_id)
transactions(timestamp)
```

---

# 22. Dashboard

Display:

- Total parts
- Total stock
- Low-stock items
- Reserved stock
- Active locations
- Empty locations
- Occupied locations
- Recent transactions
- Recently received material
- Recently issued material
- Cell count
- Cell status summary

---

# 23. Development Order

## Phase 1 — Setup

- Frontend
- Backend
- MongoDB
- Docker Compose
- Environment configuration

## Phase 2 — Master Data

- Part types
- Vendors
- Parts
- Locations

## Phase 3 — Lots

- Create lots
- Receive lots
- Lot search

## Phase 4 — Inventory

- Receive
- Issue
- Transfer
- Reserve
- Release
- Dashboard

## Phase 5 — Cell Tracking

- Cell creation
- Cell serial search
- Cell inventory
- Individual cell transfer
- Cell history

## Phase 6 — NFC

- NFC location mapping
- NFC scanning
- Source/destination NFC workflow
- NFC validation
- Fallback QR/manual location support

## Phase 7 — Security

- Login
- Roles
- Permissions
- Audit

## Phase 8 — Reports

- Stock report
- Location report
- Lot report
- Cell traceability report
- Transaction report

## Phase 9 — Testing

- Unit tests
- Integration tests
- API tests
- Inventory transaction tests
- Cell traceability tests
- NFC workflow tests

---

# 24. Non-Negotiable Design Rules

1. `part` = what the material is.
2. `lot` = which batch.
3. `cell` = which exact physical battery cell.
4. `location` = where the material physically is.
5. `inventory` = current quantity-based stock.
6. `cell_inventory` = current location/status of an individual cell.
7. `transactions` = immutable movement history.
8. NFC = location identifier only.
9. Backend = source of truth.
10. Frontend must never directly modify database state.
11. Do not store current quantity in `part` or `lots`.
12. Do not delete transaction history.
13. All stock changes must use database transactions.
14. Use internal numeric IDs plus human-readable codes/serial numbers.
15. Use `VARCHAR` for part codes, MPNs and lot/batch numbers.
16. Maintain consistent FK datatypes.
17. Individual cell traceability must never be lost.

---

# 25. AI Coding Agent Instructions

Implement this as a real working application, not a static mockup.

Before coding:

1. Inspect the existing repository.
2. Identify existing frontend/backend code.
3. Reuse working infrastructure where appropriate.
4. Do not overwrite working code unnecessarily.
5. Create database migrations first.
6. Implement backend entities, repositories, services, DTOs and APIs.
7. Add validation and transactional business logic.
8. Test backend APIs.
9. Implement frontend pages and workflows.
10. Integrate frontend with backend.
11. Implement NFC location workflow and fallback.
12. Add authentication and authorization.
13. Add tests.
14. Update README with setup, configuration and run instructions.

Do not hardcode inventory data into the frontend.

All inventory state must come from backend APIs.

The frontend must never directly access MongoDB.

The backend must enforce all business rules.

For every stock-changing operation:

```text
Validate
  -> Update current state
  -> Create immutable transaction
  -> Commit atomically
```

The final application must be clean, maintainable, production-oriented and ready for future MES integration.

