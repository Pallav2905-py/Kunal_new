"""
LeadFlow — Application Service Registry
Centralized dependency injection / service locator.
"""

from __future__ import annotations

from typing import Optional
from pymongo.database import Database

from app.database.mongodb import MongoDB
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.lead_repo import LeadRepository
from app.database.repositories.call_repo import CallRepository
from app.database.repositories.followup_repo import FollowUpRepository
from app.backend.services.auth_service import AuthService
from app.backend.services.import_service import LeadImportService
from app.backend.models.domain import AuthToken, UserRole


class AppServices:
    """
    Application-wide service registry.
    Created once at startup; passed through the application.
    """

    def __init__(self, db: Database) -> None:
        # Repositories
        self.user_repo = UserRepository(db)
        self.lead_repo = LeadRepository(db)
        self.call_repo = CallRepository(db)
        self.followup_repo = FollowUpRepository(db)

        # Services
        self.auth_service = AuthService(self.user_repo)
        self.import_service = LeadImportService(self.lead_repo)

        # Lazy-loaded AI services
        self._gemini = None
        self._stt = None
        self._pipeline = None
        self._analytics = None

        self.db = db

        # Current user session
        self.current_user: Optional[AuthToken] = None

    @property
    def current_role(self) -> Optional[UserRole]:
        if self.current_user:
            return self.current_user.user.role
        return None

    @property
    def current_user_id(self) -> Optional[str]:
        if self.current_user:
            return self.current_user.user.id
        return None

    @property
    def current_user_name(self) -> Optional[str]:
        if self.current_user:
            return self.current_user.user.name
        return None

    def get_gemini_service(self):
        if self._gemini is None:
            from app.ai.gemini_service import create_gemini_service
            self._gemini = create_gemini_service()
        return self._gemini

    def get_stt_service(self):
        if self._stt is None:
            from app.ai.transcription import create_transcription_service
            self._stt = create_transcription_service()
        return self._stt

    def get_pipeline(self):
        if self._pipeline is None:
            from app.ai.langchain_pipeline import AnalysisPipeline
            self._pipeline = AnalysisPipeline(
                transcription_service=self.get_stt_service(),
                gemini_service=self.get_gemini_service(),
                call_repo=self.call_repo,
                lead_repo=self.lead_repo,
            )
        return self._pipeline

    def get_analytics_orchestrator(self):
        if self._analytics is None:
            from app.analytics_engine.orchestrator import AnalyticsOrchestrator
            self._analytics = AnalyticsOrchestrator(
                db=self.db,
                gemini=self.get_gemini_service(),
            )
        return self._analytics

    def is_admin(self) -> bool:
        return self.current_role == UserRole.ADMIN

    def is_manager(self) -> bool:
        return self.current_role in (UserRole.ADMIN, UserRole.SALES_MANAGER)

    def can_manage_users(self) -> bool:
        return self.is_admin()

    def can_import_leads(self) -> bool:
        return self.current_role in (
            UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_EXECUTIVE
        )

    def can_upload_recordings(self) -> bool:
        return self.current_role in (
            UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_EXECUTIVE
        )

    def can_view_analytics(self) -> bool:
        return self.current_role in (UserRole.ADMIN, UserRole.SALES_MANAGER)
AQ.Ab8RN6I-JWAvasnb5wPyblcNn8GlJ_tnFl5-kQ7CC5m5_GyhVAAQ.Ab8RN6I-JWAvasnb5wPyblcNn8GlJ_tnFl5-kQ7CC5m5_GyhVAAQ.Ab8RN6I-JWAvasnb5wPyblcNn8GlJ_tnFl5-kQ7CC5m5_GyhVAAQ.Ab8RN6I-JWAvasnb5wPyblcNn8GlJ_tnFl5-kQ7CC5m5_GyhVAAQ.Ab8RN6I-JWAvasnb5wPyblcNn8GlJ_tnFl5-kQ7CC5m5_GyhVA