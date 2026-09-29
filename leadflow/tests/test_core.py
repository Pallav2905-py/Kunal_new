"""
LeadFlow — Tests for authentication, lead validation, import, AI schema validation.
"""

from __future__ import annotations

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.backend.models.domain import (
    UserCreate, UserDB, UserRole, LeadCreate, LeadSource,
    CallAnalysis, CallIntent, CallSentiment, LeadPriority,
    ImportValidationResult,
)
from app.backend.services.auth_service import (
    hash_password, verify_password, create_jwt_token,
    decode_jwt_token, AuthService, TokenPayload,
)


# ─────────────────────────────────────────────
# Authentication Tests
# ─────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_verify_correct_password(self):
        hashed = hash_password("test123")
        assert verify_password("test123", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("test123")
        assert verify_password("wrongpass", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        h1 = hash_password("pass1")
        h2 = hash_password("pass2")
        assert h1 != h2


class TestJWT:
    def test_create_and_decode_token(self):
        payload = TokenPayload(
            user_id="507f1f77bcf86cd799439011",
            email="test@example.com",
            role=UserRole.SALES_EXECUTIVE,
            name="Test User",
        )
        token = create_jwt_token(payload)
        assert isinstance(token, str)

        decoded = decode_jwt_token(token)
        assert decoded is not None
        assert decoded.email == "test@example.com"
        assert decoded.role == UserRole.SALES_EXECUTIVE

    def test_invalid_token_returns_none(self):
        result = decode_jwt_token("invalid.token.here")
        assert result is None

    def test_tampered_token_returns_none(self):
        payload = TokenPayload(
            user_id="507f1f77bcf86cd799439011",
            email="test@example.com",
            role=UserRole.ADMIN,
            name="Admin",
        )
        token = create_jwt_token(payload)
        tampered = token[:-5] + "XXXXX"
        result = decode_jwt_token(tampered)
        assert result is None


class TestRBACPermissions:
    def setup_method(self):
        self.auth = AuthService(MagicMock())

    def test_admin_can_manage_users(self):
        assert self.auth.can_manage_users(UserRole.ADMIN) is True

    def test_sales_manager_cannot_manage_users(self):
        assert self.auth.can_manage_users(UserRole.SALES_MANAGER) is False

    def test_admin_can_import(self):
        assert self.auth.can_import_leads(UserRole.ADMIN) is True

    def test_support_cannot_import(self):
        assert self.auth.can_import_leads(UserRole.SUPPORT) is False

    def test_can_access_hierarchy(self):
        assert self.auth.can_access(UserRole.ADMIN, UserRole.SALES_MANAGER) is True
        assert self.auth.can_access(UserRole.SALES_EXECUTIVE, UserRole.ADMIN) is False


# ─────────────────────────────────────────────
# Lead Validation Tests
# ─────────────────────────────────────────────

class TestLeadValidation:
    def test_valid_lead(self):
        lead = LeadCreate(
            name="Rahul Sharma",
            company="TechCorp",
            phone="+91 98765 43210",
            email="rahul@techcorp.com",
        )
        assert lead.name == "Rahul Sharma"
        assert lead.email == "rahul@techcorp.com"

    def test_email_normalized_to_lowercase(self):
        lead = LeadCreate(name="Test User", email="TEST@EXAMPLE.COM")
        assert lead.email == "test@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            LeadCreate(name="Bad Email", email="not-an-email")

    def test_name_required(self):
        with pytest.raises(ValidationError):
            LeadCreate(name="")

    def test_lead_without_optional_fields(self):
        lead = LeadCreate(name="Minimal Lead")
        assert lead.company is None
        assert lead.phone is None
        assert lead.email is None
        assert lead.source == LeadSource.UNKNOWN

    def test_empty_email_accepted(self):
        lead = LeadCreate(name="No Email", email=None)
        assert lead.email is None


# ─────────────────────────────────────────────
# AI Schema Validation Tests
# ─────────────────────────────────────────────

class TestCallAnalysisSchema:
    def _valid_data(self) -> dict:
        return {
            "summary": "Customer interested in enterprise plan for 100 users.",
            "intent": CallIntent.PURCHASE,
            "sentiment": CallSentiment.POSITIVE,
            "requirements": ["CRM integration", "Analytics dashboard"],
            "objections": ["Pricing concern"],
            "purchase_timeline": "Within 30 days",
            "lead_score": 85,
            "priority": LeadPriority.HIGH,
            "follow_up_required": True,
            "follow_up_reason": "Send pricing proposal",
            "recommended_action": "Send detailed proposal and schedule demo",
            "confidence": 0.92,
        }

    def test_valid_analysis_passes(self):
        data = self._valid_data()
        analysis = CallAnalysis(**data)
        assert analysis.lead_score == 85
        assert analysis.confidence == 0.92

    def test_lead_score_below_zero_rejected(self):
        data = self._valid_data()
        data["lead_score"] = -5
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_lead_score_above_100_rejected(self):
        data = self._valid_data()
        data["lead_score"] = 105
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_confidence_above_1_rejected(self):
        data = self._valid_data()
        data["confidence"] = 1.5
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_confidence_below_0_rejected(self):
        data = self._valid_data()
        data["confidence"] = -0.1
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_invalid_intent_rejected(self):
        data = self._valid_data()
        data["intent"] = "WANTS_TO_BUY"  # Not in enum
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_invalid_sentiment_rejected(self):
        data = self._valid_data()
        data["sentiment"] = "HAPPY"
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_summary_too_short_rejected(self):
        data = self._valid_data()
        data["summary"] = "Short"
        with pytest.raises(ValidationError):
            CallAnalysis(**data)

    def test_empty_requirements_accepted(self):
        data = self._valid_data()
        data["requirements"] = []
        analysis = CallAnalysis(**data)
        assert analysis.requirements == []

    def test_none_purchase_timeline_accepted(self):
        data = self._valid_data()
        data["purchase_timeline"] = None
        analysis = CallAnalysis(**data)
        assert analysis.purchase_timeline is None

    def test_boundary_lead_score_0(self):
        data = self._valid_data()
        data["lead_score"] = 0
        analysis = CallAnalysis(**data)
        assert analysis.lead_score == 0

    def test_boundary_lead_score_100(self):
        data = self._valid_data()
        data["lead_score"] = 100
        analysis = CallAnalysis(**data)
        assert analysis.lead_score == 100

    def test_boundary_confidence_0(self):
        data = self._valid_data()
        data["confidence"] = 0.0
        analysis = CallAnalysis(**data)
        assert analysis.confidence == 0.0

    def test_boundary_confidence_1(self):
        data = self._valid_data()
        data["confidence"] = 1.0
        analysis = CallAnalysis(**data)
        assert analysis.confidence == 1.0


# ─────────────────────────────────────────────
# Lead Score Categorization
# ─────────────────────────────────────────────

class TestLeadScoreCategorization:
    def _score_to_priority(self, score: int) -> str:
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def test_score_0_is_low(self):
        assert self._score_to_priority(0) == "LOW"

    def test_score_39_is_low(self):
        assert self._score_to_priority(39) == "LOW"

    def test_score_40_is_medium(self):
        assert self._score_to_priority(40) == "MEDIUM"

    def test_score_69_is_medium(self):
        assert self._score_to_priority(69) == "MEDIUM"

    def test_score_70_is_high(self):
        assert self._score_to_priority(70) == "HIGH"

    def test_score_100_is_high(self):
        assert self._score_to_priority(100) == "HIGH"


# ─────────────────────────────────────────────
# UserCreate Validation
# ─────────────────────────────────────────────

class TestUserCreate:
    def test_valid_user(self):
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            password="securepassword",
            role=UserRole.SALES_EXECUTIVE,
        )
        assert user.name == "John Doe"

    def test_name_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(name="A", email="a@b.com", password="password123")

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John Doe", email="a@b.com", password="123")

    def test_email_normalized(self):
        user = UserCreate(name="Test User", email="TEST@DOMAIN.COM", password="password123")
        assert user.email == "test@domain.com"
