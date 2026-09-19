from datetime import datetime, timezone
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.models.counter import SequenceCounter
from app.security.auth import hash_password, check_password, generate_token

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.org_repo = OrganizationRepository()

    def login(self, username_or_email: str, password: str, organization_code: str = None):
        user = self.user_repo.find_by_username_or_email(username_or_email)
        if not user or not check_password(password, user["password_hash"]):
            raise ValueError("Invalid username/email or password")

        if user.get("status") == "INACTIVE" or not user.get("active", True):
            raise ValueError("User account is disabled")

        org_id = user.get("organization_id", "ORG-001")
        site_id = user.get("site_id", "SITE-001")

        token = generate_token(
            user_id=user["_id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            organization_id=org_id,
            site_id=site_id
        )

        return {
            "token": token,
            "user": {
                "_id": user["_id"],
                "username": user["username"],
                "email": user["email"],
                "name": user.get("name") or user.get("full_name") or user["username"],
                "full_name": user.get("name") or user.get("full_name") or user["username"],
                "role": user["role"],
                "organization_id": org_id,
                "site_id": site_id,
                "status": user.get("status", "ACTIVE")
            }
        }

    def register(self, data: dict, created_by: str = "system", org_id: str = "ORG-001"):
        email = data["email"].lower().strip()
        username = data["username"].lower().strip()

        if self.user_repo.find_by_email(email, org_id):
            raise ValueError(f"Email '{email}' is already registered")
        if self.user_repo.find_by_username(username, org_id):
            raise ValueError(f"Username '{username}' is already taken")

        user_id = SequenceCounter.get_next_id("user")
        now = datetime.now(timezone.utc).isoformat()
        name = data.get("name") or data.get("full_name") or username

        user_doc = {
            "_id": user_id,
            "organization_id": data.get("organization_id") or org_id,
            "site_id": data.get("site_id", "SITE-001"),
            "username": username,
            "email": email,
            "name": name,
            "full_name": name,
            "password_hash": hash_password(data["password"]),
            "role": data.get("role", "STORE_OPERATOR"),
            "status": data.get("status", "ACTIVE"),
            "active": True,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now
        }
        self.user_repo.insert_one(user_doc)
        return {k: v for k, v in user_doc.items() if k != "password_hash"}

    def get_all_users(self, org_id: str = "ORG-001", search: str = None, role: str = None, active: bool = None):
        query = {"organization_id": org_id}
        if role:
            query["role"] = role.upper().strip()
        if active is not None:
            query["status"] = "ACTIVE" if active else "INACTIVE"
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}}
            ]

        users = self.user_repo.find_all(query, sort_by=[("created_at", -1)])
        return [{k: v for k, v in u.items() if k != "password_hash"} for u in users]

    def get_user_by_id(self, user_id: str, org_id: str = "ORG-001"):
        user = self.user_repo.find_one({"_id": user_id, "organization_id": org_id})
        if not user:
            user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        return {k: v for k, v in user.items() if k != "password_hash"}

    def update_user(self, user_id: str, data: dict, org_id: str = "ORG-001"):
        user = self.get_user_by_id(user_id, org_id)
        update_set = {}
        if "name" in data or "full_name" in data:
            name_val = (data.get("name") or data.get("full_name") or "").strip()
            update_set["name"] = name_val
            update_set["full_name"] = name_val
        if "email" in data and data["email"]:
            new_email = data["email"].lower().strip()
            existing = self.user_repo.find_by_email(new_email, org_id)
            if existing and existing["_id"] != user["_id"]:
                raise ValueError(f"Email '{new_email}' is already taken by another user")
            update_set["email"] = new_email
        if "role" in data and data["role"]:
            update_set["role"] = data["role"].upper().strip()
        if "site_id" in data:
            update_set["site_id"] = data["site_id"]
        if "status" in data:
            update_set["status"] = data["status"]
            update_set["active"] = data["status"] == "ACTIVE"
        if "active" in data:
            update_set["active"] = bool(data["active"])
            update_set["status"] = "ACTIVE" if data["active"] else "INACTIVE"

        update_set["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.user_repo.update_one({"_id": user["_id"]}, {"$set": update_set})
        return self.get_user_by_id(user["_id"], org_id)

    def reset_password(self, user_id: str, new_password: str, org_id: str = "ORG-001"):
        user = self.get_user_by_id(user_id, org_id)
        self.user_repo.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "password_hash": hash_password(new_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"message": "Password reset successfully"}

    def delete_user(self, user_id: str, org_id: str = "ORG-001"):
        user = self.get_user_by_id(user_id, org_id)
        self.user_repo.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "status": "INACTIVE",
                "active": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"user_id": user["_id"], "message": "User deactivated successfully"}

