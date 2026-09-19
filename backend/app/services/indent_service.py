from datetime import datetime, timezone
from app.config.database import Database
from app.models.counter import SequenceCounter
from app.repositories.indent_repository import IndentRepository
from app.repositories.indent_return_repository import IndentReturnRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.transaction_repository import TransactionRepository

class IndentService:
    def __init__(self):
        self.indent_repo = IndentRepository()
        self.return_repo = IndentReturnRepository()
        self.item_repo = ItemRepository()
        self.project_repo = ProjectRepository()
        self.user_repo = UserRepository()
        self.location_repo = LocationRepository()
        self.inventory_repo = InventoryRepository()
        self.txn_repo = TransactionRepository()

    def resolve_location(self, org_id: str, loc_id: str = None, loc_code: str = None, session=None):
        loc = None
        if loc_id:
            loc = self.location_repo.find_one({"_id": loc_id, "organization_id": org_id}, session=session)
            if not loc:
                loc = self.location_repo.find_by_code(org_id, loc_id, session=session)
        elif loc_code:
            loc = self.location_repo.find_by_code(org_id, loc_code.strip(), session=session)

        if not loc:
            raise ValueError("Location could not be resolved from provided ID or Code")
        return loc

    def create_indent(self, data: dict, user: dict, org_id: str = "ORG-001"):
        now = datetime.now(timezone.utc).isoformat()
        indent_id = SequenceCounter.get_next_id("indent")

        # 1. Resolve Project
        project_id = (data.get("project_id") or "").strip()
        project = self.project_repo.find_by_project_id(org_id, project_id) or self.project_repo.find_by_id(project_id)
        project_name = project.get("project_desc") or project_id if project else project_id

        # 2. Resolve Project Head
        project_head_id = (data.get("project_head_id") or "").strip()
        project_head = self.user_repo.find_by_id(project_head_id) or self.user_repo.find_by_username_or_email(project_head_id, org_id)
        project_head_name = project_head.get("name") or project_head.get("username") if project_head else project_head_id
        actual_head_id = project_head["_id"] if project_head else project_head_id

        # 3. Validate & format items
        formatted_items = []
        for idx, item_req in enumerate(data.get("items", [])):
            part_identifier = item_req.get("part_id") or item_req.get("item_id")
            part = self.item_repo.find_one({"_id": part_identifier, "organization_id": org_id})
            if not part:
                part = self.item_repo.find_by_code(org_id, part_identifier)
            if not part:
                part = self.item_repo.find_by_id(part_identifier)
            if not part:
                part = self.item_repo.find_one({
                    "$or": [
                        {"_id": part_identifier},
                        {"code": str(part_identifier).strip().upper()},
                        {"part_code": str(part_identifier).strip().upper()}
                    ]
                })
            if not part:
                raise ValueError(f"Part/Item '{part_identifier}' at line {idx+1} not found")

            qty = float(item_req.get("requested_quantity") or item_req.get("quantity") or 0)
            if qty <= 0:
                raise ValueError(f"Requested quantity for part '{part.get('code')}' must be > 0")

            formatted_items.append({
                "item_id": part["_id"],
                "part_id": part["_id"],
                "item_code": part.get("code", ""),
                "part_code": part.get("code", ""),
                "item_name": part.get("name", ""),
                "part_name": part.get("name", ""),
                "requested_quantity": qty,
                "issued_quantity": 0.0,
                "returned_quantity": 0.0,
                "status": "PENDING",
                "notes": item_req.get("notes", "")
            })

        indent_doc = {
            "_id": indent_id,
            "indent_number": indent_id,
            "organization_id": org_id,
            "site_id": data.get("site_id") or user.get("site_id"),
            "project_id": project_id,
            "project_name": project_name,
            "requester_id": user.get("_id") or user.get("user_id"),
            "requester_name": user.get("name") or user.get("username", "Unknown"),
            "requester_email": user.get("email", ""),
            "project_head_id": actual_head_id,
            "project_head_name": project_head_name,
            "required_by_date": data.get("required_by_date"),
            "priority": data.get("priority", "MEDIUM"),
            "purpose": data.get("purpose", ""),
            "status": "PENDING_APPROVAL" if data.get("status") != "DRAFT" else "DRAFT",
            "items": formatted_items,
            "notes": data.get("notes", ""),
            "approval": None,
            "rejection": None,
            "issue_history": [],
            "created_at": now,
            "updated_at": now
        }

        self.indent_repo.insert_one(indent_doc)
        return indent_doc

    def get_all_indents(self, filters: dict = None, page: int = 1, per_page: int = 50,
                        sort_by: str = "created_at", sort_dir: int = -1, org_id: str = "ORG-001"):
        query = {"organization_id": org_id}
        filters = filters or {}

        if filters.get("status"):
            query["status"] = filters["status"].upper()
        if filters.get("project_id"):
            query["project_id"] = filters["project_id"]
        if filters.get("requester_id"):
            query["requester_id"] = filters["requester_id"]
        if filters.get("project_head_id"):
            query["project_head_id"] = filters["project_head_id"]
        if filters.get("priority"):
            query["priority"] = filters["priority"].upper()
        if filters.get("site_id"):
            query["site_id"] = filters["site_id"]
        if filters.get("q"):
            q_str = str(filters["q"]).strip()
            query["$or"] = [
                {"indent_number": {"$regex": q_str, "$options": "i"}},
                {"project_id": {"$regex": q_str, "$options": "i"}},
                {"project_name": {"$regex": q_str, "$options": "i"}},
                {"requester_name": {"$regex": q_str, "$options": "i"}},
                {"purpose": {"$regex": q_str, "$options": "i"}}
            ]

        total = self.indent_repo.count(query)
        skip = (page - 1) * per_page
        items = self.indent_repo.find_all(query, sort_by=[(sort_by, sort_dir)], skip=skip, limit=per_page)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if per_page > 0 else 1
        }

    def get_indent_by_id(self, indent_id: str, org_id: str = "ORG-001"):
        indent = self.indent_repo.find_one({
            "organization_id": org_id,
            "$or": [{"_id": indent_id}, {"indent_number": indent_id}]
        })
        if not indent:
            raise ValueError(f"Indent '{indent_id}' not found")

        # Fetch linked returns
        returns = self.return_repo.find_all({"indent_id": indent["_id"]})
        indent["returns"] = returns
        return indent

    def update_indent(self, indent_id: str, data: dict, user: dict, org_id: str = "ORG-001"):
        indent = self.get_indent_by_id(indent_id, org_id)
        if indent.get("status") not in ["DRAFT", "PENDING_APPROVAL"]:
            raise ValueError(f"Cannot update indent with status '{indent.get('status')}'")

        updates = {}
        now = datetime.now(timezone.utc).isoformat()

        if "project_id" in data:
            project_id = data["project_id"].strip()
            project = self.project_repo.find_by_project_id(org_id, project_id) or self.project_repo.find_by_id(project_id)
            updates["project_id"] = project_id
            updates["project_name"] = project.get("project_desc") or project_id if project else project_id

        if "project_head_id" in data:
            head_id = data["project_head_id"].strip()
            project_head = self.user_repo.find_by_id(head_id) or self.user_repo.find_by_username_or_email(head_id, org_id)
            updates["project_head_id"] = project_head["_id"] if project_head else head_id
            updates["project_head_name"] = project_head.get("name") or project_head.get("username") if project_head else head_id

        if "required_by_date" in data:
            updates["required_by_date"] = data["required_by_date"]
        if "priority" in data:
            updates["priority"] = data["priority"]
        if "purpose" in data:
            updates["purpose"] = data["purpose"]
        if "notes" in data:
            updates["notes"] = data["notes"]

        if "items" in data:
            formatted_items = []
            for idx, item_req in enumerate(data.get("items", [])):
                part_identifier = item_req.get("part_id") or item_req.get("item_id")
                part = self.item_repo.find_one({"_id": part_identifier, "organization_id": org_id})
                if not part:
                    part = self.item_repo.find_by_code(org_id, part_identifier)
                if not part:
                    raise ValueError(f"Part/Item '{part_identifier}' at line {idx+1} not found")

                qty = float(item_req.get("requested_quantity") or item_req.get("quantity") or 0)
                if qty <= 0:
                    raise ValueError(f"Requested quantity for part '{part.get('code')}' must be > 0")

                formatted_items.append({
                    "item_id": part["_id"],
                    "part_id": part["_id"],
                    "item_code": part.get("code", ""),
                    "part_code": part.get("code", ""),
                    "item_name": part.get("name", ""),
                    "part_name": part.get("name", ""),
                    "requested_quantity": qty,
                    "issued_quantity": 0.0,
                    "returned_quantity": 0.0,
                    "status": "PENDING",
                    "notes": item_req.get("notes", "")
                })
            updates["items"] = formatted_items

        updates["updated_at"] = now
        self.indent_repo.update_one({"_id": indent["_id"]}, {"$set": updates})
        return self.get_indent_by_id(indent["_id"], org_id)

    def submit_indent(self, indent_id: str, user: dict, org_id: str = "ORG-001"):
        indent = self.get_indent_by_id(indent_id, org_id)
        if indent.get("status") != "DRAFT":
            raise ValueError(f"Only DRAFT indents can be submitted. Current status: '{indent.get('status')}'")

        now = datetime.now(timezone.utc).isoformat()
        self.indent_repo.update_one(
            {"_id": indent["_id"]},
            {"$set": {"status": "PENDING_APPROVAL", "updated_at": now}}
        )
        return self.get_indent_by_id(indent["_id"], org_id)

    def approve_indent(self, indent_id: str, approval_data: dict, user: dict, org_id: str = "ORG-001"):
        indent = self.get_indent_by_id(indent_id, org_id)
        if indent.get("status") != "PENDING_APPROVAL":
            raise ValueError(f"Indent status must be PENDING_APPROVAL to approve. Current: '{indent.get('status')}'")

        now = datetime.now(timezone.utc).isoformat()
        approval_doc = {
            "approved_by": user.get("_id") or user.get("user_id"),
            "approved_by_name": user.get("name") or user.get("username", "Approver"),
            "approved_at": now,
            "comments": approval_data.get("comments", "Approved")
        }

        self.indent_repo.update_one(
            {"_id": indent["_id"]},
            {"$set": {
                "status": "APPROVED",
                "approval": approval_doc,
                "rejection": None,
                "updated_at": now
            }}
        )
        return self.get_indent_by_id(indent["_id"], org_id)

    def reject_indent(self, indent_id: str, reject_data: dict, user: dict, org_id: str = "ORG-001"):
        indent = self.get_indent_by_id(indent_id, org_id)
        if indent.get("status") != "PENDING_APPROVAL":
            raise ValueError(f"Indent status must be PENDING_APPROVAL to reject. Current: '{indent.get('status')}'")

        now = datetime.now(timezone.utc).isoformat()
        rejection_doc = {
            "rejected_by": user.get("_id") or user.get("user_id"),
            "rejected_by_name": user.get("name") or user.get("username", "Reviewer"),
            "rejected_at": now,
            "reason": reject_data.get("reason", "Rejected")
        }

        self.indent_repo.update_one(
            {"_id": indent["_id"]},
            {"$set": {
                "status": "REJECTED",
                "rejection": rejection_doc,
                "updated_at": now
            }}
        )
        return self.get_indent_by_id(indent["_id"], org_id)

    def issue_stock(self, indent_id: str, issue_data: dict, user: dict, org_id: str = "ORG-001"):
        indent = self.get_indent_by_id(indent_id, org_id)
        if indent.get("status") not in ["APPROVED", "PARTIALLY_ISSUED"]:
            raise ValueError(f"Cannot issue stock for indent with status '{indent.get('status')}'. Must be APPROVED or PARTIALLY_ISSUED.")

        def _execute(session=None):
            now = datetime.now(timezone.utc).isoformat()
            items_state = {item["part_id"]: dict(item) for item in indent.get("items", [])}
            # Also map by item_id
            for item in indent.get("items", []):
                if item.get("item_id"):
                    items_state[item["item_id"]] = items_state[item["part_id"]]

            issue_records = []
            for issue_item in issue_data.get("items", []):
                part_identifier = issue_item.get("part_id") or issue_item.get("item_id")
                part = self.item_repo.find_one({"_id": part_identifier, "organization_id": org_id}, session=session)
                if not part:
                    part = self.item_repo.find_by_code(org_id, part_identifier, session=session)
                if not part:
                    raise ValueError(f"Part '{part_identifier}' not found")

                part_id = part["_id"]
                if part_id not in items_state:
                    raise ValueError(f"Part '{part.get('code')}' is not in this indent request")

                indent_item = items_state[part_id]
                qty_to_issue = float(issue_item.get("issued_quantity") or issue_item.get("quantity") or 0)
                if qty_to_issue <= 0:
                    raise ValueError(f"Issue quantity must be > 0 for part '{part.get('code')}'")

                rem_needed = indent_item["requested_quantity"] - indent_item.get("issued_quantity", 0)
                if qty_to_issue > rem_needed:
                    raise ValueError(f"Cannot issue {qty_to_issue} for '{part.get('code')}'. Remaining unissued quantity is {rem_needed}")

                lot_number = (issue_item.get("lot_number") or issue_item.get("lot_id") or "").strip() or None
                if lot_number in ["DEFAULT", "STANDARD / NO LOT", ""]:
                    lot_number = None

                # Resolve source location
                loc_id_req = issue_item.get("location_id")
                loc_code_req = issue_item.get("location_code")
                src_loc = None
                if loc_id_req or loc_code_req:
                    try:
                        src_loc = self.resolve_location(
                            org_id=org_id,
                            loc_id=loc_id_req,
                            loc_code=loc_code_req,
                            session=session
                        )
                    except Exception:
                        src_loc = None

                # If location not resolved, auto-detect location from inventory holding this part/lot
                if not src_loc:
                    match_q = {"organization_id": org_id, "item_id": part_id, "quantity": {"$gte": qty_to_issue}}
                    if lot_number:
                        match_q["lot_number"] = lot_number
                    inv_match = self.inventory_repo.find_one(match_q, session=session)
                    if not inv_match:
                        match_fallback = {"organization_id": org_id, "item_id": part_id, "quantity": {"$gt": 0}}
                        if lot_number:
                            match_fallback["lot_number"] = lot_number
                        inv_match = self.inventory_repo.find_one(match_fallback, session=session)
                    
                    if inv_match and inv_match.get("location_id"):
                        src_loc = self.location_repo.find_by_id(inv_match["location_id"], session=session)

                if not src_loc:
                    raise ValueError(f"Could not resolve source location with available stock for part '{part.get('code')}'")

                src_loc_id = src_loc["_id"]
                serials = issue_item.get("cell_serial_numbers") or []

                # Deduct stock
                if serials:
                    for s_no in serials:
                        inv = self.inventory_repo.find_by_keys(
                            org_id=org_id,
                            item_id=part_id,
                            location_id=src_loc_id,
                            lot_number=lot_number,
                            serial_number=s_no,
                            session=session
                        )
                        if not inv or inv.get("status") != "AVAILABLE":
                            raise ValueError(f"Serial '{s_no}' not available at location '{src_loc.get('location_code')}'")
                        self.inventory_repo.update_one(
                            {"_id": inv["_id"]},
                            {"$set": {"status": "ISSUED", "quantity": 0.0, "updated_at": now}},
                            session=session
                        )
                else:
                    inv = None
                    if lot_number:
                        inv = self.inventory_repo.find_by_keys(
                            org_id=org_id,
                            item_id=part_id,
                            location_id=src_loc_id,
                            lot_number=lot_number,
                            serial_number=None,
                            session=session
                        )
                    if not inv:
                        inv = self.inventory_repo.find_one({
                            "organization_id": org_id,
                            "item_id": part_id,
                            "location_id": src_loc_id,
                            "quantity": {"$gte": qty_to_issue}
                        }, session=session) or self.inventory_repo.find_one({
                            "organization_id": org_id,
                            "item_id": part_id,
                            "location_id": src_loc_id
                        }, session=session)

                    if not inv or inv.get("quantity", 0) < qty_to_issue:
                        avail = inv.get("quantity", 0) if inv else 0
                        raise ValueError(f"INSUFFICIENT_STOCK: Available stock for '{part.get('code')}' at '{src_loc.get('location_code')}' is {avail}, Requested: {qty_to_issue}")

                    rem_stock = inv["quantity"] - qty_to_issue
                    new_inv_status = "AVAILABLE" if rem_stock > 0 else "DEPLETED"
                    self.inventory_repo.update_one(
                        {"_id": inv["_id"]},
                        {"$set": {"quantity": rem_stock, "status": new_inv_status, "updated_at": now}},
                        session=session
                    )

                # Log Transaction
                txn_id = SequenceCounter.get_next_id("transaction", session=session)
                txn_doc = {
                    "_id": txn_id,
                    "t_id": txn_id,
                    "organization_id": org_id,
                    "transaction_type": "INDENT_ISSUE",
                    "item_id": part_id,
                    "part_id": part_id,
                    "lot_number": lot_number,
                    "lot_batch_no": lot_number,
                    "serial_number": serials[0] if serials else None,
                    "quantity": qty_to_issue,
                    "from_location_id": src_loc_id,
                    "to_location_id": None,
                    "performed_by": user.get("_id") or user.get("user_id"),
                    "reference": {
                        "indent_id": indent["_id"],
                        "indent_number": indent.get("indent_number"),
                        "project_id": indent.get("project_id"),
                        "requester_id": indent.get("requester_id")
                    },
                    "timestamp": now,
                    "remarks": issue_data.get("comments") or f"Indent {indent.get('indent_number')} issue to project {indent.get('project_id')}"
                }
                self.txn_repo.insert_one(txn_doc, session=session)

                # Update item state
                indent_item["issued_quantity"] = indent_item.get("issued_quantity", 0) + qty_to_issue
                if indent_item["issued_quantity"] >= indent_item["requested_quantity"]:
                    indent_item["status"] = "FULLY_ISSUED"
                else:
                    indent_item["status"] = "PARTIALLY_ISSUED"

                issue_records.append({
                    "part_id": part_id,
                    "part_code": part.get("code"),
                    "issued_quantity": qty_to_issue,
                    "location_id": src_loc_id,
                    "location_code": src_loc.get("location_code"),
                    "lot_number": lot_number,
                    "cell_serial_numbers": serials,
                    "transaction_id": txn_id
                })

            # Recalculate Indent Status
            all_items = list({it["part_id"]: it for it in items_state.values()}.values())
            all_fully_issued = all(it.get("issued_quantity", 0) >= it.get("requested_quantity", 0) for it in all_items)
            any_issued = any(it.get("issued_quantity", 0) > 0 for it in all_items)
            new_indent_status = "ISSUED" if all_fully_issued else ("PARTIALLY_ISSUED" if any_issued else indent.get("status"))

            history_entry = {
                "issued_by": user.get("_id") or user.get("user_id"),
                "issued_by_name": user.get("name") or user.get("username", "Store Keeper"),
                "issued_at": now,
                "comments": issue_data.get("comments", ""),
                "items": issue_records
            }

            self.indent_repo.update_one(
                {"_id": indent["_id"]},
                {
                    "$set": {
                        "status": new_indent_status,
                        "items": all_items,
                        "updated_at": now
                    },
                    "$push": {"issue_history": history_entry}
                },
                session=session
            )

            return self.get_indent_by_id(indent["_id"], org_id)

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()

    def close_indent(self, indent_id: str, user: dict, notes: str = None, org_id: str = "ORG-001"):
        indent = self.get_indent_by_id(indent_id, org_id)
        now = datetime.now(timezone.utc).isoformat()
        self.indent_repo.update_one(
            {"_id": indent["_id"]},
            {"$set": {
                "status": "CLOSED",
                "closed_by": user.get("_id") or user.get("user_id"),
                "closed_at": now,
                "closure_notes": notes or "Closed by user",
                "updated_at": now
            }}
        )
        return self.get_indent_by_id(indent["_id"], org_id)

    # --- Indent Returns ---
    def create_return(self, data: dict, user: dict, org_id: str = "ORG-001"):
        now = datetime.now(timezone.utc).isoformat()
        indent_id = data.get("indent_id")
        indent = self.get_indent_by_id(indent_id, org_id)

        if indent.get("status") not in ["ISSUED", "PARTIALLY_ISSUED", "APPROVED"]:
            raise ValueError(f"Cannot raise return for indent with status '{indent.get('status')}'")

        return_id = SequenceCounter.get_next_id("indent_return")

        indent_items_map = {item["part_id"]: item for item in indent.get("items", [])}
        for item in indent.get("items", []):
            if item.get("item_id"):
                indent_items_map[item["item_id"]] = indent_items_map[item["part_id"]]

        formatted_return_items = []
        for idx, ret_item in enumerate(data.get("items", [])):
            part_identifier = ret_item.get("part_id") or ret_item.get("item_id")
            part = self.item_repo.find_one({"_id": part_identifier, "organization_id": org_id})
            if not part:
                part = self.item_repo.find_by_code(org_id, part_identifier)
            if not part:
                raise ValueError(f"Part '{part_identifier}' at line {idx+1} not found")

            part_id = part["_id"]
            if part_id not in indent_items_map:
                raise ValueError(f"Part '{part.get('code')}' was not in indent '{indent.get('indent_number')}'")

            indent_item = indent_items_map[part_id]
            qty_to_return = float(ret_item.get("returned_quantity") or ret_item.get("quantity") or 0)
            if qty_to_return <= 0:
                raise ValueError(f"Return quantity must be > 0 for '{part.get('code')}'")

            max_returnable = indent_item.get("issued_quantity", 0) - indent_item.get("returned_quantity", 0)
            if qty_to_return > max_returnable:
                raise ValueError(f"Return quantity {qty_to_return} exceeds returnable quantity {max_returnable} for '{part.get('code')}'")

            formatted_return_items.append({
                "item_id": part_id,
                "part_id": part_id,
                "item_code": part.get("code", ""),
                "part_code": part.get("code", ""),
                "item_name": part.get("name", ""),
                "part_name": part.get("name", ""),
                "returned_quantity": qty_to_return,
                "condition": ret_item.get("condition", "GOOD"),
                "reason": ret_item.get("reason", ""),
                "cell_serial_numbers": ret_item.get("cell_serial_numbers", [])
            })

        return_doc = {
            "_id": return_id,
            "return_number": return_id,
            "organization_id": org_id,
            "indent_id": indent["_id"],
            "indent_number": indent.get("indent_number"),
            "project_id": indent.get("project_id"),
            "requester_id": user.get("_id") or user.get("user_id"),
            "requester_name": user.get("name") or user.get("username", "Requester"),
            "status": "PENDING_INSPECTION",
            "items": formatted_return_items,
            "reason": data.get("reason", ""),
            "remarks": data.get("remarks", ""),
            "inspection": None,
            "created_at": now,
            "updated_at": now
        }

        self.return_repo.insert_one(return_doc)
        return return_doc

    def get_all_returns(self, filters: dict = None, page: int = 1, per_page: int = 50,
                        sort_by: str = "created_at", sort_dir: int = -1, org_id: str = "ORG-001"):
        query = {"organization_id": org_id}
        filters = filters or {}

        if filters.get("status"):
            query["status"] = filters["status"].upper()
        if filters.get("indent_id"):
            query["indent_id"] = filters["indent_id"]
        if filters.get("requester_id"):
            query["requester_id"] = filters["requester_id"]
        if filters.get("q"):
            q_str = str(filters["q"]).strip()
            query["$or"] = [
                {"return_number": {"$regex": q_str, "$options": "i"}},
                {"indent_number": {"$regex": q_str, "$options": "i"}},
                {"project_id": {"$regex": q_str, "$options": "i"}},
                {"requester_name": {"$regex": q_str, "$options": "i"}}
            ]

        total = self.return_repo.count(query)
        skip = (page - 1) * per_page
        items = self.return_repo.find_all(query, sort_by=[(sort_by, sort_dir)], skip=skip, limit=per_page)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if per_page > 0 else 1
        }

    def get_return_by_id(self, return_id: str, org_id: str = "ORG-001"):
        ret = self.return_repo.find_one({
            "organization_id": org_id,
            "$or": [{"_id": return_id}, {"return_number": return_id}]
        })
        if not ret:
            raise ValueError(f"Return request '{return_id}' not found")
        return ret

    def accept_return(self, return_id: str, accept_data: dict, user: dict, org_id: str = "ORG-001"):
        ret = self.get_return_by_id(return_id, org_id)
        if ret.get("status") != "PENDING_INSPECTION":
            raise ValueError(f"Return status must be PENDING_INSPECTION. Current: '{ret.get('status')}'")

        def _execute(session=None):
            now = datetime.now(timezone.utc).isoformat()
            decision = (accept_data.get("status") or "ACCEPTED").upper()

            if decision == "REJECTED":
                self.return_repo.update_one(
                    {"_id": ret["_id"]},
                    {"$set": {
                        "status": "REJECTED",
                        "inspection": {
                            "inspected_by": user.get("_id") or user.get("user_id"),
                            "inspected_by_name": user.get("name") or user.get("username", "Store Keeper"),
                            "inspected_at": now,
                            "inspection_notes": accept_data.get("inspection_notes", "Return rejected")
                        },
                        "updated_at": now
                    }},
                    session=session
                )
                return self.get_return_by_id(ret["_id"], org_id)

            # Accept items and restock GOOD items
            items_input = {it["part_id"]: it for it in accept_data.get("items", [])}
            indent = self.indent_repo.find_by_id(ret["indent_id"], session=session)
            indent_items = indent.get("items", []) if indent else []
            indent_items_map = {it["part_id"]: it for it in indent_items}

            processed_items = []
            for ret_item in ret.get("items", []):
                part_id = ret_item["part_id"]
                custom_accept = items_input.get(part_id, {})
                condition = custom_accept.get("condition") or ret_item.get("condition", "GOOD")
                qty = float(custom_accept.get("accepted_quantity") or ret_item.get("returned_quantity", 0))

                restock_loc_id = None
                if condition == "GOOD":
                    restock_loc = self.resolve_location(
                        org_id=org_id,
                        loc_id=custom_accept.get("restock_location_id") or accept_data.get("restock_location_id"),
                        loc_code=custom_accept.get("restock_location_code") or accept_data.get("restock_location_code"),
                        session=session
                    )
                    restock_loc_id = restock_loc["_id"]
                    lot_number = custom_accept.get("lot_id") or custom_accept.get("lot_number") or None

                    # Restock into inventory
                    inv = self.inventory_repo.find_by_keys(
                        org_id=org_id,
                        item_id=part_id,
                        location_id=restock_loc_id,
                        lot_number=lot_number,
                        serial_number=None,
                        session=session
                    )
                    if inv:
                        self.inventory_repo.update_one(
                            {"_id": inv["_id"]},
                            {"$inc": {"quantity": qty}, "$set": {"status": "AVAILABLE", "updated_at": now}},
                            session=session
                        )
                    else:
                        inv_id = SequenceCounter.get_next_id("inventory", session=session)
                        self.inventory_repo.insert_one({
                            "_id": inv_id,
                            "organization_id": org_id,
                            "item_id": part_id,
                            "part_id": part_id,
                            "location_id": restock_loc_id,
                            "lot_number": lot_number,
                            "serial_number": None,
                            "quantity": qty,
                            "status": "AVAILABLE",
                            "created_at": now,
                            "updated_at": now
                        }, session=session)

                    # Log return transaction
                    txn_id = SequenceCounter.get_next_id("transaction", session=session)
                    txn_doc = {
                        "_id": txn_id,
                        "t_id": txn_id,
                        "organization_id": org_id,
                        "transaction_type": "INDENT_RETURN",
                        "item_id": part_id,
                        "part_id": part_id,
                        "lot_number": lot_number,
                        "quantity": qty,
                        "from_location_id": None,
                        "to_location_id": restock_loc_id,
                        "performed_by": user.get("_id") or user.get("user_id"),
                        "reference": {
                            "return_id": ret["_id"],
                            "return_number": ret.get("return_number"),
                            "indent_id": ret.get("indent_id"),
                            "indent_number": ret.get("indent_number"),
                            "condition": condition
                        },
                        "timestamp": now,
                        "remarks": f"Return {ret.get('return_number')} restocked to {restock_loc.get('location_code')}"
                    }
                    self.txn_repo.insert_one(txn_doc, session=session)

                # Update returned_quantity on indent
                if part_id in indent_items_map:
                    indent_items_map[part_id]["returned_quantity"] = indent_items_map[part_id].get("returned_quantity", 0) + qty

                processed_items.append({
                    "part_id": part_id,
                    "accepted_quantity": qty,
                    "condition": condition,
                    "restock_location_id": restock_loc_id
                })

            # Update Indent Items
            if indent:
                self.indent_repo.update_one(
                    {"_id": indent["_id"]},
                    {"$set": {"items": list(indent_items_map.values()), "updated_at": now}},
                    session=session
                )

            # Update Return Doc
            self.return_repo.update_one(
                {"_id": ret["_id"]},
                {"$set": {
                    "status": "ACCEPTED",
                    "inspection": {
                        "inspected_by": user.get("_id") or user.get("user_id"),
                        "inspected_by_name": user.get("name") or user.get("username", "Store Keeper"),
                        "inspected_at": now,
                        "inspection_notes": accept_data.get("inspection_notes", "Return accepted and material inspected"),
                        "processed_items": processed_items
                    },
                    "updated_at": now
                }},
                session=session
            )

            return self.get_return_by_id(ret["_id"], org_id)

        if Database.is_replica_set and Database.get_client():
            with Database.get_client().start_session() as session:
                with session.start_transaction():
                    return _execute(session)
        return _execute()
