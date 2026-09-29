"""
LeadFlow — Lead Repository
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional
from bson import ObjectId
from pymongo.database import Database

from app.backend.models.domain import LeadDB, LeadStatus, LeadPriority

logger = logging.getLogger(__name__)


def _doc_to_lead(doc: dict) -> LeadDB:
    doc["id"] = str(doc.pop("_id"))
    return LeadDB(**doc)


class LeadRepository:
    def __init__(self, db: Database) -> None:
        self.col = db.leads

    def create(self, lead: LeadDB) -> LeadDB:
        doc = lead.model_dump(exclude={"id"})
        result = self.col.insert_one(doc)
        lead.id = str(result.inserted_id)
        return lead

    def create_many(self, leads: list[LeadDB]) -> int:
        if not leads:
            return 0
        docs = [lead.model_dump(exclude={"id"}) for lead in leads]
        result = self.col.insert_many(docs)
        return len(result.inserted_ids)

    def find_by_id(self, lead_id: str) -> Optional[LeadDB]:
        try:
            doc = self.col.find_one({"_id": ObjectId(lead_id)})
            if doc:
                return _doc_to_lead(doc)
        except Exception:
            pass
        return None

    def find_by_phone(self, phone: str) -> Optional[LeadDB]:
        doc = self.col.find_one({"phone": phone})
        if doc:
            return _doc_to_lead(doc)
        return None

    def find_by_email(self, email: str) -> Optional[LeadDB]:
        if not email:
            return None
        doc = self.col.find_one({"email": email.lower()})
        if doc:
            return _doc_to_lead(doc)
        return None

    def exists_by_phone_or_email(self, phone: Optional[str], email: Optional[str]) -> bool:
        conditions = []
        if phone:
            conditions.append({"phone": phone})
        if email:
            conditions.append({"email": email.lower()})
        if not conditions:
            return False
        return self.col.count_documents({"$or": conditions}) > 0

    def list_all(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
    ) -> tuple[list[LeadDB], int]:
        query: dict[str, Any] = {}

        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if assigned_to:
            query["assigned_to"] = assigned_to
        if min_score is not None or max_score is not None:
            score_q: dict[str, int] = {}
            if min_score is not None:
                score_q["$gte"] = min_score
            if max_score is not None:
                score_q["$lte"] = max_score
            query["lead_score"] = score_q
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"company": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]

        total = self.col.count_documents(query)
        skip = (page - 1) * page_size

        docs = self.col.find(
            query,
            sort=[("created_at", -1)],
        ).skip(skip).limit(page_size)

        leads = [_doc_to_lead(doc) for doc in docs]
        return leads, total

    def update(self, lead_id: str, updates: dict) -> bool:
        updates["updated_at"] = datetime.utcnow()
        try:
            result = self.col.update_one(
                {"_id": ObjectId(lead_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Lead update error: {e}")
            return False

    def delete(self, lead_id: str) -> bool:
        try:
            result = self.col.delete_one({"_id": ObjectId(lead_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    def count_by_status(self) -> dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        result = {}
        for doc in self.col.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    def count_by_priority(self) -> dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
        ]
        result = {}
        for doc in self.col.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    def average_score(self) -> float:
        pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": "$lead_score"}}}
        ]
        docs = list(self.col.aggregate(pipeline))
        if docs:
            return round(docs[0].get("avg", 0) or 0, 1)
        return 0.0

    def count_high_priority(self) -> int:
        return self.col.count_documents({"priority": "high"})

    def count_total(self) -> int:
        return self.col.count_documents({})

    def get_high_priority_leads(self, limit: int = 10) -> list[LeadDB]:
        docs = self.col.find(
            {"priority": "high"},
            sort=[("lead_score", -1)],
        ).limit(limit)
        return [_doc_to_lead(doc) for doc in docs]

    def get_by_assigned_to(self, user_id: str) -> list[LeadDB]:
        docs = self.col.find({"assigned_to": user_id}, sort=[("created_at", -1)])
        return [_doc_to_lead(doc) for doc in docs]
