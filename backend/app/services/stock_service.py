from datetime import datetime, timezone
from pymongo import ReturnDocument
from app.config.database import Database
from app.models.counter import SequenceCounter
from app.repositories.part_repository import PartRepository, LotRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.cell_repository import CellRepository, CellInventoryRepository
from app.repositories.transaction_repository import TransactionRepository

class StockService:
    def __init__(self):
        self.part_repo = PartRepository()
        self.lot_repo = LotRepository()
        self.location_repo = LocationRepository()
        self.inventory_repo = InventoryRepository()
        self.cell_repo = CellRepository()
        self.cell_inventory_repo = CellInventoryRepository()
        self.txn_repo = TransactionRepository()

    def resolve_location(self, loc_id: str = None, loc_code: str = None, nfc_uid: str = None, session=None):
        """Resolves location by id, code, or nfc uid and checks ACTIVE status."""
        loc = None
        if loc_id:
            loc = self.location_repo.find_by_id(loc_id, session=session)
        elif loc_code:
            loc = self.location_repo.find_by_code(loc_code.strip(), session=session)
        elif nfc_uid:
            loc = self.location_repo.find_by_nfc(nfc_uid.strip(), session=session)

        if not loc:
            raise ValueError("Destination/Source location could not be resolved from provided ID, Code, or NFC Tag")

        if loc.get("status") != "ACTIVE":
            raise ValueError(f"Location '{loc.get('location_code')}' is not ACTIVE (current status: {loc.get('status')})")

        return loc

    def log_transaction(self, part_id: str, lot_id: str, cell_id: str, txn_type: str, quantity: int,
                        from_loc_id: str, to_loc_id: str, user_id: str, ref_id: str = None,
                        desc: str = None, session=None):
        """Creates an immutable audit transaction record."""
        txn_id = SequenceCounter.get_next_id("transaction", session=session)
        now = datetime.now(timezone.utc).isoformat()
        txn_doc = {
            "_id": txn_id,
            "part_id": part_id,
            "lot_id": lot_id,
            "cell_id": cell_id,
            "transaction_type": txn_type,
            "quantity": quantity,
            "from_location_id": from_loc_id,
            "to_location_id": to_loc_id,
            "user_id": user_id,
            "reference_id": ref_id,
            "timestamp": now,
            "description": desc or f"{txn_type} transaction executed"
        }
        self.txn_repo.insert_one(txn_doc, session=session)
        return txn_doc

    def receive(self, data: dict, user_id: str):
        """Atomic Receive for quantity parts and bulk serial-tracked battery cells."""
        def _execute(session=None):
            part = self.part_repo.find_by_id(data["part_id"], session=session)
            if not part:
                raise ValueError(f"Part {data['part_id']} does not exist")
            if not part.get("active", True):
                raise ValueError(f"Part {part.get('part_code')} is inactive")

            # Resolve or Create Lot
            lot_id = data.get("lot_id")
            if not lot_id and data.get("lot_batch_no"):
                batch_no = data["lot_batch_no"].strip()
                existing_lot = self.lot_repo.find_by_part_and_batch(part["_id"], batch_no, session=session)
                if existing_lot:
                    lot_id = existing_lot["_id"]
                else:
                    lot_id = SequenceCounter.get_next_id("lot", session=session)
                    lot_doc = {
                        "_id": lot_id,
                        "part_id": part["_id"],
                        "lot_batch_no": batch_no,
                        "vendor_id": data.get("vendor_id") or part.get("vendor_id"),
                        "manufacturing_date": data.get("manufacturing_date"),
                        "received_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "expiry_date": data.get("expiry_date")
                    }
                    self.lot_repo.insert_one(lot_doc, session=session)
            elif not lot_id:
                raise ValueError("Either lot_id or lot_batch_no must be supplied")

            lot = self.lot_repo.find_by_id(lot_id, session=session)
            if not lot:
                raise ValueError(f"Lot {lot_id} does not exist")

            # Resolve Location
            destination_loc = self.resolve_location(
                loc_id=data.get("location_id"),
                loc_code=data.get("location_code"),
                nfc_uid=data.get("nfc_tag_uid"),
                session=session
            )
            dest_loc_id = destination_loc["_id"]

            qty = int(data["quantity"])
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero")

            now = datetime.now(timezone.utc).isoformat()

            # --- Branch by Tracking Type ---
            if part.get("tracking_type") == "SERIAL":
                # Battery cells bulk receive
                cell_serials = []
                if data.get("cell_serials"):
                    cell_serials = [s.strip() for s in data["cell_serials"] if s.strip()]
                elif data.get("serial_range_prefix") and data.get("serial_range_start") is not None and data.get("serial_range_end") is not None:
                    prefix = data["serial_range_prefix"].strip()
                    start_num = int(data["serial_range_start"])
                    end_num = int(data["serial_range_end"])
                    pad = max(6, len(str(end_num)))
                    cell_serials = [f"{prefix}{str(i).zfill(pad)}" for i in range(start_num, end_num + 1)]

                if len(cell_serials) != qty:
                    raise ValueError(f"Supplied cell serials count ({len(cell_serials)}) does not match receive quantity ({qty})")

                # Verify serial uniqueness
                existing_cells = self.cell_repo.find_all({"cell_serial_no": {"$in": cell_serials}}, session=session)
                if existing_cells:
                    dupes = [c["cell_serial_no"] for c in existing_cells[:5]]
                    raise ValueError(f"Duplicate cell serial numbers found: {', '.join(dupes)}")

                # Batch generate Cell IDs
                cell_ids = SequenceCounter.get_next_batch_ids("cell", qty, session=session)
                cell_inv_ids = SequenceCounter.get_next_batch_ids("cell_inventory", qty, session=session)

                cell_docs = []
                cell_inv_docs = []

                for idx, serial in enumerate(cell_serials):
                    c_id = cell_ids[idx]
                    cinv_id = cell_inv_ids[idx]
                    
                    cell_docs.append({
                        "_id": c_id,
                        "cell_serial_no": serial,
                        "part_id": part["_id"],
                        "lot_id": lot["_id"],
                        "manufacturing_date": data.get("manufacturing_date") or lot.get("manufacturing_date"),
                        "date_code": data.get("date_code", ""),
                        "status": "AVAILABLE",
                        "created_at": now,
                        "updated_at": now
                    })

                    cell_inv_docs.append({
                        "_id": cinv_id,
                        "cell_id": c_id,
                        "location_id": dest_loc_id,
                        "status": "AVAILABLE",
                        "stored_at": now,
                        "updated_at": now
                    })

                self.cell_repo.insert_many(cell_docs, session=session)
                self.cell_inventory_repo.insert_many(cell_inv_docs, session=session)

                # Batch generate transactions for audit
                txn_doc = self.log_transaction(
                    part_id=part["_id"],
                    lot_id=lot["_id"],
                    cell_id=None, # Summary transaction for bulk cell receive
                    txn_type="RECEIVE",
                    quantity=qty,
                    from_loc_id=None,
                    to_loc_id=dest_loc_id,
                    user_id=user_id,
                    ref_id=data.get("reference_id"),
                    desc=f"Bulk received {qty} cells ({cell_serials[0]} - {cell_serials[-1]})",
                    session=session
                )

                return {
                    "operation": "RECEIVE",
                    "part_id": part["_id"],
                    "part_code": part["part_code"],
                    "lot_id": lot["_id"],
                    "lot_batch_no": lot["lot_batch_no"],
                    "location_id": dest_loc_id,
                    "location_code": destination_loc["location_code"],
                    "quantity": qty,
                    "cell_count": len(cell_docs),
                    "first_serial": cell_serials[0],
                    "last_serial": cell_serials[-1],
                    "transaction_id": txn_doc["_id"]
                }

            else:
                # Quantity parts receive
                inv = self.inventory_repo.find_by_part_lot_location(
                    part_id=part["_id"],
                    lot_id=lot["_id"],
                    location_id=dest_loc_id,
                    session=session
                )

                if inv:
                    self.inventory_repo.update_one(
                        {"_id": inv["_id"]},
                        {
                            "$inc": {"quantity": qty, "available_quantity": qty},
                            "$set": {"status": "AVAILABLE"}
                        },
                        session=session
                    )
                    inv_id = inv["_id"]
                else:
                    inv_id = SequenceCounter.get_next_id("inventory", session=session)
                    inv_doc = {
                        "_id": inv_id,
                        "part_id": part["_id"],
                        "lot_id": lot["_id"],
                        "location_id": dest_loc_id,
                        "quantity": qty,
                        "available_quantity": qty,
                        "reserved_quantity": 0,
                        "reserved_by": None,
                        "reserved_for": None,
                        "status": "AVAILABLE",
                        "created_at": now,
                        "updated_at": now
                    }
                    self.inventory_repo.insert_one(inv_doc, session=session)

                txn_doc = self.log_transaction(
                    part_id=part["_id"],
                    lot_id=lot["_id"],
                    cell_id=None,
                    txn_type="RECEIVE",
                    quantity=qty,
                    from_loc_id=None,
                    to_loc_id=dest_loc_id,
                    user_id=user_id,
                    ref_id=data.get("reference_id"),
                    desc=data.get("description") or f"Received {qty} {part.get('unit_of_measure', 'PCS')}",
                    session=session
                )

                return {
                    "operation": "RECEIVE",
                    "inventory_id": inv_id,
                    "part_id": part["_id"],
                    "part_code": part["part_code"],
                    "lot_id": lot["_id"],
                    "lot_batch_no": lot["lot_batch_no"],
                    "location_id": dest_loc_id,
                    "location_code": destination_loc["location_code"],
                    "quantity": qty,
                    "transaction_id": txn_doc["_id"]
                }

        return Database.execute_transaction(_execute)

    def issue(self, data: dict, user_id: str):
        """Atomic Issue for quantity parts."""
        def _execute(session=None):
            part = self.part_repo.find_by_id(data["part_id"], session=session)
            if not part:
                raise ValueError(f"Part {data['part_id']} does not exist")

            lot = self.lot_repo.find_by_id(data["lot_id"], session=session)
            if not lot:
                raise ValueError(f"Lot {data['lot_id']} does not exist")

            source_loc = self.resolve_location(
                loc_id=data.get("location_id"),
                loc_code=data.get("location_code"),
                nfc_uid=data.get("nfc_tag_uid"),
                session=session
            )
            src_loc_id = source_loc["_id"]

            qty = int(data["quantity"])
            if qty <= 0:
                raise ValueError("Issue quantity must be greater than zero")

            inv = self.inventory_repo.find_by_part_lot_location(part["_id"], lot["_id"], src_loc_id, session=session)
            if not inv:
                raise ValueError(f"No stock record found for Part '{part['part_code']}' at Location '{source_loc['location_code']}'")

            if inv.get("available_quantity", 0) < qty:
                raise ValueError(
                    f"INSUFFICIENT_STOCK: Requested {qty} exceeds available quantity ({inv.get('available_quantity', 0)})"
                )

            new_qty = inv["quantity"] - qty
            new_avail = inv["available_quantity"] - qty
            new_status = "OUT_OF_STOCK" if new_qty == 0 else "AVAILABLE"

            self.inventory_repo.update_one(
                {"_id": inv["_id"]},
                {
                    "$inc": {"quantity": -qty, "available_quantity": -qty},
                    "$set": {"status": new_status}
                },
                session=session
            )

            txn_doc = self.log_transaction(
                part_id=part["_id"],
                lot_id=lot["_id"],
                cell_id=None,
                txn_type="ISSUE",
                quantity=qty,
                from_loc_id=src_loc_id,
                to_loc_id=None,
                user_id=user_id,
                ref_id=data.get("reference_id"),
                desc=data.get("description") or f"Issued {qty} {part.get('unit_of_measure', 'PCS')}",
                session=session
            )

            return {
                "operation": "ISSUE",
                "inventory_id": inv["_id"],
                "part_code": part["part_code"],
                "lot_batch_no": lot["lot_batch_no"],
                "location_code": source_loc["location_code"],
                "issued_quantity": qty,
                "remaining_quantity": new_qty,
                "remaining_available": new_avail,
                "transaction_id": txn_doc["_id"]
            }

        return Database.execute_transaction(_execute)

    def transfer(self, data: dict, user_id: str):
        """Atomic Transfer for quantity parts between locations."""
        def _execute(session=None):
            part = self.part_repo.find_by_id(data["part_id"], session=session)
            if not part:
                raise ValueError(f"Part {data['part_id']} does not exist")

            lot = self.lot_repo.find_by_id(data["lot_id"], session=session)
            if not lot:
                raise ValueError(f"Lot {data['lot_id']} does not exist")

            src_loc = self.resolve_location(
                loc_id=data.get("from_location_id"),
                loc_code=data.get("from_location_code"),
                nfc_uid=data.get("from_nfc_tag_uid"),
                session=session
            )
            dest_loc = self.resolve_location(
                loc_id=data.get("to_location_id"),
                loc_code=data.get("to_location_code"),
                nfc_uid=data.get("to_nfc_tag_uid"),
                session=session
            )

            if src_loc["_id"] == dest_loc["_id"]:
                raise ValueError("Source and destination locations cannot be identical")

            qty = int(data["quantity"])
            if qty <= 0:
                raise ValueError("Transfer quantity must be greater than zero")

            # Check source inventory
            src_inv = self.inventory_repo.find_by_part_lot_location(part["_id"], lot["_id"], src_loc["_id"], session=session)
            if not src_inv:
                raise ValueError(f"No stock found for Part '{part['part_code']}' at Source Location '{src_loc['location_code']}'")

            if src_inv.get("available_quantity", 0) < qty:
                raise ValueError(
                    f"INSUFFICIENT_STOCK: Requested transfer {qty} exceeds available quantity ({src_inv.get('available_quantity', 0)})"
                )

            # Decrement source
            new_src_qty = src_inv["quantity"] - qty
            new_src_avail = src_inv["available_quantity"] - qty
            src_status = "OUT_OF_STOCK" if new_src_qty == 0 else "AVAILABLE"

            self.inventory_repo.update_one(
                {"_id": src_inv["_id"]},
                {
                    "$inc": {"quantity": -qty, "available_quantity": -qty},
                    "$set": {"status": src_status}
                },
                session=session
            )

            # Increment destination
            dest_inv = self.inventory_repo.find_by_part_lot_location(part["_id"], lot["_id"], dest_loc["_id"], session=session)
            now = datetime.now(timezone.utc).isoformat()
            if dest_inv:
                self.inventory_repo.update_one(
                    {"_id": dest_inv["_id"]},
                    {
                        "$inc": {"quantity": qty, "available_quantity": qty},
                        "$set": {"status": "AVAILABLE"}
                    },
                    session=session
                )
            else:
                dest_inv_id = SequenceCounter.get_next_id("inventory", session=session)
                self.inventory_repo.insert_one({
                    "_id": dest_inv_id,
                    "part_id": part["_id"],
                    "lot_id": lot["_id"],
                    "location_id": dest_loc["_id"],
                    "quantity": qty,
                    "available_quantity": qty,
                    "reserved_quantity": 0,
                    "reserved_by": None,
                    "reserved_for": None,
                    "status": "AVAILABLE",
                    "created_at": now,
                    "updated_at": now
                }, session=session)

            txn_doc = self.log_transaction(
                part_id=part["_id"],
                lot_id=lot["_id"],
                cell_id=None,
                txn_type="TRANSFER",
                quantity=qty,
                from_loc_id=src_loc["_id"],
                to_loc_id=dest_loc["_id"],
                user_id=user_id,
                ref_id=data.get("reference_id"),
                desc=data.get("description") or f"Transferred {qty} from {src_loc['location_code']} to {dest_loc['location_code']}",
                session=session
            )

            return {
                "operation": "TRANSFER",
                "part_code": part["part_code"],
                "lot_batch_no": lot["lot_batch_no"],
                "from_location": src_loc["location_code"],
                "to_location": dest_loc["location_code"],
                "quantity": qty,
                "transaction_id": txn_doc["_id"]
            }

        return Database.execute_transaction(_execute)

    def transfer_cell(self, data: dict, user_id: str):
        """Atomic Transfer for an individual physical cell."""
        def _execute(session=None):
            cell = None
            if data.get("cell_id"):
                cell = self.cell_repo.find_by_id(data["cell_id"], session=session)
            elif data.get("cell_serial_no"):
                cell = self.cell_repo.find_by_serial(data["cell_serial_no"].strip(), session=session)

            if not cell:
                raise ValueError("Cell not found with supplied ID or serial number")

            # Lookup current cell location
            cell_inv = self.cell_inventory_repo.find_by_cell_id(cell["_id"], session=session)
            if not cell_inv:
                raise ValueError(f"Cell {cell['cell_serial_no']} has no active location in inventory")

            src_loc_id = cell_inv["location_id"]
            src_loc = self.location_repo.find_by_id(src_loc_id, session=session)

            # Resolve destination location
            dest_loc = self.resolve_location(
                loc_id=data.get("to_location_id"),
                loc_code=data.get("to_location_code"),
                nfc_uid=data.get("to_nfc_tag_uid"),
                session=session
            )
            dest_loc_id = dest_loc["_id"]

            if src_loc_id == dest_loc_id:
                raise ValueError(f"Cell {cell['cell_serial_no']} is already located at '{dest_loc['location_code']}'")

            # Update cell inventory location
            self.cell_inventory_repo.update_one(
                {"_id": cell_inv["_id"]},
                {
                    "$set": {
                        "location_id": dest_loc_id,
                        "status": "AVAILABLE"
                    }
                },
                session=session
            )

            # Log transaction
            txn_doc = self.log_transaction(
                part_id=cell["part_id"],
                lot_id=cell["lot_id"],
                cell_id=cell["_id"],
                txn_type="TRANSFER",
                quantity=1,
                from_loc_id=src_loc_id,
                to_loc_id=dest_loc_id,
                user_id=user_id,
                ref_id=data.get("reference_id"),
                desc=data.get("description") or f"Cell {cell['cell_serial_no']} transferred",
                session=session
            )

            return {
                "operation": "CELL_TRANSFER",
                "cell_id": cell["_id"],
                "cell_serial_no": cell["cell_serial_no"],
                "from_location": src_loc["location_code"] if src_loc else src_loc_id,
                "to_location": dest_loc["location_code"],
                "transaction_id": txn_doc["_id"]
            }

        return Database.execute_transaction(_execute)

    def reserve(self, data: dict, user_id: str):
        """Atomic stock reservation for work orders."""
        def _execute(session=None):
            inv = None
            if data.get("inventory_id"):
                inv = self.inventory_repo.find_by_id(data["inventory_id"], session=session)
            elif data.get("part_id") and data.get("lot_id") and data.get("location_id"):
                inv = self.inventory_repo.find_by_part_lot_location(data["part_id"], data["lot_id"], data["location_id"], session=session)

            if not inv:
                raise ValueError("Inventory record not found for reservation")

            qty = int(data["quantity"])
            if qty <= 0:
                raise ValueError("Reserve quantity must be greater than zero")

            if inv.get("available_quantity", 0) < qty:
                raise ValueError(
                    f"INSUFFICIENT_STOCK: Requested reserve {qty} exceeds available quantity ({inv.get('available_quantity', 0)})"
                )

            work_order = data["reserved_for"].strip()

            self.inventory_repo.update_one(
                {"_id": inv["_id"]},
                {
                    "$inc": {"available_quantity": -qty, "reserved_quantity": qty},
                    "$set": {
                        "reserved_by": user_id,
                        "reserved_for": work_order
                    }
                },
                session=session
            )

            txn_doc = self.log_transaction(
                part_id=inv["part_id"],
                lot_id=inv["lot_id"],
                cell_id=None,
                txn_type="RESERVE",
                quantity=qty,
                from_loc_id=inv["location_id"],
                to_loc_id=inv["location_id"],
                user_id=user_id,
                ref_id=work_order,
                desc=data.get("description") or f"Stock reserved for Work Order {work_order}",
                session=session
            )

            return {
                "operation": "RESERVE",
                "inventory_id": inv["_id"],
                "reserved_quantity": qty,
                "reserved_for": work_order,
                "transaction_id": txn_doc["_id"]
            }

        return Database.execute_transaction(_execute)

    def release(self, data: dict, user_id: str):
        """Atomic stock release from reservation."""
        def _execute(session=None):
            inv = None
            if data.get("inventory_id"):
                inv = self.inventory_repo.find_by_id(data["inventory_id"], session=session)
            elif data.get("part_id") and data.get("lot_id") and data.get("location_id"):
                inv = self.inventory_repo.find_by_part_lot_location(data["part_id"], data["lot_id"], data["location_id"], session=session)

            if not inv:
                raise ValueError("Inventory record not found for release")

            qty = int(data["quantity"])
            if qty <= 0:
                raise ValueError("Release quantity must be greater than zero")

            if inv.get("reserved_quantity", 0) < qty:
                raise ValueError(
                    f"Cannot release {qty}: only {inv.get('reserved_quantity', 0)} is currently reserved"
                )

            new_reserved = inv["reserved_quantity"] - qty
            reserved_for = inv.get("reserved_for") if new_reserved > 0 else None
            reserved_by = inv.get("reserved_by") if new_reserved > 0 else None

            self.inventory_repo.update_one(
                {"_id": inv["_id"]},
                {
                    "$inc": {"available_quantity": qty, "reserved_quantity": -qty},
                    "$set": {
                        "reserved_by": reserved_by,
                        "reserved_for": reserved_for
                    }
                },
                session=session
            )

            txn_doc = self.log_transaction(
                part_id=inv["part_id"],
                lot_id=inv["lot_id"],
                cell_id=None,
                txn_type="RELEASE",
                quantity=qty,
                from_loc_id=inv["location_id"],
                to_loc_id=inv["location_id"],
                user_id=user_id,
                ref_id=data.get("reference_id"),
                desc=data.get("description") or f"Released {qty} units back to available stock",
                session=session
            )

            return {
                "operation": "RELEASE",
                "inventory_id": inv["_id"],
                "released_quantity": qty,
                "remaining_reserved": new_reserved,
                "transaction_id": txn_doc["_id"]
            }

        return Database.execute_transaction(_execute)
