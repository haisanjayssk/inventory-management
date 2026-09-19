import uuid

class IdGenerator:
    PREFIX_MAP = {
        "organization": "ORG",
        "user": "USER",
        "project": "PRJ",
        "item_type": "IT",
        "part_type": "IT",
        "item": "ITEM",
        "part": "ITEM",
        "location": "LOC",
        "vendor": "VEN",
        "inventory": "INV",
        "transaction": "TXN",
        "indent": "IND",
        "indent_return": "RET"
    }

    @classmethod
    def generate_id(cls, entity_name: str, length: int = 8, session=None) -> str:
        prefix = cls.PREFIX_MAP.get(entity_name.lower(), entity_name.upper())
        rand_hex = uuid.uuid4().hex[:length].upper()
        return f"{prefix}-{rand_hex}"

    @classmethod
    def generate_batch_ids(cls, entity_name: str, count: int, length: int = 8, session=None) -> list:
        prefix = cls.PREFIX_MAP.get(entity_name.lower(), entity_name.upper())
        return [f"{prefix}-{uuid.uuid4().hex[:length].upper()}" for _ in range(count)]

    # Compatibility methods for SequenceCounter drop-in replacement
    @classmethod
    def get_next_id(cls, entity_name: str, session=None) -> str:
        return cls.generate_id(entity_name, session=session)

    @classmethod
    def get_next_batch_ids(cls, entity_name: str, count: int, session=None) -> list:
        return cls.generate_batch_ids(entity_name, count, session=session)

    @classmethod
    def sync_counters(cls):
        # Stateless - no DB collection needed
        pass

SequenceCounter = IdGenerator
