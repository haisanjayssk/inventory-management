from marshmallow import Schema, fields as ma_fields, validate, validates_schema, ValidationError, EXCLUDE

class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

# --- Organizations ---
class OrganizationSchema(BaseSchema):
    code = ma_fields.String(required=True, validate=validate.Length(min=1, max=50))
    name = ma_fields.String(required=True, validate=validate.Length(min=1, max=200))
    country = ma_fields.String(allow_none=True, load_default="India")
    site = ma_fields.Raw(allow_none=True, load_default=[]) # JSON array or object
    status = ma_fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE"]), load_default="ACTIVE")

# --- Projects ---
class ProjectSchema(BaseSchema):
    project_id = ma_fields.String(required=True, validate=validate.Length(min=1, max=100))
    project_desc = ma_fields.String(allow_none=True, load_default="")
    responsible_person = ma_fields.String(allow_none=True, load_default="")

# --- Item Types & Fields ---
class ItemTypeFieldSchema(BaseSchema):
    field_name = ma_fields.String(required=True, validate=validate.Length(min=1, max=100))
    field_key = ma_fields.String(required=True, validate=validate.Length(min=1, max=100))
    data_type = ma_fields.String(validate=validate.OneOf(["STRING", "NUMBER", "DECIMAL", "BOOLEAN", "SELECT"]), load_default="STRING")
    unit = ma_fields.String(allow_none=True, load_default=None)
    options = ma_fields.List(ma_fields.String(), allow_none=True, load_default=[])
    required = ma_fields.Boolean(load_default=False)
    active = ma_fields.Boolean(load_default=True)

class ItemTypeSchema(BaseSchema):
    code = ma_fields.String(allow_none=True, load_default=None)
    name = ma_fields.String(allow_none=True, load_default=None)
    part_type_name = ma_fields.String(allow_none=True, load_default=None)
    description = ma_fields.String(allow_none=True, load_default="")
    tracking_mode = ma_fields.String(validate=validate.OneOf(["QUANTITY", "SERIAL", "LOT"]), load_default="QUANTITY")
    fields = ma_fields.List(ma_fields.Nested(ItemTypeFieldSchema), allow_none=True, load_default=[])
    site_id = ma_fields.String(allow_none=True, load_default=None)
    active = ma_fields.Boolean(load_default=True)

    @validates_schema
    def validate_item_type(self, data, **kwargs):
        if not data.get("name") and data.get("part_type_name"):
            data["name"] = data["part_type_name"]
        if not data.get("name"):
            raise ValidationError("Field 'name' or 'part_type_name' is required.", field_name="name")
        if not data.get("code"):
            data["code"] = data["name"].upper().replace(" ", "_")

# Backward-compatibility alias
PartTypeSchema = ItemTypeSchema
PartTypeFieldSchema = ItemTypeFieldSchema

# --- Items ---
class ItemSchema(BaseSchema):
    item_type_id = ma_fields.String(allow_none=True, load_default=None)
    part_type_id = ma_fields.String(allow_none=True, load_default=None)
    code = ma_fields.String(allow_none=True, load_default=None)
    part_code = ma_fields.String(allow_none=True, load_default=None)
    name = ma_fields.String(allow_none=True, load_default=None)
    part_name = ma_fields.String(allow_none=True, load_default=None)
    description = ma_fields.String(allow_none=True, load_default="")
    attributes = ma_fields.Dict(allow_none=True, load_default={})
    package = ma_fields.String(allow_none=True, load_default="")
    mpn = ma_fields.String(allow_none=True, load_default="")
    mfr = ma_fields.String(allow_none=True, load_default="")
    vendor_id = ma_fields.String(allow_none=True, load_default=None)
    site_id = ma_fields.String(allow_none=True, load_default=None)
    active = ma_fields.Boolean(load_default=True)

    @validates_schema
    def validate_names(self, data, **kwargs):
        if not data.get("code") and data.get("part_code"):
            data["code"] = data["part_code"]
        if not data.get("name") and data.get("part_name"):
            data["name"] = data["part_name"]
        if not data.get("item_type_id") and data.get("part_type_id"):
            data["item_type_id"] = data["part_type_id"]
        if not data.get("code"):
            raise ValidationError("Field 'code' or 'part_code' is required.", field_name="code")
        if not data.get("name"):
            raise ValidationError("Field 'name' or 'part_name' is required.", field_name="name")
        if not data.get("item_type_id"):
            raise ValidationError("Field 'item_type_id' or 'part_type_id' is required.", field_name="item_type_id")

