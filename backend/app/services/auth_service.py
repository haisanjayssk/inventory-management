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
