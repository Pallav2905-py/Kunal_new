"""
LeadFlow — Call Repository
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pymongo.database import Database

from app.backend.models.domain import CallRecordDB, CallAnalysisDB, AnalysisStatus

logger = logging.getLogger(__name__)


def _doc_to_call(doc: dict) -> CallRecordDB:
    doc["id"] = str(doc.pop("_id"))
    return CallRecordDB(**doc)


def _doc_to_analysis(doc: dict) -> CallAnalysisDB:
    doc["id"] = str(doc.pop("_id"))
    return CallAnalysisDB(**doc)


class CallRepository:
    def __init__(self, db: Database) -> None:
        self.records = db.call_records
        self.analyses = db.call_analyses

    # ── Records ──────────────────────────────────

    def create_record(self, record: CallRecordDB) -> CallRecordDB:
        doc = record.model_dump(exclude={"id"})
        result = self.records.insert_one(doc)
        record.id = str(result.inserted_id)
        return record

    def find_record_by_id(self, call_id: str) -> Optional[CallRecordDB]:
        try:
            doc = self.records.find_one({"_id": ObjectId(call_id)})
            if doc:
                return _doc_to_call(doc)
        except Exception:
            pass
        return None

    def update_record(self, call_id: str, updates: dict) -> bool:
        try:
            result = self.records.update_one(
                {"_id": ObjectId(call_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Call record update error: {e}")
            return False

    def list_records_for_lead(self, lead_id: str) -> list[CallRecordDB]:
        docs = self.records.find(
            {"lead_id": lead_id},
            sort=[("created_at", -1)]
        )
        return [_doc_to_call(doc) for doc in docs]

    def list_recent_records(self, limit: int = 20) -> list[CallRecordDB]:
        docs = self.records.find(
            {},
            sort=[("created_at", -1)]
        ).limit(limit)
        return [_doc_to_call(doc) for doc in docs]

    def count_total(self) -> int:
        return self.records.count_documents({})

    def count_analyzed(self) -> int:
        return self.records.count_documents({"analysis_status": "completed"})

    # ── Analyses ─────────────────────────────────

    def create_analysis(self, analysis: CallAnalysisDB) -> CallAnalysisDB:
        doc = analysis.model_dump(exclude={"id"})
        result = self.analyses.insert_one(doc)
        analysis.id = str(result.inserted_id)
        return analysis

    def find_analysis_by_call(self, call_id: str) -> Optional[CallAnalysisDB]:
        doc = self.analyses.find_one({"call_id": call_id})
        if doc:
            return _doc_to_analysis(doc)
        return None

    def list_recent_analyses(self, limit: int = 20) -> list[CallAnalysisDB]:
        docs = self.analyses.find(
            {},
            sort=[("created_at", -1)]
        ).limit(limit)
        return [_doc_to_analysis(doc) for doc in docs]

    def sentiment_distribution(self) -> dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$analysis.sentiment", "count": {"$sum": 1}}}
        ]
        result = {}
        for doc in self.analyses.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    def intent_distribution(self) -> dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$analysis.intent", "count": {"$sum": 1}}}
        ]
        result = {}
        for doc in self.analyses.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    def average_lead_score_from_analyses(self) -> float:
        pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": "$analysis.lead_score"}}}
        ]
        docs = list(self.analyses.aggregate(pipeline))
        if docs:
            return round(docs[0].get("avg", 0) or 0, 1)
        return 0.0