# Backward-compatibility alias
PartSchema = ItemSchema

# --- Vendors ---
class VendorSchema(BaseSchema):
    code = ma_fields.String(allow_none=True, load_default=None)
    name = ma_fields.String(allow_none=True, load_default=None)
    vendor_name = ma_fields.String(allow_none=True, load_default=None)
    email = ma_fields.Email(allow_none=True, load_default=None)
    contact = ma_fields.Raw(allow_none=True, load_default={})
    address = ma_fields.Raw(allow_none=True, load_default={})
    country = ma_fields.String(allow_none=True, load_default="India")
    types = ma_fields.Raw(allow_none=True, load_default=[])
    site_id = ma_fields.String(allow_none=True, load_default=None)
    status = ma_fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE", "BLOCKED"]), load_default="ACTIVE")

    @validates_schema
    def validate_vendor(self, data, **kwargs):
        if not data.get("name") and data.get("vendor_name"):
            data["name"] = data["vendor_name"]
        if not data.get("name"):
            raise ValidationError("Field 'name' or 'vendor_name' is required.", field_name="name")

# --- Locations ---
class LocationSchema(BaseSchema):
    location_code = ma_fields.String(required=True, validate=validate.Length(min=1, max=100))
    name = ma_fields.String(allow_none=True, load_default="")
    type = ma_fields.String(allow_none=True, load_default="BIN") # WAREHOUSE, BAY, ROW, RACK, BIN, BOX
    parent_id = ma_fields.String(allow_none=True, load_default=None)
    site_id = ma_fields.String(allow_none=True, load_default=None)
    nfc_uid = ma_fields.String(allow_none=True, load_default=None)
    nfc_tag_uid = ma_fields.String(allow_none=True, load_default=None)
    qr_code = ma_fields.String(allow_none=True, load_default=None)
    warehouse_code = ma_fields.String(allow_none=True, load_default=None)
    bay_number = ma_fields.String(allow_none=True, load_default=None)
    row_number = ma_fields.String(allow_none=True, load_default=None)
    rack_number = ma_fields.String(allow_none=True, load_default=None)
    section_code = ma_fields.String(allow_none=True, load_default=None)
    status = ma_fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE", "MAINTENANCE"]), load_default="ACTIVE")

class BayConfigSchema(BaseSchema):
    bay = ma_fields.String(required=True)
    rows_count = ma_fields.Integer(required=True, validate=validate.Range(min=1, max=20))

class BulkLocationGenerateSchema(BaseSchema):
    warehouse_name = ma_fields.String(required=True, validate=validate.Length(min=2, max=100))
    warehouse_code = ma_fields.String(allow_none=True, load_default=None)
    bays = ma_fields.List(ma_fields.String(), allow_none=True, load_default=None)
    rows_count = ma_fields.Integer(allow_none=True, load_default=None, validate=validate.Range(min=1, max=20))
    racks_count = ma_fields.Integer(required=True, validate=validate.Range(min=1, max=20))
    sections = ma_fields.List(ma_fields.String(), allow_none=True, load_default=[])
    bay_configs = ma_fields.List(ma_fields.Nested(BayConfigSchema), allow_none=True, load_default=None)
    site_id = ma_fields.String(allow_none=True, load_default=None)

