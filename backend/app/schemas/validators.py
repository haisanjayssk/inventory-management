from marshmallow import Schema, fields, validate, validates, ValidationError

class UserLoginSchema(Schema):
    username_or_email = fields.String(required=True)
    password = fields.String(required=True)

class UserRegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    full_name = fields.String(required=True)
    role = fields.String(
        required=True,
        validate=validate.OneOf(["ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR", "VIEWER"])
    )

class UserUpdateSchema(Schema):
    full_name = fields.String(validate=validate.Length(min=2, max=100))
    email = fields.Email()
    role = fields.String(
        validate=validate.OneOf(["ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR", "VIEWER"])
    )
    active = fields.Boolean()

class UserPasswordResetSchema(Schema):
    new_password = fields.String(required=True, validate=validate.Length(min=6))


class PartTypeFieldSchema(Schema):
    field_name = fields.String(required=True)
    field_key = fields.String(required=True)
    data_type = fields.String(
        required=True,
        validate=validate.OneOf(["STRING", "NUMBER", "DECIMAL", "BOOLEAN", "SELECT"])
    )
    unit = fields.String(allow_none=True, load_default=None)
    options = fields.List(fields.String(), allow_none=True, load_default=[])
    required = fields.Boolean(load_default=False)
    active = fields.Boolean(load_default=True)

class PartTypeSchema(Schema):
    part_type_name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    description = fields.String(allow_none=True, load_default="")
    fields = fields.List(fields.Nested(PartTypeFieldSchema), allow_none=True, load_default=[])

class VendorSchema(Schema):
    vendor_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    contact = fields.String(allow_none=True, load_default="")
    email = fields.Email(allow_none=True, load_default=None)
    address = fields.String(allow_none=True, load_default="")
    country = fields.String(allow_none=True, load_default="India")
    status = fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE"]), load_default="ACTIVE")

class PartSchema(Schema):
    part_type_id = fields.String(required=True)
    part_code = fields.String(required=True, validate=validate.Length(min=2, max=100))
    part_name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    package = fields.String(allow_none=True, load_default="")
    vendor_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="")
    mfr = fields.String(allow_none=True, load_default="")
    mpn = fields.String(allow_none=True, load_default="")
    rohs = fields.String(validate=validate.OneOf(["YES", "NO", "NA"]), load_default="YES")
    static_sensitive = fields.String(validate=validate.OneOf(["YES", "NO"]), load_default="NO")
    msl = fields.String(allow_none=True, load_default="NA")
    unit_of_measure = fields.String(validate=validate.Length(min=1, max=10), load_default="PCS")
    tracking_type = fields.String(validate=validate.OneOf(["QUANTITY", "SERIAL"]), required=True)
    attributes = fields.Dict(allow_none=True, load_default={})
    active = fields.Boolean(load_default=True)

class LotSchema(Schema):
    part_id = fields.String(required=True)
    lot_batch_no = fields.String(required=True, validate=validate.Length(min=1, max=100))
    vendor_id = fields.String(allow_none=True, load_default=None)
    dop = fields.String(allow_none=True, load_default=None)
    manufacturing_date = fields.String(allow_none=True, load_default=None)
    received_date = fields.String(allow_none=True, load_default=None)
    expiry_date = fields.String(allow_none=True, load_default=None)

class LocationSchema(Schema):
    warehouse_code = fields.String(required=True)
    bay_number = fields.String(required=True)
    row_number = fields.Integer(required=True, validate=validate.Range(min=1, max=20))
    rack_number = fields.Integer(required=True, validate=validate.Range(min=1, max=20))
    section_code = fields.String(allow_none=True, load_default="", validate=validate.Length(max=5))
    location_code = fields.String(allow_none=True, load_default=None)
    nfc_tag_uid = fields.String(allow_none=True, load_default=None)
    status = fields.String(validate=validate.OneOf(["ACTIVE", "INACTIVE", "MAINTENANCE"]), load_default="ACTIVE")

