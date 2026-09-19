from datetime import datetime, timezone
from app.config.database import Database
from app.models.counter import SequenceCounter
from app.repositories.item_repository import ItemRepository
from app.repositories.item_type_repository import ItemTypeRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.vendor_repository import VendorRepository

class StockService:
    def __init__(self):
        self.item_repo = ItemRepository()
        self.item_type_repo = ItemTypeRepository()
        self.location_repo = LocationRepository()
        self.inventory_repo = InventoryRepository()
        self.txn_repo = TransactionRepository()
        self.vendor_repo = VendorRepository()

    def resolve_location(self, org_id: str, loc_id: str = None, loc_code: str = None, nfc_uid: str = None, qr_code: str = None, session=None):
        loc = None
        if loc_id:
            loc = self.location_repo.find_one({"_id": loc_id, "organization_id": org_id}, session=session)
            if not loc:
                loc = self.location_repo.find_by_code(org_id, loc_id, session=session)
        elif loc_code:
            loc = self.location_repo.find_by_code(org_id, loc_code.strip(), session=session)
        elif nfc_uid:
            loc = self.location_repo.find_by_nfc(org_id, nfc_uid.strip(), session=session)
        elif qr_code:
            loc = self.location_repo.find_by_qr(org_id, qr_code.strip(), session=session)

        if not loc:
            raise ValueError("Location could not be resolved from provided ID, Code, NFC, or QR Tag")

        if loc.get("status") != "ACTIVE":
            raise ValueError(f"Location '{loc.get('location_code')}' is not ACTIVE (status: {loc.get('status')})")

        return loc

    def log_transaction(self, org_id: str, t_id: str, txn_type: str, item_id: str, quantity: float,
                        from_loc_id: str, to_loc_id: str, performed_by: str,
                        lot_number: str = None, serial_number: str = None, vendor_id: str = None,
                        reference: dict = None, remarks: str = None, session=None):
        txn_id = SequenceCounter.get_next_id("transaction", session=session)
        now = datetime.now(timezone.utc).isoformat()
        txn_doc = {
            "_id": txn_id,
            "t_id": t_id,
            "organization_id": org_id,
            "transaction_type": txn_type,
            "item_id": item_id,
            "part_id": item_id,
            "lot_number": lot_number,
            "lot_batch_no": lot_number,
            "serial_number": serial_number,
            "quantity": float(quantity),
            "from_location_id": from_loc_id,
            "to_location_id": to_loc_id,
            "vendor_id": vendor_id,
            "performed_by": performed_by,
            "reference": reference or {},
            "timestamp": now,
            "remarks": remarks or f"{txn_type} transaction"
        }
        self.txn_repo.insert_one(txn_doc, session=session)
        return txn_doc

    def receive(self, data: dict, user_id: str, org_id: str = "ORG-001"):
        def _execute(session=None):
            # 1. Resolve Item
            item_identifier = data.get("item_id") or data.get("part_id")
            item = self.item_repo.find_one({"_id": item_identifier, "organization_id": org_id}, session=session)
            if not item:
                item = self.item_repo.find_by_code(org_id, item_identifier, session=session)
            if not item:
                raise ValueError(f"Item '{item_identifier}' does not exist")
            if not item.get("active", True):
                raise ValueError(f"Item '{item.get('code')}' is inactive")

            item_type = self.item_type_repo.find_one({"_id": item["item_type_id"], "organization_id": org_id}, session=session)
            tracking_mode = item_type.get("tracking_mode", "QUANTITY") if item_type else "QUANTITY"

            # 2. Resolve Destination Location
            dest_loc = self.resolve_location(
                org_id=org_id,
                loc_id=data.get("location_id"),
                loc_code=data.get("location_code"),
                nfc_uid=data.get("nfc_uid") or data.get("nfc_tag_uid"),
                qr_code=data.get("qr_code"),
                session=session
            )
            dest_loc_id = dest_loc["_id"]

            qty = float(data["quantity"])
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero")

            lot_number = (data.get("lot_number") or data.get("lot_batch_no") or "").strip() or None
            vendor_id = data.get("vendor_id")
            reference = data.get("reference") or {}
            remarks = data.get("remarks") or data.get("description") or "Material receipt"
            site_id = data.get("site_id") or item.get("site_id") or "SITE-001"

            t_id = SequenceCounter.get_next_id("transaction", session=session)
            now = datetime.now(timezone.utc).isoformat()

            # 3. Branch by Tracking Mode (SERIAL vs QUANTITY/LOT)
            if tracking_mode == "SERIAL":
                serials = []
                if data.get("serial_numbers"):
                    serials = [s.strip() for s in data["serial_numbers"] if s.strip()]
                elif data.get("serial_number"):
                    serials = [data["serial_number"].strip()]
                elif data.get("serial_range_prefix") and data.get("serial_range_start") is not None and data.get("serial_range_end") is not None:
                    prefix = data["serial_range_prefix"].strip()
                    start_num = int(data["serial_range_start"])
                    end_num = int(data["serial_range_end"])
                    pad = max(6, len(str(end_num)))
                    serials = [f"{prefix}{str(i).zfill(pad)}" for i in range(start_num, end_num + 1)]

                if len(serials) != int(qty):
                    raise ValueError(f"Quantity is {int(qty)} but {len(serials)} serial numbers were provided/generated.")

                existing = self.inventory_repo.find_all({
                    "organization_id": org_id,
                    "serial_number": {"$in": serials},
                    "status": "AVAILABLE"
                }, session=session)
                if existing:
                    dupes = [x["serial_number"] for x in existing[:5]]
                    raise ValueError(f"Duplicate active serials already in inventory: {', '.join(dupes)}")

                inv_ids = SequenceCounter.get_next_batch_ids("inventory", len(serials), session=session)
                inv_docs = []
                for idx, s_num in enumerate(serials):
                    inv_docs.append({
                        "_id": inv_ids[idx],
                        "organization_id": org_id,
                        "item_id": item["_id"],
                        "part_id": item["_id"],
                        "location_id": dest_loc_id,
                        "lot_number": lot_number,
                        "serial_number": s_num,
                        "cell_id": s_num,
                        "cell_serial_no": s_num,
                        "quantity": 1.0,
                        "site_id": site_id,
                        "vendor_id": vendor_id,
                        "status": "AVAILABLE",
                        "created_at": now,
                        "updated_at": now
                    })

                self.inventory_repo.insert_many(inv_docs, session=session)

                self.log_transaction(
                    org_id=org_id,
                    t_id=t_id,
                    txn_type="RECEIVE",
                    item_id=item["_id"],
                    quantity=qty,
                    from_loc_id=None,
                    to_loc_id=dest_loc_id,
                    performed_by=user_id,
                    lot_number=lot_number,
                    serial_number=f"{serials[0]} - {serials[-1]}" if len(serials) > 1 else serials[0],
                    vendor_id=vendor_id,
                    reference=reference,
                    remarks=remarks,
                    session=session
                )

                return {
                    "operation": "RECEIVE",
                    "t_id": t_id,
                    "item_id": item["_id"],
                    "part_id": item["_id"],
                    "item_code": item["code"],
                    "part_code": item["code"],
                    "location_id": dest_loc_id,
                    "location_code": dest_loc["location_code"],
                    "lot_number": lot_number,
                    "lot_id": lot_number,
                    "lot_batch_no": lot_number,
                    "quantity": qty,
                    "cell_count": len(serials),
                    "serials_count": len(serials),
                    "first_serial": serials[0],
                    "last_serial": serials[-1]
                }

            else:
                inv = self.inventory_repo.find_by_keys(
                    org_id=org_id,
                    item_id=item["_id"],
                    location_id=dest_loc_id,
                    lot_number=lot_number,
                    serial_number=None,
                    session=session
                )

                if inv:
                    self.inventory_repo.update_one(
                        {"_id": inv["_id"]},
                        {
                            "$inc": {"quantity": qty},
                            "$set": {"status": "AVAILABLE", "updated_at": now}
                        },
                        session=session
                    )
                    inv_id = inv["_id"]
                else:
                    inv_id = SequenceCounter.get_next_id("inventory", session=session)
                    self.inventory_repo.insert_one({
                        "_id": inv_id,
                        "organization_id": org_id,
                        "item_id": item["_id"],
                        "part_id": item["_id"],
                        "location_id": dest_loc_id,
                        "lot_number": lot_number,
                        "serial_number": None,
                        "quantity": qty,
                        "site_id": site_id,
                        "vendor_id": vendor_id,
                        "status": "AVAILABLE",
                        "created_at": now,
                        "updated_at": now
                    }, session=session)

                self.log_transaction(
                    org_id=org_id,
                    t_id=t_id,
                    txn_type="RECEIVE",
                    item_id=item["_id"],
                    quantity=qty,
                    from_loc_id=None,
                    to_loc_id=dest_loc_id,
                    performed_by=user_id,
                    lot_number=lot_number,
                    vendor_id=vendor_id,
                    reference=reference,
                    remarks=remarks,
                    session=session
                )

                return {
                    "operation": "RECEIVE",
                    "t_id": t_id,
                    "inventory_id": inv_id,
                    "item_id": item["_id"],
                    "part_id": item["_id"],
                    "item_code": item["code"],
                    "part_code": item["code"],
                    "location_id": dest_loc_id,
                    "location_code": dest_loc["location_code"],
                    "lot_number": lot_number,
                    "lot_id": lot_number,
                    "lot_batch_no": lot_number,
                    "quantity": qty
                }

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()

    def issue(self, data: dict, user_id: str, org_id: str = "ORG-001"):
        def _execute(session=None):
            item_identifier = data.get("item_id") or data.get("part_id")
            item = self.item_repo.find_one({"_id": item_identifier, "organization_id": org_id}, session=session)
            if not item:
                item = self.item_repo.find_by_code(org_id, item_identifier, session=session)
            if not item:
                raise ValueError(f"Item '{item_identifier}' does not exist")

            src_loc = self.resolve_location(
                org_id=org_id,
                loc_id=data.get("location_id"),
                loc_code=data.get("location_code"),
                nfc_uid=data.get("nfc_uid") or data.get("nfc_tag_uid"),
                qr_code=data.get("qr_code"),
                session=session
            )
            src_loc_id = src_loc["_id"]

            qty = float(data["quantity"])
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero")

            lot_number = (data.get("lot_number") or data.get("lot_id") or "").strip() or None
            serial_number = (data.get("serial_number") or "").strip() or None
            reference = data.get("reference") or {}
            remarks = data.get("remarks") or data.get("description") or "Material issue"

            t_id = SequenceCounter.get_next_id("transaction", session=session)
            now = datetime.now(timezone.utc).isoformat()

            if serial_number:
                inv = self.inventory_repo.find_by_keys(
                    org_id=org_id,
                    item_id=item["_id"],
                    location_id=src_loc_id,
                    lot_number=lot_number,
                    serial_number=serial_number,
                    session=session
                )
                if not inv or inv.get("status") != "AVAILABLE":
                    raise ValueError(f"Serial '{serial_number}' is not available at location '{src_loc['location_code']}'")

                self.inventory_repo.update_one(
                    {"_id": inv["_id"]},
                    {"$set": {"status": "ISSUED", "quantity": 0.0, "updated_at": now}},
                    session=session
                )
            else:
                inv = self.inventory_repo.find_by_keys(
                    org_id=org_id,
                    item_id=item["_id"],
                    location_id=src_loc_id,
                    lot_number=lot_number,
                    serial_number=None,
                    session=session
                )
                if not inv or inv.get("quantity", 0) < qty:
                    avail = inv.get("quantity", 0) if inv else 0
                    raise ValueError(f"INSUFFICIENT_STOCK: Available stock is {avail}, Requested: {qty}")

                rem_qty = inv["quantity"] - qty
                new_status = "AVAILABLE" if rem_qty > 0 else "DEPLETED"
                self.inventory_repo.update_one(
                    {"_id": inv["_id"]},
                    {"$set": {"quantity": rem_qty, "status": new_status, "updated_at": now}},
                    session=session
                )

            self.log_transaction(
                org_id=org_id,
                t_id=t_id,
                txn_type="ISSUE",
                item_id=item["_id"],
                quantity=qty,
                from_loc_id=src_loc_id,
                to_loc_id=None,
                performed_by=user_id,
                lot_number=lot_number,
                serial_number=serial_number,
                reference=reference,
                remarks=remarks,
                session=session
            )

            return {
                "operation": "ISSUE",
                "t_id": t_id,
                "item_id": item["_id"],
                "part_id": item["_id"],
                "location_code": src_loc["location_code"],
                "quantity": qty,
                "remaining_quantity": rem_qty if not serial_number else 0
            }

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()

    def transfer(self, data: dict, user_id: str, org_id: str = "ORG-001"):
        def _execute(session=None):
            item_identifier = data.get("item_id") or data.get("part_id")
            item = self.item_repo.find_one({"_id": item_identifier, "organization_id": org_id}, session=session)
            if not item:
                item = self.item_repo.find_by_code(org_id, item_identifier, session=session)
            if not item:
                raise ValueError(f"Item '{item_identifier}' does not exist")

            src_loc = self.resolve_location(
                org_id=org_id,
                loc_id=data.get("from_location_id"),
                loc_code=data.get("from_location_code"),
                nfc_uid=data.get("from_nfc_uid") or data.get("from_nfc_tag_uid"),
                session=session
            )
            dest_loc = self.resolve_location(
                org_id=org_id,
                loc_id=data.get("to_location_id"),
                loc_code=data.get("to_location_code"),
                nfc_uid=data.get("to_nfc_uid") or data.get("to_nfc_tag_uid"),
                session=session
            )

            if src_loc["_id"] == dest_loc["_id"]:
                raise ValueError("Source and destination locations must be different")

            qty = float(data["quantity"])
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero")

            lot_number = (data.get("lot_number") or data.get("lot_id") or "").strip() or None
            serial_number = (data.get("serial_number") or "").strip() or None
            reference = data.get("reference") or {}
            remarks = data.get("remarks") or data.get("description") or "Material transfer"

            t_id = SequenceCounter.get_next_id("transaction", session=session)
            now = datetime.now(timezone.utc).isoformat()

            if serial_number:
                inv = self.inventory_repo.find_by_keys(
                    org_id=org_id,
                    item_id=item["_id"],
                    location_id=src_loc["_id"],
                    lot_number=lot_number,
                    serial_number=serial_number,
                    session=session
                )
                if not inv or inv.get("status") != "AVAILABLE":
                    raise ValueError(f"Serial '{serial_number}' is not available at origin location '{src_loc['location_code']}'")

                self.inventory_repo.update_one(
                    {"_id": inv["_id"]},
                    {"$set": {"location_id": dest_loc["_id"], "updated_at": now}},
                    session=session
                )
            else:
                src_inv = self.inventory_repo.find_by_keys(
                    org_id=org_id,
                    item_id=item["_id"],
                    location_id=src_loc["_id"],
                    lot_number=lot_number,
                    serial_number=None,
                    session=session
                )
                if not src_inv or src_inv.get("quantity", 0) < qty:
                    avail = src_inv.get("quantity", 0) if src_inv else 0
                    raise ValueError(f"Insufficient stock at '{src_loc['location_code']}'. Available: {avail}, Transfer: {qty}")

                rem_qty = src_inv["quantity"] - qty
                new_status = "AVAILABLE" if rem_qty > 0 else "DEPLETED"
                self.inventory_repo.update_one(
                    {"_id": src_inv["_id"]},
                    {"$set": {"quantity": rem_qty, "status": new_status, "updated_at": now}},
                    session=session
                )

                dest_inv = self.inventory_repo.find_by_keys(
                    org_id=org_id,
                    item_id=item["_id"],
                    location_id=dest_loc["_id"],
                    lot_number=lot_number,
                    serial_number=None,
                    session=session
                )
                if dest_inv:
                    self.inventory_repo.update_one(
                        {"_id": dest_inv["_id"]},
                        {"$inc": {"quantity": qty}, "$set": {"status": "AVAILABLE", "updated_at": now}},
                        session=session
                    )
                else:
                    new_inv_id = SequenceCounter.get_next_id("inventory", session=session)
                    self.inventory_repo.insert_one({
                        "_id": new_inv_id,
                        "organization_id": org_id,
                        "item_id": item["_id"],
                        "part_id": item["_id"],
                        "location_id": dest_loc["_id"],
                        "lot_number": lot_number,
                        "serial_number": None,
                        "quantity": qty,
                        "site_id": src_inv.get("site_id", "SITE-001"),
                        "vendor_id": src_inv.get("vendor_id"),
                        "status": "AVAILABLE",
                        "created_at": now,
                        "updated_at": now
                    }, session=session)

            self.log_transaction(
                org_id=org_id,
                t_id=t_id,
                txn_type="TRANSFER",
                item_id=item["_id"],
                quantity=qty,
                from_loc_id=src_loc["_id"],
                to_loc_id=dest_loc["_id"],
                performed_by=user_id,
                lot_number=lot_number,
                serial_number=serial_number,
                reference=reference,
                remarks=remarks,
                session=session
            )

            return {
                "operation": "TRANSFER",
                "t_id": t_id,
                "item_id": item["_id"],
                "part_id": item["_id"],
                "from_location": src_loc["location_code"],
                "from_location_code": src_loc["location_code"],
                "to_location": dest_loc["location_code"],
                "to_location_code": dest_loc["location_code"],
                "quantity": qty
            }

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()

    def transfer_cell(self, data: dict, user_id: str, org_id: str = "ORG-001"):
        serial = (data.get("serial_number") or data.get("cell_serial_no") or data.get("cell_id") or "").strip()
        if not serial:
            raise ValueError("Serial number is required for cell transfer")

        inv = self.inventory_repo.find_by_serial(org_id, serial)
        if not inv:
            raise ValueError(f"Serial '{serial}' not found in active inventory")

        transfer_payload = {
            "item_id": inv["item_id"],
            "from_location_id": inv["location_id"],
            "to_location_id": data.get("to_location_id"),
            "to_location_code": data.get("to_location_code"),
            "to_nfc_uid": data.get("to_nfc_uid") or data.get("to_nfc_tag_uid"),
            "quantity": 1.0,
            "serial_number": serial,
            "lot_number": inv.get("lot_number"),
            "reference": data.get("reference") or {"reference_id": data.get("reference_id")},
            "remarks": data.get("remarks") or data.get("description") or f"Transferred cell {serial}"
        }
        return self.transfer(transfer_payload, user_id=user_id, org_id=org_id)

    def reserve(self, data: dict, user_id: str, org_id: str = "ORG-001"):
        def _execute(session=None):
            item_identifier = data.get("item_id") or data.get("part_id")
            item = self.item_repo.find_one({"_id": item_identifier, "organization_id": org_id}, session=session)
            if not item:
                item = self.item_repo.find_by_code(org_id, item_identifier, session=session)
            if not item:
                raise ValueError(f"Item '{item_identifier}' does not exist")

            loc_id = data.get("location_id")
            lot_number = data.get("lot_number") or data.get("lot_id")
            qty = float(data["quantity"])
            reserved_for = data.get("reserved_for", "WORK_ORDER")

            inv = None
            if data.get("inventory_id"):
                inv = self.inventory_repo.find_one({"_id": data["inventory_id"], "organization_id": org_id}, session=session)
            elif loc_id and lot_number:
                inv = self.inventory_repo.find_by_keys(org_id=org_id, item_id=item["_id"], location_id=loc_id, lot_number=lot_number, serial_number=None, session=session)
            elif loc_id:
                inv = self.inventory_repo.find_one({"organization_id": org_id, "item_id": item["_id"], "location_id": loc_id}, session=session)
            elif lot_number:
                inv = self.inventory_repo.find_one({"organization_id": org_id, "item_id": item["_id"], "lot_number": lot_number}, session=session)

            if not inv:
                raise ValueError("Inventory record not found for reservation")

            curr_qty = inv.get("quantity", 0)
            curr_reserved = inv.get("reserved_quantity", 0)
            avail_qty = curr_qty - curr_reserved

            if avail_qty < qty:
                raise ValueError(f"INSUFFICIENT_STOCK: Available to reserve: {avail_qty}, Requested: {qty}")

            new_reserved = curr_reserved + qty
            now = datetime.now(timezone.utc).isoformat()
            t_id = SequenceCounter.get_next_id("transaction", session=session)

            self.inventory_repo.update_one(
                {"_id": inv["_id"]},
                {
                    "$set": {
                        "reserved_quantity": new_reserved,
                        "available_quantity": curr_qty - new_reserved,
                        "reserved_by": user_id,
                        "reserved_for": reserved_for,
                        "updated_at": now
                    }
                },
                session=session
            )

            self.log_transaction(
                org_id=org_id,
                t_id=t_id,
                txn_type="RESERVE",
                item_id=item["_id"],
                quantity=qty,
                from_loc_id=inv["location_id"],
                to_loc_id=None,
                performed_by=user_id,
                lot_number=lot_number,
                reference={"reserved_for": reserved_for},
                remarks=data.get("remarks", f"Reserved {qty} for {reserved_for}"),
                session=session
            )

            return {
                "operation": "RESERVE",
                "t_id": t_id,
                "inventory_id": inv["_id"],
                "item_id": item["_id"],
                "part_id": item["_id"],
                "reserved_quantity": new_reserved,
                "quantity": qty,
                "reserved_for": reserved_for
            }

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()

    def release(self, data: dict, user_id: str, org_id: str = "ORG-001"):
        def _execute(session=None):
            item_identifier = data.get("item_id") or data.get("part_id")
            item = self.item_repo.find_one({"_id": item_identifier, "organization_id": org_id}, session=session)
            if not item:
                item = self.item_repo.find_by_code(org_id, item_identifier, session=session)
            if not item:
                raise ValueError(f"Item '{item_identifier}' does not exist")

            loc_id = data.get("location_id")
            lot_number = data.get("lot_number") or data.get("lot_id")
            qty = float(data["quantity"])

            inv = None
            if data.get("inventory_id"):
                inv = self.inventory_repo.find_one({"_id": data["inventory_id"], "organization_id": org_id}, session=session)
            elif loc_id and lot_number:
                inv = self.inventory_repo.find_by_keys(org_id=org_id, item_id=item["_id"], location_id=loc_id, lot_number=lot_number, serial_number=None, session=session)
            elif loc_id:
                inv = self.inventory_repo.find_one({"organization_id": org_id, "item_id": item["_id"], "location_id": loc_id}, session=session)
            elif lot_number:
                inv = self.inventory_repo.find_one({"organization_id": org_id, "item_id": item["_id"], "lot_number": lot_number}, session=session)

            if not inv:
                raise ValueError("Inventory record not found for release")

            curr_qty = inv.get("quantity", 0)
            curr_reserved = inv.get("reserved_quantity", 0)

            if curr_reserved < qty:
                raise ValueError(f"Cannot release {qty}: only {curr_reserved} currently reserved")

            rem_reserved = curr_reserved - qty
            now = datetime.now(timezone.utc).isoformat()
            t_id = SequenceCounter.get_next_id("transaction", session=session)

            self.inventory_repo.update_one(
                {"_id": inv["_id"]},
                {
                    "$set": {
                        "reserved_quantity": rem_reserved,
                        "available_quantity": curr_qty - rem_reserved,
                        "updated_at": now
                    }
                },
                session=session
            )

            self.log_transaction(
                org_id=org_id,
                t_id=t_id,
                txn_type="RELEASE",
                item_id=item["_id"],
                quantity=qty,
                from_loc_id=inv["location_id"],
                to_loc_id=None,
                performed_by=user_id,
                lot_number=lot_number,
                remarks=data.get("remarks", f"Released {qty} reserved stock"),
                session=session
            )

            return {
                "operation": "RELEASE",
                "t_id": t_id,
                "inventory_id": inv["_id"],
                "item_id": item["_id"],
                "part_id": item["_id"],
                "released_quantity": qty,
                "remaining_reserved": rem_reserved
            }

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()