# --- Stock Operations ---
class StockReceiveSchema(BaseSchema):
    item_id = ma_fields.String(allow_none=True, load_default=None)
    part_id = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    lot_batch_no = ma_fields.String(allow_none=True, load_default=None)
    serial_number = ma_fields.String(allow_none=True, load_default=None)
    serial_numbers = ma_fields.List(ma_fields.String(), allow_none=True, load_default=None)
    serial_range_prefix = ma_fields.String(allow_none=True, load_default=None)
    serial_range_start = ma_fields.Integer(allow_none=True, load_default=None)
    serial_range_end = ma_fields.Integer(allow_none=True, load_default=None)
    quantity = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    location_id = ma_fields.String(allow_none=True, load_default=None)
    location_code = ma_fields.String(allow_none=True, load_default=None)
    nfc_uid = ma_fields.String(allow_none=True, load_default=None)
    nfc_tag_uid = ma_fields.String(allow_none=True, load_default=None)
    qr_code = ma_fields.String(allow_none=True, load_default=None)
    vendor_id = ma_fields.String(allow_none=True, load_default=None)
    reference = ma_fields.Raw(allow_none=True, load_default={}) # JSON dict (e.g. project_id, po_number)
    remarks = ma_fields.String(allow_none=True, load_default="Material receipt")
    description = ma_fields.String(allow_none=True, load_default=None)
    manufacturing_date = ma_fields.String(allow_none=True, load_default=None)
    date_code = ma_fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_receive(self, data, **kwargs):
        if not data.get("item_id") and data.get("part_id"):
            data["item_id"] = data["part_id"]
        if not data.get("item_id"):
            raise ValidationError("Either 'item_id' or 'part_id' is required.", field_name="item_id")
        if not data.get("lot_number") and data.get("lot_batch_no"):
            data["lot_number"] = data["lot_batch_no"]
        if not data.get("nfc_uid") and data.get("nfc_tag_uid"):
            data["nfc_uid"] = data["nfc_tag_uid"]

class StockIssueSchema(BaseSchema):
    item_id = ma_fields.String(allow_none=True, load_default=None)
    part_id = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    lot_id = ma_fields.String(allow_none=True, load_default=None)
    serial_number = ma_fields.String(allow_none=True, load_default=None)
    location_id = ma_fields.String(allow_none=True, load_default=None)
    location_code = ma_fields.String(allow_none=True, load_default=None)
    nfc_uid = ma_fields.String(allow_none=True, load_default=None)
    nfc_tag_uid = ma_fields.String(allow_none=True, load_default=None)
    qr_code = ma_fields.String(allow_none=True, load_default=None)
    quantity = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    reference = ma_fields.Raw(allow_none=True, load_default={})
    remarks = ma_fields.String(allow_none=True, load_default="Material issue")
    description = ma_fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_issue(self, data, **kwargs):
        if not data.get("item_id") and data.get("part_id"):
            data["item_id"] = data["part_id"]
        if not data.get("item_id"):
            raise ValidationError("Either 'item_id' or 'part_id' is required.", field_name="item_id")
        if not data.get("lot_number") and data.get("lot_id"):
            data["lot_number"] = data["lot_id"]

class StockTransferSchema(BaseSchema):
    item_id = ma_fields.String(allow_none=True, load_default=None)
    part_id = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    lot_id = ma_fields.String(allow_none=True, load_default=None)
    serial_number = ma_fields.String(allow_none=True, load_default=None)
    from_location_id = ma_fields.String(allow_none=True, load_default=None)
    from_location_code = ma_fields.String(allow_none=True, load_default=None)
    from_nfc_uid = ma_fields.String(allow_none=True, load_default=None)
    from_nfc_tag_uid = ma_fields.String(allow_none=True, load_default=None)
    to_location_id = ma_fields.String(allow_none=True, load_default=None)
    to_location_code = ma_fields.String(allow_none=True, load_default=None)
    to_nfc_uid = ma_fields.String(allow_none=True, load_default=None)
    to_nfc_tag_uid = ma_fields.String(allow_none=True, load_default=None)
    quantity = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    reference = ma_fields.Raw(allow_none=True, load_default={})
    remarks = ma_fields.String(allow_none=True, load_default="Material transfer")
    description = ma_fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_transfer(self, data, **kwargs):
        if not data.get("item_id") and data.get("part_id"):
            data["item_id"] = data["part_id"]
        if not data.get("item_id"):
            raise ValidationError("Either 'item_id' or 'part_id' is required.", field_name="item_id")
        if not data.get("lot_number") and data.get("lot_id"):
            data["lot_number"] = data["lot_id"]

