"""
LeadFlow — User Repository
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pymongo.database import Database

from app.backend.models.domain import UserCreate, UserDB, UserPublic, UserRole

logger = logging.getLogger(__name__)


def _doc_to_user(doc: dict) -> UserDB:
    doc["id"] = str(doc.pop("_id"))
    return UserDB(**doc)


class UserRepository:
    def __init__(self, db: Database) -> None:
        self.col = db.users

    def find_by_email(self, email: str) -> Optional[UserDB]:
        doc = self.col.find_one({"email": email.lower()})
        if doc:
            return _doc_to_user(doc)
        return None

    def find_by_id(self, user_id: str) -> Optional[UserDB]:
        try:
            doc = self.col.find_one({"_id": ObjectId(user_id)})
            if doc:
                return _doc_to_user(doc)
        except Exception:
            pass
        return None

    def create(self, user: UserDB) -> UserDB:
        doc = user.model_dump(exclude={"id"})
        result = self.col.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    def update_last_login(self, user_id: str) -> None:
        self.col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    def list_all(self) -> list[UserPublic]:
        docs = self.col.find({}, sort=[("name", 1)])
        result = []
        for doc in docs:
            user = _doc_to_user(doc)
            result.append(UserPublic(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login,
            ))
        return result

    def update(self, user_id: str, updates: dict) -> bool:
        updates["updated_at"] = datetime.utcnow()
        result = self.col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def delete(self, user_id: str) -> bool:
        result = self.col.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    def count(self) -> int:
        return self.col.count_documents({})
