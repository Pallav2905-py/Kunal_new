"""
LeadFlow — LangChain Analysis Pipeline
Orchestrates transcription → Gemini analysis → Pydantic validation.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.ai.gemini_service import GeminiService
from app.ai.transcription import TranscriptionService
from app.ai.prompts import (
    CONVERSATION_ANALYSIS_SYSTEM,
    CONVERSATION_ANALYSIS_HUMAN,
)
from app.backend.models.domain import (
    CallAnalysis, CallAnalysisDB, CallRecordDB, LeadPriority
)
from app.database.repositories.call_repo import CallRepository
from app.database.repositories.lead_repo import LeadRepository

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Core pipeline: audio → transcript → Gemini → Pydantic → MongoDB.
    """

    def __init__(
        self,
        transcription_service: TranscriptionService,
        gemini_service: GeminiService,
        call_repo: CallRepository,
        lead_repo: LeadRepository,
    ) -> None:
        self.stt = transcription_service
        self.gemini = gemini_service
        self.call_repo = call_repo
        self.lead_repo = lead_repo

    def process_recording(
        self,
        call_id: str,
        progress_callback=None,
    ) -> CallAnalysisDB:
        """
        Full pipeline for a call record.
        progress_callback(step: str, percent: int) if provided.
        Returns CallAnalysisDB on success.
        Raises on failure.
        """
        def _progress(step: str, pct: int):
            if progress_callback:
                progress_callback(step, pct)
            logger.info(f"[Pipeline] {step} ({pct}%)")

        pipeline_start = time.time()

        # ── 1. Load call record ──────────────────────
        _progress("Loading call record", 5)
        record = self.call_repo.find_record_by_id(call_id)
        if not record:
            raise RuntimeError(f"Call record not found: {call_id}")

        # Mark processing
        self.call_repo.update_record(call_id, {"analysis_status": "processing"})

        try:
            # ── 2. Transcription ─────────────────────
            _progress("Transcribing conversation", 20)
            transcript, duration = self.stt.transcribe(record.file_path)

            # Save transcript
            self.call_repo.update_record(call_id, {
                "transcript": transcript,
                "duration_seconds": duration,
                "transcribed_at": datetime.utcnow(),
            })
            _progress("Transcription complete", 45)

            # ── 3. AI Analysis ───────────────────────
            _progress("Analyzing conversation with AI", 50)
            analysis = self._analyze_transcript(transcript)
            _progress("AI analysis complete", 80)

            # ── 4. Pydantic Validation ───────────────
            _progress("Validating AI output", 85)
            # (already validated in _analyze_transcript)

            # ── 5. Save analysis ─────────────────────
            _progress("Updating CRM", 90)
            elapsed = time.time() - pipeline_start

            analysis_db = CallAnalysisDB(
                call_id=call_id,
                lead_id=record.lead_id,
                analysis=analysis,
                processing_time_seconds=round(elapsed, 2),
            )
            analysis_db = self.call_repo.create_analysis(analysis_db)

            # ── 6. Update call record ─────────────────
            self.call_repo.update_record(call_id, {
                "analysis_status": "completed",
                "analyzed_at": datetime.utcnow(),
            })

            # ── 7. Update lead ───────────────────────
            self._update_lead_from_analysis(record.lead_id, analysis)
            _progress("Follow-up generated", 98)
            _progress("Completed", 100)

            logger.info(
                f"Pipeline completed for call {call_id} "
                f"in {elapsed:.1f}s"
            )
            return analysis_db

        except Exception as e:
            self.call_repo.update_record(call_id, {"analysis_status": "failed"})
            logger.error(f"Pipeline failed for call {call_id}: {e}")
            raise

    def _analyze_transcript(self, transcript: str) -> CallAnalysis:
        """
        Call Gemini and parse the result into strict Pydantic schema.
        Retries once with a correction prompt if validation fails.
        """
        prompt = CONVERSATION_ANALYSIS_HUMAN.format(transcript=transcript)

        for attempt in range(2):
            try:
                raw = self.gemini.generate_json(
                    prompt=prompt,
                    system_instruction=CONVERSATION_ANALYSIS_SYSTEM,
                )
                # Enforce priority matches score
                score = int(raw.get("lead_score", 0))
                if score < 40:
                    raw["priority"] = "low"
                elif score < 70:
                    raw["priority"] = "medium"
                else:
                    raw["priority"] = "high"

                analysis = CallAnalysis(**raw)
                return analysis

            except Exception as e:
                if attempt == 0:
                    logger.warning(f"Analysis attempt 1 failed: {e}. Retrying...")
                    continue
                raise RuntimeError(
                    f"AI analysis validation failed after 2 attempts: {e}"
                ) from e

        raise RuntimeError("Analysis failed")

    def _update_lead_from_analysis(self, lead_id: str, analysis: CallAnalysis) -> None:
        """Update lead CRM fields based on AI analysis results."""
        updates = {
            "sentiment": analysis.sentiment.value,
            "intent": analysis.intent.value,
            "lead_score": analysis.lead_score,
            "priority": analysis.priority.value,
            "requirements": analysis.requirements,
            "objections": analysis.objections,
            "purchase_timeline": analysis.purchase_timeline,
            "ai_summary": analysis.summary,
            "last_contact": datetime.utcnow(),
        }

        # Upgrade status if new
        lead = self.lead_repo.find_by_id(lead_id)
        if lead and lead.status.value == "new":
            updates["status"] = "contacted"

        self.lead_repo.update(lead_id, updates)
        logger.info(f"Lead {lead_id} updated from analysis")