class StockReserveSchema(BaseSchema):
    inventory_id = ma_fields.String(allow_none=True, load_default=None)
    item_id = ma_fields.String(allow_none=True, load_default=None)
    part_id = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    lot_id = ma_fields.String(allow_none=True, load_default=None)
    location_id = ma_fields.String(allow_none=True, load_default=None)
    quantity = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    reserved_for = ma_fields.String(required=True)
    reference = ma_fields.Raw(allow_none=True, load_default={})
    remarks = ma_fields.String(allow_none=True, load_default="Stock reservation")
    description = ma_fields.String(allow_none=True, load_default=None)

class StockReleaseSchema(BaseSchema):
    inventory_id = ma_fields.String(allow_none=True, load_default=None)
    item_id = ma_fields.String(allow_none=True, load_default=None)
    part_id = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    lot_id = ma_fields.String(allow_none=True, load_default=None)
    location_id = ma_fields.String(allow_none=True, load_default=None)
    quantity = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    reference = ma_fields.Raw(allow_none=True, load_default={})
    remarks = ma_fields.String(allow_none=True, load_default="Stock release")
    description = ma_fields.String(allow_none=True, load_default=None)

class CellTransferSchema(BaseSchema):
    serial_number = ma_fields.String(allow_none=True, load_default=None)
    cell_id = ma_fields.String(allow_none=True, load_default=None)
    cell_serial_no = ma_fields.String(allow_none=True, load_default=None)
    to_location_id = ma_fields.String(allow_none=True, load_default=None)
    to_location_code = ma_fields.String(allow_none=True, load_default=None)
    to_nfc_uid = ma_fields.String(allow_none=True, load_default=None)
    to_nfc_tag_uid = ma_fields.String(allow_none=True, load_default=None)
    reference = ma_fields.Raw(allow_none=True, load_default={})
    reference_id = ma_fields.String(allow_none=True, load_default=None)
    remarks = ma_fields.String(allow_none=True, load_default="Cell transferred")
    description = ma_fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_cell(self, data, **kwargs):
        if not data.get("serial_number"):
            data["serial_number"] = data.get("cell_serial_no") or data.get("cell_id")
        if not data.get("serial_number"):
            raise ValidationError("Field 'serial_number' is required.", field_name="serial_number")

# --- Lots (Legacy Schema) ---
class LotSchema(BaseSchema):
    part_id = ma_fields.String(allow_none=True, load_default=None)
    item_id = ma_fields.String(allow_none=True, load_default=None)
    lot_batch_no = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    vendor_id = ma_fields.String(allow_none=True, load_default=None)
    manufacturing_date = ma_fields.String(allow_none=True, load_default=None)
    received_date = ma_fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_lot(self, data, **kwargs):
        if not data.get("part_id") and data.get("item_id"):
            data["part_id"] = data["item_id"]
        if not data.get("lot_batch_no") and data.get("lot_number"):
            data["lot_batch_no"] = data["lot_number"]
        if not data.get("part_id"):
            raise ValidationError("Field 'part_id' or 'item_id' is required.", field_name="part_id")
        if not data.get("lot_batch_no"):
            raise ValidationError("Field 'lot_batch_no' or 'lot_number' is required.", field_name="lot_batch_no")

# --- Users & Auth ---
class UserLoginSchema(BaseSchema):
    username_or_email = ma_fields.String(required=True, validate=validate.Length(min=1))
    password = ma_fields.String(required=True, validate=validate.Length(min=1))
    organization_code = ma_fields.String(allow_none=True, load_default=None)

