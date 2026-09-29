"""
LeadFlow — MongoDB Database Connection
"""

from __future__ import annotations

import logging
from typing import Optional
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""

    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    @classmethod
    def connect(cls, uri: str, db_name: str) -> None:
        """Connect to MongoDB and configure indexes."""
        try:
            cls._client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            # Verify connection
            cls._client.admin.command("ping")
            cls._db = cls._client[db_name]
            logger.info(f"Connected to MongoDB: {db_name}")
            cls._ensure_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    @classmethod
    def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB disconnected")

    @classmethod
    def get_db(cls) -> Database:
        if cls._db is None:
            raise RuntimeError("MongoDB not connected. Call MongoDB.connect() first.")
        return cls._db

    @classmethod
    def is_connected(cls) -> bool:
        try:
            if cls._client is None:
                return False
            cls._client.admin.command("ping")
            return True
        except Exception:
            return False

    @classmethod
    def _ensure_indexes(cls) -> None:
        """Create indexes for performance."""
        db = cls._db
        if db is None:
            return

        try:
            # Users
            db.users.create_index("email", unique=True)

            # Leads
            db.leads.create_index("phone")
            db.leads.create_index("email")
            db.leads.create_index("status")
            db.leads.create_index("assigned_to")
            db.leads.create_index("lead_score")
            db.leads.create_index("priority")
            db.leads.create_index([("created_at", pymongo.DESCENDING)])

            # Call records
            db.call_records.create_index("lead_id")
            db.call_records.create_index([("created_at", pymongo.DESCENDING)])

            # Call analyses
            db.call_analyses.create_index("call_id", unique=True)
            db.call_analyses.create_index("lead_id")
            db.call_analyses.create_index("analysis.sentiment")
            db.call_analyses.create_index("analysis.intent")

            # Follow-ups
            db.follow_ups.create_index("lead_id")
            db.follow_ups.create_index("due_date")
            db.follow_ups.create_index("status")
            db.follow_ups.create_index("assigned_to")

            # Audit logs
            db.audit_logs.create_index([("timestamp", pymongo.DESCENDING)])

            logger.info("MongoDB indexes ensured")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
