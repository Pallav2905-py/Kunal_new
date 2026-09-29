"""
LeadFlow — Analytics Metrics (deterministic, no Gemini)
All calculations use Python + MongoDB aggregation pipelines.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any

from pymongo.database import Database

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
    """All analytics metrics computed deterministically."""

    # Lead metrics
    total_leads: int = 0
    leads_by_status: dict[str, int] = field(default_factory=dict)
    leads_by_priority: dict[str, int] = field(default_factory=dict)
    high_priority_count: int = 0
    avg_lead_score: float = 0.0

    # Conversion
    converted_count: int = 0
    lost_count: int = 0
    conversion_rate: float = 0.0

    # Calls
    total_calls: int = 0
    analyzed_calls: int = 0

    # Sentiment distribution
    sentiment_distribution: dict[str, int] = field(default_factory=dict)

    # Intent distribution
    intent_distribution: dict[str, int] = field(default_factory=dict)

    # Follow-ups
    total_followups: int = 0
    pending_followups: int = 0
    overdue_followups: int = 0
    completed_followups: int = 0
    followup_completion_rate: float = 0.0

    # Score buckets
    score_high: int = 0     # 70-100
    score_medium: int = 0   # 40-69
    score_low: int = 0      # 0-39

    # Executive performance
    executive_performance: list[dict[str, Any]] = field(default_factory=list)

    # Common objections (from analyses)
    common_objections: list[str] = field(default_factory=list)

    # Computed at
    computed_at: datetime = field(default_factory=datetime.utcnow)


class MetricsCalculator:
    """Calculates all CRM metrics deterministically from MongoDB."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def compute_all(self) -> PipelineMetrics:
        """Compute full metrics. Used by Analytics Agent."""
        m = PipelineMetrics()
        start = datetime.utcnow()

        try:
            m.total_leads = self._count_leads()
            m.leads_by_status = self._leads_by_status()
            m.leads_by_priority = self._leads_by_priority()
            m.high_priority_count = m.leads_by_priority.get("high", 0)
            m.avg_lead_score = self._avg_lead_score()
            m.converted_count = m.leads_by_status.get("converted", 0)
            m.lost_count = m.leads_by_status.get("lost", 0)
            m.conversion_rate = self._conversion_rate(m.total_leads, m.converted_count)
            m.total_calls = self._count_calls()
            m.analyzed_calls = self._count_analyzed_calls()
            m.sentiment_distribution = self._sentiment_distribution()
            m.intent_distribution = self._intent_distribution()
            m.total_followups, m.pending_followups, m.overdue_followups, m.completed_followups = self._followup_counts()
            m.followup_completion_rate = self._followup_rate(m.total_followups, m.completed_followups)
            m.score_high, m.score_medium, m.score_low = self._score_buckets()
            m.executive_performance = self._executive_performance()
            m.common_objections = self._common_objections()
            m.computed_at = datetime.utcnow()

            elapsed = (datetime.utcnow() - start).total_seconds()
            logger.info(f"Metrics computed in {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"Metrics computation error: {e}")

        return m

    def _count_leads(self) -> int:
        return self.db.leads.count_documents({})

    def _leads_by_status(self) -> dict[str, int]:
        pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        return {doc["_id"]: doc["count"] for doc in self.db.leads.aggregate(pipeline)}

    def _leads_by_priority(self) -> dict[str, int]:
        pipeline = [{"$group": {"_id": "$priority", "count": {"$sum": 1}}}]
        return {doc["_id"]: doc["count"] for doc in self.db.leads.aggregate(pipeline)}

    def _avg_lead_score(self) -> float:
        pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$lead_score"}}}]
        docs = list(self.db.leads.aggregate(pipeline))
        return round(docs[0].get("avg", 0) or 0, 1) if docs else 0.0

    def _conversion_rate(self, total: int, converted: int) -> float:
        if total == 0:
            return 0.0
        return round((converted / total) * 100, 1)

    def _count_calls(self) -> int:
        return self.db.call_records.count_documents({})

    def _count_analyzed_calls(self) -> int:
        return self.db.call_records.count_documents({"analysis_status": "completed"})

    def _sentiment_distribution(self) -> dict[str, int]:
        pipeline = [{"$group": {"_id": "$analysis.sentiment", "count": {"$sum": 1}}}]
        return {doc["_id"]: doc["count"] for doc in self.db.call_analyses.aggregate(pipeline)}

    def _intent_distribution(self) -> dict[str, int]:
        pipeline = [{"$group": {"_id": "$analysis.intent", "count": {"$sum": 1}}}]
        return {doc["_id"]: doc["count"] for doc in self.db.call_analyses.aggregate(pipeline)}

    def _followup_counts(self) -> tuple[int, int, int, int]:
        now = datetime.utcnow()
        total = self.db.follow_ups.count_documents({})
        pending = self.db.follow_ups.count_documents({"status": "pending"})
        overdue = self.db.follow_ups.count_documents({
            "status": {"$in": ["pending", "overdue"]},
            "due_date": {"$lt": now}
        })
        completed = self.db.follow_ups.count_documents({"status": "completed"})
        return total, pending, overdue, completed

    def _followup_rate(self, total: int, completed: int) -> float:
        if total == 0:
            return 0.0
        return round((completed / total) * 100, 1)

    def _score_buckets(self) -> tuple[int, int, int]:
        high = self.db.leads.count_documents({"lead_score": {"$gte": 70}})
        medium = self.db.leads.count_documents({"lead_score": {"$gte": 40, "$lt": 70}})
        low = self.db.leads.count_documents({"lead_score": {"$lt": 40}})
        return high, medium, low

    def _executive_performance(self) -> list[dict[str, Any]]:
        pipeline = [
            {
                "$group": {
                    "_id": "$assigned_to_name",
                    "leads": {"$sum": 1},
                    "avg_score": {"$avg": "$lead_score"},
                    "converted": {
                        "$sum": {"$cond": [{"$eq": ["$status", "converted"]}, 1, 0]}
                    }
                }
            },
            {"$match": {"_id": {"$ne": None}}},
            {"$sort": {"leads": -1}},
            {"$limit": 10},
        ]
        result = []
        for doc in self.db.leads.aggregate(pipeline):
            result.append({
                "name": doc["_id"],
                "leads": doc["leads"],
                "avg_score": round(doc.get("avg_score", 0) or 0, 1),
                "converted": doc.get("converted", 0),
            })
        return result

    def _common_objections(self) -> list[str]:
        """Extract all objections from analyses and return top ones."""
        pipeline = [
            {"$unwind": "$analysis.objections"},
            {"$group": {"_id": "$analysis.objections", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        return [doc["_id"] for doc in self.db.call_analyses.aggregate(pipeline)]