class UserRegisterSchema(BaseSchema):
    username = ma_fields.String(required=True, validate=validate.Length(min=3, max=100))
    email = ma_fields.Email(required=True)
    name = ma_fields.String(allow_none=True, load_default="")
    password = ma_fields.String(required=True, validate=validate.Length(min=6, max=100))
    role = ma_fields.String(validate=validate.OneOf(["ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR", "VIEWER"]), load_default="STORE_OPERATOR")
    organization_id = ma_fields.String(allow_none=True, load_default="ORG-001")
    site_id = ma_fields.String(allow_none=True, load_default=None)
    status = ma_fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE"]), load_default="ACTIVE")
    full_name = ma_fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_user(self, data, **kwargs):
        if not data.get("name") and data.get("full_name"):
            data["name"] = data["full_name"]

class UserUpdateSchema(BaseSchema):
    name = ma_fields.String(allow_none=True)
    full_name = ma_fields.String(allow_none=True)
    email = ma_fields.Email(allow_none=True)
    role = ma_fields.String(validate=validate.OneOf(["ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR", "VIEWER"]), allow_none=True)
    site_id = ma_fields.String(allow_none=True)
    status = ma_fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE"]), allow_none=True)
    active = ma_fields.Boolean(allow_none=True)

class UserPasswordResetSchema(BaseSchema):
    new_password = ma_fields.String(required=True, validate=validate.Length(min=6, max=100))

# --- Indents & Returns ---
class IndentItemSchema(BaseSchema):
    part_id = ma_fields.String(allow_none=True, load_default=None)
    item_id = ma_fields.String(allow_none=True, load_default=None)
    requested_quantity = ma_fields.Float(allow_none=True, load_default=None)
    quantity = ma_fields.Float(allow_none=True, load_default=None)
    notes = ma_fields.String(allow_none=True, load_default="")

    @validates_schema
    def validate_indent_item(self, data, **kwargs):
        if not data.get("part_id") and data.get("item_id"):
            data["part_id"] = data["item_id"]
        if not data.get("part_id"):
            raise ValidationError("Field 'part_id' or 'item_id' is required.", field_name="part_id")
        if data.get("requested_quantity") is None and data.get("quantity") is not None:
            data["requested_quantity"] = data["quantity"]
        if data.get("requested_quantity") is None or data.get("requested_quantity") <= 0:
            raise ValidationError("Field 'requested_quantity' must be greater than 0.", field_name="requested_quantity")

class IndentCreateSchema(BaseSchema):
    project_id = ma_fields.String(required=True, validate=validate.Length(min=1))
    project_head_id = ma_fields.String(required=True, validate=validate.Length(min=1))
    required_by_date = ma_fields.String(allow_none=True, load_default=None)
    priority = ma_fields.String(validate=validate.OneOf(["LOW", "MEDIUM", "HIGH", "URGENT"]), load_default="MEDIUM")
    purpose = ma_fields.String(allow_none=True, load_default="")
    status = ma_fields.String(validate=validate.OneOf(["DRAFT", "PENDING_APPROVAL"]), load_default="PENDING_APPROVAL")
    items = ma_fields.List(ma_fields.Nested(IndentItemSchema), required=True, validate=validate.Length(min=1))
    notes = ma_fields.String(allow_none=True, load_default="")
    site_id = ma_fields.String(allow_none=True, load_default=None)

class IndentUpdateSchema(BaseSchema):
    project_id = ma_fields.String(allow_none=True)
    project_head_id = ma_fields.String(allow_none=True)
    required_by_date = ma_fields.String(allow_none=True)
    priority = ma_fields.String(validate=validate.OneOf(["LOW", "MEDIUM", "HIGH", "URGENT"]), allow_none=True)
    purpose = ma_fields.String(allow_none=True)
    items = ma_fields.List(ma_fields.Nested(IndentItemSchema), allow_none=True)
    notes = ma_fields.String(allow_none=True)

class IndentApprovalSchema(BaseSchema):
    comments = ma_fields.String(allow_none=True, load_default="Approved")

class IndentRejectSchema(BaseSchema):
    reason = ma_fields.String(required=True, validate=validate.Length(min=1))

