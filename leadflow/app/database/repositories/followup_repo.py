"""
LeadFlow — Follow-up Repository
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pymongo.database import Database

from app.backend.models.domain import FollowUpDB, FollowUpStatus

logger = logging.getLogger(__name__)


def _doc_to_followup(doc: dict) -> FollowUpDB:
    doc["id"] = str(doc.pop("_id"))
    return FollowUpDB(**doc)


class FollowUpRepository:
    def __init__(self, db: Database) -> None:
        self.col = db.follow_ups

    def create(self, followup: FollowUpDB) -> FollowUpDB:
        doc = followup.model_dump(exclude={"id"})
        result = self.col.insert_one(doc)
        followup.id = str(result.inserted_id)
        return followup

    def find_by_id(self, followup_id: str) -> Optional[FollowUpDB]:
        try:
            doc = self.col.find_one({"_id": ObjectId(followup_id)})
            if doc:
                return _doc_to_followup(doc)
        except Exception:
            pass
        return None

    def list_all(
        self,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[FollowUpDB], int]:
        query: dict = {}
        if status:
            query["status"] = status
        if assigned_to:
            query["assigned_to"] = assigned_to

        total = self.col.count_documents(query)
        skip = (page - 1) * page_size
        docs = self.col.find(query, sort=[("due_date", 1)]).skip(skip).limit(page_size)
        return [_doc_to_followup(doc) for doc in docs], total

    def list_for_lead(self, lead_id: str) -> list[FollowUpDB]:
        docs = self.col.find({"lead_id": lead_id}, sort=[("due_date", 1)])
        return [_doc_to_followup(doc) for doc in docs]

    def update_status(self, followup_id: str, status: FollowUpStatus) -> bool:
        updates: dict = {"status": status.value}
        if status == FollowUpStatus.COMPLETED:
            updates["completed_at"] = datetime.utcnow()
        try:
            result = self.col.update_one(
                {"_id": ObjectId(followup_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def count_overdue(self) -> int:
        now = datetime.utcnow()
        return self.col.count_documents({
            "status": "pending",
            "due_date": {"$lt": now}
        })

    def count_pending(self) -> int:
        return self.col.count_documents({"status": "pending"})

    def count_by_status(self) -> dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        result = {}
        for doc in self.col.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    def auto_mark_overdue(self) -> int:
        """Mark pending follow-ups as overdue if past due date."""
        now = datetime.utcnow()
        result = self.col.update_many(
            {"status": "pending", "due_date": {"$lt": now}},
            {"$set": {"status": "overdue"}}
        )
        return result.modified_count
