# MES-Ready Production Inventory Management Web Application

A production-ready Inventory Management Web Application for an electronics and battery manufacturing environment built with **Python 3.9+ / Flask / PyMongo** on the backend and **Vue 3 / Vite / Tailwind CSS** on the frontend.

Designed to run across all devices (Android Chrome, Windows Desktop, POS terminals, and iOS) with Web NFC API tag resolution, live camera barcode/DataMatrix scanning, dynamic part type schemas, atomic ACID stock operations, and future MES traceability.

---

## 🌟 Key Features

1. **Dual Inventory Tracking Models**:
   - **Quantity-Tracked Bulk Components**: Resistors, Diodes, Capacitors, ICs, Connectors, Bus Bars, Screws (`Part -> Lot -> Inventory -> Location -> Quantity`).
   - **Serialized Battery Cells**: Individually tracked cylindrical and prismatic cells (`CELL-2026-000001`) with complete manufacturing history and lifecycle traceability (`Receive -> CDC Test -> Sorting -> Welding -> Battery Pack`).

2. **NFC & Warehouse Location Hierarchy**:
   - Structured EMS storage format: `E11-1A` (*Warehouse* `E`, *Bay* `1`, *Row* `1`, *Rack* `1`, *Section* `A`).
   - Physical NFC tag identifiers (`inventory://location/E11-1A`) mapped securely on the backend.
   - Built-in **Bulk Location Generator Wizard** to generate complete warehouse bin structures in seconds.
   - Fallback to live camera Barcode/DataMatrix scanner and manual code entry.

3. **Dynamic Part Attributes Engine**:
   - Create, edit, and configure custom dynamic fields per part type (e.g. Resistance, Voltage Rating, Tolerance, Nominal Capacity, Chemistry, Bus Bar dimensions) without database migrations.
   - Schema enforcement on part creation.

4. **Atomic Transaction Safety & Audit Logging**:
   - All stock operations (`Receive`, `Issue`, `Transfer`, `Reserve`, `Release`, `Cell Transfer`) execute atomically with negative-stock prevention.
   - Every movement creates an immutable transaction record (`who`, `what`, `when`, `from`, `to`, `quantity`, `reference`).

5. **Role-Based Access Control (RBAC)**:
   - `ADMIN`: Full system management, user registrations, part types, locations, and reports.
   - `INVENTORY_MANAGER`: Parts catalog, vendors, lots, stock reservations, and operations.
   - `STORE_OPERATOR`: Material receipt, issues, transfers, and NFC scanning.
   - `VIEWER`: Read-only audit and inventory monitoring.

---

## 🚀 Quick Start & Installation

### Option 1: Run Locally

#### 1. Backend (Python + Flask)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start MongoDB locally (port 27017)
# Run the Flask backend
python run.py
```
Backend will start on `http://127.0.0.1:5001`. On first run, it seeds inventory reference data only. Application users, passwords, and roles are managed exclusively in Keycloak.

Set these backend environment variables before starting the application:

```bash
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=mes-inventory
KEYCLOAK_CLIENT_ID=mes-frontend
KEYCLOAK_CLIENT_SECRET=<existing mes-frontend secret, if configured>
KEYCLOAK_ADMIN_CLIENT_ID=mes-backend
KEYCLOAK_ADMIN_CLIENT_SECRET=<existing mes-backend secret>
```

#### 2. Frontend (Vue 3 + Vite)
```bash
cd frontend
npm install
npm run dev
```
Frontend will be accessible at `http://localhost:3000`.

---

### Option 2: Run with Docker Compose

```bash
docker-compose up --build
```
- **Frontend App**: `http://localhost:3000`
- **Backend API**: `http://localhost:5001/api/health`
- **MongoDB**: `localhost:27017`

---

User accounts must exist in the `mes-inventory` Keycloak realm with one of the existing realm roles: `ADMIN`, `INVENTORY_MANAGER`, `STORE_OPERATOR`, or `VIEWER`.

---

## 🧪 Automated Tests

Run backend unit and integration tests with pytest:
```bash
cd backend
venv/bin/pytest -v
```

Tests cover:
- Authentication & JWT permissions
- Dynamic part types schema validation
- Warehouse hierarchy generation & NFC tag resolution
- Atomic Receive, Issue, Transfer, Reserve, Release flows with negative-stock prevention
- Bulk cell intake via Range Generator & serial transfer history

---

## 📡 REST API Documentation

### Authentication
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/me`

### Part Types & Dynamic Fields
- `GET /api/v1/part-types`
- `POST /api/v1/part-types`
- `POST /api/v1/part-types/<id>/fields`
- `DELETE /api/v1/part-types/fields/<field_id>`

### Parts & Vendors
- `GET /api/v1/parts`
- `POST /api/v1/parts`
- `GET /api/v1/vendors`
- `POST /api/v1/vendors`
- `GET /api/v1/lots`
- `POST /api/v1/lots`

### Locations & NFC
- `GET /api/v1/locations`
- `GET /api/v1/locations/code/<location_code>`
- `GET /api/v1/locations/nfc/<nfc_tag_uid>`
- `POST /api/v1/locations/bulk-generate`

### Stock Operations
- `POST /api/v1/stock/receive` (Supports bulk quantity parts & serialized battery cells with range generator)
- `POST /api/v1/stock/issue`
- `POST /api/v1/stock/transfer`
- `POST /api/v1/stock/reserve`
- `POST /api/v1/stock/release`
- `POST /api/v1/cells/transfer`

### Traceability & Audit
- `GET /api/v1/cells`
- `GET /api/v1/cells/serial/<serial_no>`
- `GET /api/v1/transactions`
- `GET /api/v1/dashboard/metrics`
- `GET /api/v1/reports/stock-by-part`