class IndentIssueItemSchema(BaseSchema):
    part_id = ma_fields.String(allow_none=True, load_default=None)
    item_id = ma_fields.String(allow_none=True, load_default=None)
    issued_quantity = ma_fields.Float(allow_none=True, load_default=None)
    quantity = ma_fields.Float(allow_none=True, load_default=None)
    location_id = ma_fields.String(allow_none=True, load_default=None)
    location_code = ma_fields.String(allow_none=True, load_default=None)
    lot_id = ma_fields.String(allow_none=True, load_default=None)
    lot_number = ma_fields.String(allow_none=True, load_default=None)
    cell_serial_numbers = ma_fields.List(ma_fields.String(), allow_none=True, load_default=[])
    remarks = ma_fields.String(allow_none=True, load_default="")

    @validates_schema
    def validate_issue_item(self, data, **kwargs):
        if not data.get("part_id") and data.get("item_id"):
            data["part_id"] = data["item_id"]
        if not data.get("part_id"):
            raise ValidationError("Field 'part_id' or 'item_id' is required.", field_name="part_id")
        if data.get("issued_quantity") is None and data.get("quantity") is not None:
            data["issued_quantity"] = data["quantity"]
        if data.get("issued_quantity") is None or data.get("issued_quantity") <= 0:
            raise ValidationError("Field 'issued_quantity' must be greater than 0.", field_name="issued_quantity")

class IndentIssueSchema(BaseSchema):
    items = ma_fields.List(ma_fields.Nested(IndentIssueItemSchema), required=True, validate=validate.Length(min=1))
    comments = ma_fields.String(allow_none=True, load_default="Indent stock issue")

class IndentReturnItemSchema(BaseSchema):
    part_id = ma_fields.String(allow_none=True, load_default=None)
    item_id = ma_fields.String(allow_none=True, load_default=None)
    returned_quantity = ma_fields.Float(allow_none=True, load_default=None)
    quantity = ma_fields.Float(allow_none=True, load_default=None)
    condition = ma_fields.String(validate=validate.OneOf(["GOOD", "DEFECTIVE", "SCRAP"]), load_default="GOOD")
    reason = ma_fields.String(allow_none=True, load_default="")
    cell_serial_numbers = ma_fields.List(ma_fields.String(), allow_none=True, load_default=[])

    @validates_schema
    def validate_return_item(self, data, **kwargs):
        if not data.get("part_id") and data.get("item_id"):
            data["part_id"] = data["item_id"]
        if not data.get("part_id"):
            raise ValidationError("Field 'part_id' or 'item_id' is required.", field_name="part_id")
        if data.get("returned_quantity") is None and data.get("quantity") is not None:
            data["returned_quantity"] = data["quantity"]
        if data.get("returned_quantity") is None or data.get("returned_quantity") <= 0:
            raise ValidationError("Field 'returned_quantity' must be greater than 0.", field_name="returned_quantity")

class IndentReturnCreateSchema(BaseSchema):
    indent_id = ma_fields.String(required=True, validate=validate.Length(min=1))
    items = ma_fields.List(ma_fields.Nested(IndentReturnItemSchema), required=True, validate=validate.Length(min=1))
    reason = ma_fields.String(allow_none=True, load_default="")
    remarks = ma_fields.String(allow_none=True, load_default="")

class IndentReturnAcceptItemSchema(BaseSchema):
    part_id = ma_fields.String(required=True)
    accepted_quantity = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    condition = ma_fields.String(validate=validate.OneOf(["GOOD", "DEFECTIVE", "SCRAP"]), load_default="GOOD")
    restock_location_id = ma_fields.String(allow_none=True, load_default=None)
    restock_location_code = ma_fields.String(allow_none=True, load_default=None)
    lot_id = ma_fields.String(allow_none=True, load_default=None)
    cell_serial_numbers = ma_fields.List(ma_fields.String(), allow_none=True, load_default=[])

class IndentReturnAcceptSchema(BaseSchema):
    items = ma_fields.List(ma_fields.Nested(IndentReturnAcceptItemSchema), allow_none=True, load_default=[])
    inspection_notes = ma_fields.String(allow_none=True, load_default="Return accepted and inspected")
    status = ma_fields.String(validate=validate.OneOf(["ACCEPTED", "REJECTED"]), load_default="ACCEPTED")