class BayConfigSchema(Schema):
    bay = fields.String(required=True)
    rows_count = fields.Integer(required=True, validate=validate.Range(min=1, max=20))

class BulkLocationGenerateSchema(Schema):
    warehouse_name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    warehouse_code = fields.String(allow_none=True, load_default=None)
    bays = fields.List(fields.String(), allow_none=True, load_default=None) # e.g. ["1", "2", "3"]
    rows_count = fields.Integer(allow_none=True, load_default=None, validate=validate.Range(min=1, max=20))
    racks_count = fields.Integer(required=True, validate=validate.Range(min=1, max=20))
    sections = fields.List(fields.String(), allow_none=True, load_default=[]) # e.g. ["A", "B"] or [] for single rack
    bay_configs = fields.List(fields.Nested(BayConfigSchema), allow_none=True, load_default=None)


class StockReceiveSchema(Schema):
    part_id = fields.String(required=True)
    lot_id = fields.String(allow_none=True, load_default=None)
    lot_batch_no = fields.String(allow_none=True, load_default=None)
    vendor_id = fields.String(allow_none=True, load_default=None)
    manufacturing_date = fields.String(allow_none=True, load_default=None)
    expiry_date = fields.String(allow_none=True, load_default=None)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    location_id = fields.String(allow_none=True, load_default=None)
    location_code = fields.String(allow_none=True, load_default=None)
    nfc_tag_uid = fields.String(allow_none=True, load_default=None)
    reference_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="Material receipt")
    # For Cells bulk ingestion:
    cell_serials = fields.List(fields.String(), allow_none=True, load_default=None)
    serial_range_prefix = fields.String(allow_none=True, load_default=None)
    serial_range_start = fields.Integer(allow_none=True, load_default=None)
    serial_range_end = fields.Integer(allow_none=True, load_default=None)
    date_code = fields.String(allow_none=True, load_default=None)

class StockIssueSchema(Schema):
    part_id = fields.String(required=True)
    lot_id = fields.String(required=True)
    location_id = fields.String(allow_none=True, load_default=None)
    location_code = fields.String(allow_none=True, load_default=None)
    nfc_tag_uid = fields.String(allow_none=True, load_default=None)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    reference_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="Material issue")

class StockTransferSchema(Schema):
    part_id = fields.String(required=True)
    lot_id = fields.String(required=True)
    from_location_id = fields.String(allow_none=True, load_default=None)
    from_location_code = fields.String(allow_none=True, load_default=None)
    from_nfc_tag_uid = fields.String(allow_none=True, load_default=None)
    to_location_id = fields.String(allow_none=True, load_default=None)
    to_location_code = fields.String(allow_none=True, load_default=None)
    to_nfc_tag_uid = fields.String(allow_none=True, load_default=None)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    reference_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="Material transfer")

class StockReserveSchema(Schema):
    inventory_id = fields.String(allow_none=True, load_default=None)
    part_id = fields.String(allow_none=True, load_default=None)
    lot_id = fields.String(allow_none=True, load_default=None)
    location_id = fields.String(allow_none=True, load_default=None)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    reserved_for = fields.String(required=True) # Work order number
    reference_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="Stock reservation")

class StockReleaseSchema(Schema):
    inventory_id = fields.String(allow_none=True, load_default=None)
    part_id = fields.String(allow_none=True, load_default=None)
    lot_id = fields.String(allow_none=True, load_default=None)
    location_id = fields.String(allow_none=True, load_default=None)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    reference_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="Stock release")

class CellTransferSchema(Schema):
    cell_id = fields.String(allow_none=True, load_default=None)
    cell_serial_no = fields.String(allow_none=True, load_default=None)
    to_location_id = fields.String(allow_none=True, load_default=None)
    to_location_code = fields.String(allow_none=True, load_default=None)
    to_nfc_tag_uid = fields.String(allow_none=True, load_default=None)
    reference_id = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default="Cell transferred")
