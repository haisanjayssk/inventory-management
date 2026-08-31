import logging
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None
    is_replica_set = False

    @classmethod
    def initialize(cls, uri: str, db_name: str):
        try:
            cls.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            cls.db = cls.client[db_name]
            
            # Check server info
            cls.client.server_info()
            
            # Detect replica set
            try:
                status = cls.client.admin.command('replSetGetStatus')
                cls.is_replica_set = bool(status.get('set'))
                logger.info(f"MongoDB connected in REPLICA SET mode: {status.get('set')}")
            except Exception:
                cls.is_replica_set = False
                logger.info("MongoDB connected in STANDALONE mode (replica set not enabled).")

            cls.create_indexes()
            logger.info(f"Connected to MongoDB database: {db_name}")
            return cls.db
        except ServerSelectionTimeoutError as e:
            logger.error(f"Failed to connect to MongoDB at {uri}: {e}")
            raise e

    @classmethod
    def get_db(cls):
        return cls.db

    @classmethod
    def get_client(cls):
        return cls.client

    @classmethod
    def create_indexes(cls):
        """Creates required unique and query performance indexes according to Specification Section 21."""
        if cls.db is None:
            return

        try:
            # 1. part_types
            cls.db.part_types.create_index([("part_type_name", ASCENDING)], unique=True)

            # 2. part_type_fields
            cls.db.part_type_fields.create_index([("part_type_id", ASCENDING), ("field_key", ASCENDING)], unique=True)
            cls.db.part_type_fields.create_index([("part_type_id", ASCENDING)])

            # 3. vendors
            cls.db.vendors.create_index([("vendor_name", ASCENDING)], unique=True)

            # 4. parts
            cls.db.parts.create_index([("part_code", ASCENDING)], unique=True)
            cls.db.parts.create_index([("mpn", ASCENDING)])
            cls.db.parts.create_index([("part_type_id", ASCENDING)])
            cls.db.parts.create_index([("vendor_id", ASCENDING)])
            cls.db.parts.create_index([("part_name", TEXT), ("description", TEXT), ("part_code", TEXT)])

            # 5. lots
            cls.db.lots.create_index([("part_id", ASCENDING), ("lot_batch_no", ASCENDING)], unique=True)
            cls.db.lots.create_index([("lot_batch_no", ASCENDING)])
            cls.db.lots.create_index([("part_id", ASCENDING)])
            cls.db.lots.create_index([("vendor_id", ASCENDING)])

            # 6. cells
            cls.db.cells.create_index([("cell_serial_no", ASCENDING)], unique=True)
            cls.db.cells.create_index([("part_id", ASCENDING)])
            cls.db.cells.create_index([("lot_id", ASCENDING)])
            cls.db.cells.create_index([("status", ASCENDING)])

            # 7. locations
            cls.db.locations.create_index([("location_code", ASCENDING)], unique=True)
            cls.db.locations.create_index([("nfc_tag_uid", ASCENDING)], unique=True)
            cls.db.locations.create_index([("warehouse_code", ASCENDING)])
            cls.db.locations.create_index([("status", ASCENDING)])

            # 8. inventory
            cls.db.inventory.create_index([("part_id", ASCENDING), ("lot_id", ASCENDING), ("location_id", ASCENDING)], unique=True)
            cls.db.inventory.create_index([("part_id", ASCENDING)])
            cls.db.inventory.create_index([("lot_id", ASCENDING)])
            cls.db.inventory.create_index([("location_id", ASCENDING)])
            cls.db.inventory.create_index([("status", ASCENDING)])

            # 9. cell_inventory
            cls.db.cell_inventory.create_index([("cell_id", ASCENDING)], unique=True)
            cls.db.cell_inventory.create_index([("location_id", ASCENDING)])
            cls.db.cell_inventory.create_index([("status", ASCENDING)])

            # 10. transactions
            cls.db.transactions.create_index([("part_id", ASCENDING)])
            cls.db.transactions.create_index([("lot_id", ASCENDING)])
            cls.db.transactions.create_index([("cell_id", ASCENDING)])
            cls.db.transactions.create_index([("from_location_id", ASCENDING)])
            cls.db.transactions.create_index([("to_location_id", ASCENDING)])
            cls.db.transactions.create_index([("timestamp", DESCENDING)])
            cls.db.transactions.create_index([("transaction_type", ASCENDING)])

            # 11. users
            cls.db.users.create_index([("email", ASCENDING)], unique=True)
            cls.db.users.create_index([("username", ASCENDING)], unique=True)

            logger.info("All MongoDB collection indexes verified and created successfully.")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    @classmethod
    def execute_transaction(cls, callback):
        """
        Executes a callable inside a MongoDB multi-document transaction if replica set is available,
        or calls it directly if running in standalone mode.
        """
        if cls.is_replica_set and cls.client:
            with cls.client.start_session() as session:
                with session.start_transaction():
                    return callback(session=session)
        else:
            return callback(session=None)
