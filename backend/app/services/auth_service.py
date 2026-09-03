from datetime import datetime, timezone
from app.repositories.user_repository import UserRepository
from app.models.counter import SequenceCounter
from app.security.auth import hash_password, check_password, generate_token

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def login(self, username_or_email: str, password: str):
        user = self.user_repo.find_by_username_or_email(username_or_email)
        if not user or not check_password(password, user["password_hash"]):
            raise ValueError("Invalid username/email or password")

        if not user.get("active", True):
            raise ValueError("User account is disabled")

        token = generate_token(
            user_id=user["_id"],
            username=user["username"],
            email=user["email"],
            role=user["role"]
        )

        return {
            "token": token,
            "user": {
                "_id": user["_id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name", user["username"]),
                "role": user["role"]
            }
        }

    def register(self, data: dict, created_by: str = "system"):
        if self.user_repo.find_by_email(data["email"]):
            raise ValueError(f"Email {data['email']} is already registered")
        if self.user_repo.find_by_username(data["username"]):
            raise ValueError(f"Username {data['username']} is already taken")

        user_id = SequenceCounter.get_next_id("user")
        user_doc = {
            "_id": user_id,
            "username": data["username"].lower().strip(),
            "email": data["email"].lower().strip(),
            "full_name": data.get("full_name", data["username"]),
            "password_hash": hash_password(data["password"]),
            "role": data.get("role", "STORE_OPERATOR"),
            "active": True,
            "created_by": created_by
        }
        self.user_repo.insert_one(user_doc)
        
        user_clean = {k: v for k, v in user_doc.items() if k != "password_hash"}
        return user_clean

    def get_all_users(self, search: str = None, role: str = None, active: bool = None):
        query = {}
        if role:
            query["role"] = role.upper().strip()
        if active is not None:
            query["active"] = active
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}}
            ]

        users = self.user_repo.find_all(query, sort_by=[("created_at", -1)])
        sanitized = []
        for u in users:
            sanitized.append({k: v for k, v in u.items() if k != "password_hash"})
        return sanitized

    def get_user_by_id(self, user_id: str):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return {k: v for k, v in user.items() if k != "password_hash"}

    def update_user(self, user_id: str, data: dict):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        update_set = {}
        if "full_name" in data and data["full_name"]:
            update_set["full_name"] = data["full_name"].strip()
        if "email" in data and data["email"]:
            new_email = data["email"].lower().strip()
            existing = self.user_repo.find_by_email(new_email)
            if existing and existing["_id"] != user_id:
                raise ValueError(f"Email {new_email} is already taken by another user")
            update_set["email"] = new_email
        if "role" in data and data["role"]:
            update_set["role"] = data["role"].upper().strip()
        if "active" in data and data["active"] is not None:
            update_set["active"] = bool(data["active"])

        if update_set:
            self.user_repo.update_one({"_id": user_id}, {"$set": update_set})

        return self.get_user_by_id(user_id)

    def reset_password(self, user_id: str, new_password: str):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        new_hash = hash_password(new_password)
        self.user_repo.update_one({"_id": user_id}, {"$set": {"password_hash": new_hash}})
        return {"user_id": user_id, "message": "Password reset successfully"}

    def delete_user(self, user_id: str):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Soft delete / deactivate user
        self.user_repo.update_one({"_id": user_id}, {"$set": {"active": False}})
        return {"user_id": user_id, "message": "User account deactivated successfully"}

