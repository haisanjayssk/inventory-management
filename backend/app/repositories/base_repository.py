from datetime import datetime, timezone
from app.config.database import Database

class BaseRepository:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @property
    def collection(self):
        db = Database.get_db()
        return db[self.collection_name]

    def find_one(self, filter_query: dict, session=None):
        return self.collection.find_one(filter_query, session=session)

    def find_by_id(self, doc_id: str, session=None):
        return self.collection.find_one({"_id": doc_id}, session=session)

    def find_all(self, filter_query: dict = None, sort_by=None, skip: int = 0, limit: int = 0, session=None):
        query = filter_query or {}
        cursor = self.collection.find(query, session=session)
        if sort_by:
            cursor = cursor.sort(sort_by)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    def count(self, filter_query: dict = None, session=None) -> int:
        query = filter_query or {}
        return self.collection.count_documents(query, session=session)

    def insert_one(self, document: dict, session=None):
        now = datetime.now(timezone.utc).isoformat()
        if "created_at" not in document:
            document["created_at"] = now
        if "updated_at" not in document:
            document["updated_at"] = now
        self.collection.insert_one(document, session=session)
        return document

    def insert_many(self, documents: list, session=None):
        if not documents:
            return []
        now = datetime.now(timezone.utc).isoformat()
        for doc in documents:
            if "created_at" not in doc:
                doc["created_at"] = now
            if "updated_at" not in doc:
                doc["updated_at"] = now
        self.collection.insert_many(documents, session=session)
        return documents

    def update_one(self, filter_query: dict, update_data: dict, session=None, upsert: bool = False):
        now = datetime.now(timezone.utc).isoformat()
        if "$set" in update_data:
            update_data["$set"]["updated_at"] = now
        else:
            update_data["$set"] = {"updated_at": now}
        return self.collection.update_one(filter_query, update_data, session=session, upsert=upsert)

    def delete_one(self, filter_query: dict, session=None):
        return self.collection.delete_one(filter_query, session=session)

    def bulk_write(self, operations: list, ordered: bool = True, session=None):
        if not operations:
            return None
        return self.collection.bulk_write(operations, ordered=ordered, session=session)
