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

            cls.cleanup_legacy_collections()
            cls.create_indexes()
            logger.info(f"Connected to MongoDB database: {db_name}")
            return cls.db
        except ServerSelectionTimeoutError as e:
            logger.error(f"Failed to connect to MongoDB at {uri}: {e}")
            raise e

    @classmethod
    def cleanup_legacy_collections(cls):
        """Automatically removes legacy/deprecated collections on startup."""
        if cls.db is None:
            return

        legacy_collections = [
            "parts",
            "part_types",
            "part_type_fields",
            "lots",
            "cells",
            "cell_inventory",
            "transactions",
            "counters"
        ]

        try:
            existing = set(cls.db.list_collection_names())
            for coll_name in legacy_collections:
                if coll_name in existing:
                    cls.db[coll_name].drop()
                    logger.info(f"Cleaned up legacy MongoDB collection: '{coll_name}'")
        except Exception as e:
            logger.warning(f"Note on legacy collection cleanup: {e}")


    @classmethod
    def get_db(cls):
        return cls.db

    @classmethod
    def get_client(cls):
        return cls.client

    @classmethod
    def create_indexes(cls):
        """Creates required unique and query performance indexes for core collections."""
        if cls.db is None:
            return

        try:
            # 1. organizations
            cls.db.organizations.create_index([("code", ASCENDING)], unique=True, sparse=True)
            cls.db.organizations.create_index([("status", ASCENDING)])

            # 2. users
            cls.db.users.create_index([("organization_id", ASCENDING), ("username", ASCENDING)], unique=True, sparse=True)
            cls.db.users.create_index([("organization_id", ASCENDING), ("email", ASCENDING)], unique=True, sparse=True)
            cls.db.users.create_index([("username", ASCENDING)], sparse=True)
            cls.db.users.create_index([("email", ASCENDING)], sparse=True)

            # 3. projects
            cls.db.projects.create_index([("organization_id", ASCENDING), ("project_id", ASCENDING)], unique=True, sparse=True)
            cls.db.projects.create_index([("project_id", ASCENDING)], sparse=True)

            # 4. item_types
            cls.db.item_types.create_index([("organization_id", ASCENDING), ("code", ASCENDING)], unique=True, sparse=True)
            cls.db.item_types.create_index([("organization_id", ASCENDING), ("name", ASCENDING)], sparse=True)

            # 5. items
            cls.db.items.create_index([("organization_id", ASCENDING), ("code", ASCENDING)], unique=True, sparse=True)
            cls.db.items.create_index([("organization_id", ASCENDING), ("item_type_id", ASCENDING)], sparse=True)
            cls.db.items.create_index([("name", TEXT), ("description", TEXT), ("code", TEXT)])

            # 6. vendors
            cls.db.vendors.create_index([("organization_id", ASCENDING), ("code", ASCENDING)], sparse=True)
            cls.db.vendors.create_index([("organization_id", ASCENDING), ("name", ASCENDING)], sparse=True)

            # 7. locations
            cls.db.locations.create_index([("organization_id", ASCENDING), ("location_code", ASCENDING)], unique=True, sparse=True)
            cls.db.locations.create_index([("organization_id", ASCENDING), ("parent_id", ASCENDING)], sparse=True)
            cls.db.locations.create_index([("nfc_uid", ASCENDING)], sparse=True)
            cls.db.locations.create_index([("qr_code", ASCENDING)], sparse=True)
            cls.db.locations.create_index([("location_code", ASCENDING)], sparse=True)
            cls.db.locations.create_index([("status", ASCENDING)])

            # 8. inventory
            cls.db.inventory.create_index([
                ("organization_id", ASCENDING),
                ("item_id", ASCENDING),
                ("location_id", ASCENDING),
                ("lot_number", ASCENDING),
                ("serial_number", ASCENDING)
            ], sparse=True)
            cls.db.inventory.create_index([("serial_number", ASCENDING)], sparse=True)
            cls.db.inventory.create_index([("location_id", ASCENDING)])
            cls.db.inventory.create_index([("item_id", ASCENDING)])
            cls.db.inventory.create_index([("status", ASCENDING)])

            # 9. inventory_transactions
            cls.db.inventory_transactions.create_index([("organization_id", ASCENDING), ("t_id", ASCENDING)], sparse=True)
            cls.db.inventory_transactions.create_index([("item_id", ASCENDING)])
            cls.db.inventory_transactions.create_index([("serial_number", ASCENDING)], sparse=True)
            cls.db.inventory_transactions.create_index([("timestamp", DESCENDING)])
            cls.db.inventory_transactions.create_index([("performed_by", ASCENDING)])

            # 10. indents
            cls.db.indents.create_index([("organization_id", ASCENDING), ("indent_number", ASCENDING)], unique=True, sparse=True)
            cls.db.indents.create_index([("organization_id", ASCENDING), ("project_id", ASCENDING)], sparse=True)
            cls.db.indents.create_index([("organization_id", ASCENDING), ("status", ASCENDING)])
            cls.db.indents.create_index([("organization_id", ASCENDING), ("requester_id", ASCENDING)], sparse=True)
            cls.db.indents.create_index([("organization_id", ASCENDING), ("project_head_id", ASCENDING)], sparse=True)
            cls.db.indents.create_index([("created_at", DESCENDING)])

            # 11. indent_returns
            cls.db.indent_returns.create_index([("organization_id", ASCENDING), ("return_number", ASCENDING)], unique=True, sparse=True)
            cls.db.indent_returns.create_index([("organization_id", ASCENDING), ("indent_id", ASCENDING)], sparse=True)
            cls.db.indent_returns.create_index([("organization_id", ASCENDING), ("status", ASCENDING)])
            cls.db.indent_returns.create_index([("created_at", DESCENDING)])

            logger.info("Core collection indexes ensured successfully.")
        except PyMongoError as e:
            logger.warning(f"Note on index creation: {e}")
