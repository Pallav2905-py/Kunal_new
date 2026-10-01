"""
LeadFlow — Pydantic domain models
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
import re


# ─────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────

class UserRole(str, Enum):
    ADMIN = "admin"
    SALES_MANAGER = "sales_manager"
    SALES_EXECUTIVE = "sales_executive"
    SUPPORT = "support"


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    FOLLOW_UP = "follow_up"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"


class LeadPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    EMAIL_CAMPAIGN = "email_campaign"
    LINKEDIN = "linkedin"
    TRADE_SHOW = "trade_show"
    PARTNER = "partner"
    IMPORT = "import"
    UNKNOWN = "unknown"


class CallIntent(str, Enum):
    PURCHASE = "PURCHASE"
    INQUIRY = "INQUIRY"
    DEMO_REQUEST = "DEMO_REQUEST"
    NEGOTIATION = "NEGOTIATION"
    SUPPORT = "SUPPORT"
    FOLLOW_UP = "FOLLOW_UP"
    NOT_INTERESTED = "NOT_INTERESTED"
    UNKNOWN = "UNKNOWN"


class CallSentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"


class FollowUpStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ─────────────────────────────────────────────
# User Models
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=200)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.SALES_EXECUTIVE
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email address")
        return v.lower()


class UserDB(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class UserPublic(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


# ─────────────────────────────────────────────
# Lead Models
# ─────────────────────────────────────────────

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    source: LeadSource = LeadSource.UNKNOWN
    campaign: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email address")
        return v.lower()


class LeadDB(BaseModel):
    id: Optional[str] = None
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    source: LeadSource = LeadSource.UNKNOWN
    campaign: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    priority: LeadPriority = LeadPriority.MEDIUM
    lead_score: int = 0
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    notes: Optional[str] = None
    # AI-populated fields
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    requirements: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    purchase_timeline: Optional[str] = None
    ai_summary: Optional[str] = None
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_contact: Optional[datetime] = None
    next_followup: Optional[datetime] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    lead_score: Optional[int] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    requirements: Optional[list[str]] = None
    objections: Optional[list[str]] = None
    purchase_timeline: Optional[str] = None
    ai_summary: Optional[str] = None
    next_followup: Optional[datetime] = None


# ─────────────────────────────────────────────
# Call Models
# ─────────────────────────────────────────────

class CallRecordDB(BaseModel):
    id: Optional[str] = None
    lead_id: str
    lead_name: Optional[str] = None
    file_path: str
    file_name: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    transcript: Optional[str] = None
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING
    uploaded_by: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transcribed_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# AI Analysis Models — strict Pydantic schema
# ─────────────────────────────────────────────

class CallAnalysis(BaseModel):
    """Strict Pydantic schema for Gemini structured output."""

    summary: str = Field(..., min_length=10)
    intent: CallIntent
    sentiment: CallSentiment
    requirements: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    purchase_timeline: Optional[str] = None
    lead_score: int = Field(..., ge=0, le=100)
    priority: LeadPriority
    follow_up_required: bool
    follow_up_reason: Optional[str] = None
    recommended_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority_before(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_lower = v.strip().lower()
            if v_lower in ("low", "medium", "high"):
                return LeadPriority(v_lower)
        return v

    @field_validator("intent", mode="before")
    @classmethod
    def validate_intent_before(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper()
            for item in CallIntent:
                if item.value == v_upper:
                    return item
        return v

    @field_validator("sentiment", mode="before")
    @classmethod
    def validate_sentiment_before(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper()
            for item in CallSentiment:
                if item.value == v_upper:
                    return item
        return v

    @field_validator("lead_score")
    @classmethod
    def validate_lead_score(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError(f"lead_score must be 0-100, got {v}")
        return v

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"confidence must be 0.0-1.0, got {v}")
        return v


class CallAnalysisDB(BaseModel):
    id: Optional[str] = None
    call_id: str
    lead_id: str
    analysis: CallAnalysis
    raw_response: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────
# Follow-up Models
# ─────────────────────────────────────────────

class FollowUpCreate(BaseModel):
    lead_id: str
    lead_name: Optional[str] = None
    reason: str
    due_date: datetime
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    priority: LeadPriority = LeadPriority.MEDIUM
    notes: Optional[str] = None


class FollowUpDB(BaseModel):
    id: Optional[str] = None
    lead_id: str
    lead_name: Optional[str] = None
    reason: str
    due_date: datetime
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    priority: LeadPriority = LeadPriority.MEDIUM
    status: FollowUpStatus = FollowUpStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# Audit Log Model
# ─────────────────────────────────────────────

class AuditLog(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────
# Auth Models
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenPayload(BaseModel):
    user_id: str
    email: str
    role: UserRole
    name: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# ─────────────────────────────────────────────
# Import Models
# ─────────────────────────────────────────────

class ImportValidationResult(BaseModel):
    total: int
    valid: int
    duplicates: int
    invalid: int
    errors: list[dict[str, Any]] = Field(default_factory=list)
    valid_leads: list[LeadCreate] = Field(default_factory=list)
