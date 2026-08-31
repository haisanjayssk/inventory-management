from pymongo import ReturnDocument
from app.config.database import Database

class SequenceCounter:
    FORMAT_CONFIGS = {
        "part_type": ("PT-", 3),          # PT-001
        "part_type_field": ("PTF-", 3),    # PTF-001
        "vendor": ("VEN-", 3),            # VEN-001
        "part": ("PART-", 6),             # PART-000001
        "lot": ("LOT-", 6),               # LOT-000001
        "cell": ("CELL-ID-", 6),          # CELL-ID-000001
        "location": ("LOC-", 6),          # LOC-000001
        "inventory": ("INV-", 6),         # INV-000001
        "cell_inventory": ("CELL-INV-", 6), # CELL-INV-000001
        "transaction": ("TXN-", 6),       # TXN-000001
        "user": ("USER-", 3),             # USER-001
    }

    @classmethod
    def get_next_id(cls, entity_name: str, session=None) -> str:
        """Atomically increments sequence and returns formatted ID."""
        db = Database.get_db()
        prefix, pad_length = cls.FORMAT_CONFIGS.get(entity_name, (f"{entity_name.upper()}-", 6))
        
        counter = db.counters.find_one_and_update(
            {"_id": entity_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
            session=session
        )
        seq_num = counter["seq"]
        return f"{prefix}{str(seq_num).zfill(pad_length)}"

    @classmethod
    def get_next_batch_ids(cls, entity_name: str, count: int, session=None) -> list:
        """Atomically increments sequence by count and returns list of formatted IDs."""
        if count <= 0:
            return []
        db = Database.get_db()
        prefix, pad_length = cls.FORMAT_CONFIGS.get(entity_name, (f"{entity_name.upper()}-", 6))
        
        counter = db.counters.find_one_and_update(
            {"_id": entity_name},
            {"$inc": {"seq": count}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
            session=session
        )
        end_seq = counter["seq"]
        start_seq = end_seq - count + 1
        
        return [f"{prefix}{str(seq).zfill(pad_length)}" for seq in range(start_seq, end_seq + 1)]
