"""
LeadFlow — Call Recording Upload & Analysis Page
Shows upload dialog, processing pipeline, and analysis results.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QScrollArea,
    QFrame, QTextEdit, QSizePolicy, QProgressBar,
    QMessageBox, QTableWidgetItem,
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import (
    Panel, ProcessingStep, FieldRow, SentimentBadge,
    ScoreWidget, StatusBadge, PriorityBadge, EmptyState,
)
from app.backend.models.domain import (
    CallRecordDB, FollowUpDB, FollowUpStatus, LeadPriority
)
from app.config import settings

logger = logging.getLogger(__name__)


class AnalysisWorker(QObject):
    """Runs the full analysis pipeline in background."""
    step = Signal(str, int)  # step_name, percent
    done = Signal(str)        # analysis_id
    error = Signal(str)

    def __init__(self, services: AppServices, call_id: str):
        super().__init__()
        self.services = services
        self.call_id = call_id

    def run(self):
        try:
            pipeline = self.services.get_pipeline()

            def _progress(step, pct):
                self.step.emit(step, pct)

            analysis = pipeline.process_recording(self.call_id, _progress)

            # Auto-generate follow-up if required
            if analysis.analysis.follow_up_required:
                self._create_followup(analysis)

            self.done.emit(analysis.id)  # type: ignore
        except Exception as e:
            logger.error(f"Analysis worker error: {e}")
            self.error.emit(str(e))

    def _create_followup(self, analysis_db):
        """Auto-create follow-up recommendation from analysis."""
        try:
            record = self.services.call_repo.find_record_by_id(self.call_id)
            if not record:
                return

            lead = self.services.lead_repo.find_by_id(record.lead_id)
            if not lead:
                return

            a = analysis_db.analysis
            due_date = datetime.utcnow() + timedelta(days=2)

            followup = FollowUpDB(
                lead_id=record.lead_id,
                lead_name=lead.name,
                reason=a.follow_up_reason or a.recommended_action,
                due_date=due_date,
                assigned_to=self.services.current_user_id,
                assigned_to_name=self.services.current_user_name,
                priority=a.priority,
                notes=f"Auto-generated from AI analysis. Confidence: {a.confidence:.0%}",
            )
            self.services.followup_repo.create(followup)

            # Update lead next_followup
            self.services.lead_repo.update(record.lead_id, {
                "next_followup": due_date
            })
            logger.info(f"Auto follow-up created for lead {record.lead_id}")
        except Exception as e:
            logger.warning(f"Failed to create auto follow-up: {e}")


class CallsPage(QWidget):
    """Upload recording → process → view analysis."""

    def __init__(self, services: AppServices, lead_id: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.services = services
        self.lead_id = lead_id
        self._call_id: Optional[str] = None
        self._analysis_result = None
        self._thread: Optional[QThread] = None
        self._worker: Optional[AnalysisWorker] = None
        self._setup_ui()

        if lead_id:
            self._load_lead_info()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("page_header")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        self._title = QLabel("Call Analysis")
        self._title.setObjectName("page_title")
        self._lead_info_label = QLabel("Select a lead and upload a recording")
        self._lead_info_label.setStyleSheet("color: #626975; font-size: 12px; margin-left: 12px; margin-top: 3px;")

        h_layout.addWidget(self._title)
        h_layout.addWidget(self._lead_info_label)
        h_layout.addStretch()

        if self.services.can_upload_recordings():
            upload_btn = QPushButton("↑ Upload Recording")
            upload_btn.setObjectName("btn_primary")
            upload_btn.setFixedHeight(28)
            upload_btn.clicked.connect(self._upload_recording)
            h_layout.addWidget(upload_btn)

        layout.addWidget(header)

        # Scroll content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(20, 16, 20, 20)
        self._content_layout.setSpacing(16)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._build_content()

    def _build_content(self):
        # Processing pipeline panel
        pipeline_panel = Panel("Analysis Pipeline")
        self._steps = {
            "upload": ProcessingStep("Recording Uploaded"),
            "transcribe": ProcessingStep("Transcribing Conversation"),
            "analyze": ProcessingStep("Analyzing with AI"),
            "validate": ProcessingStep("Validating Output"),
            "crm": ProcessingStep("Updating CRM"),
            "followup": ProcessingStep("Generating Follow-up"),
            "complete": ProcessingStep("Completed"),
        }
        for step in self._steps.values():
            pipeline_panel.add_widget(step)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(4)
        pipeline_panel.add_widget(self._progress_bar)
        self._content_layout.addWidget(pipeline_panel)

        # Analysis results
        results_panel = Panel("Analysis Results")

        # Summary
        sum_label = QLabel("CALL SUMMARY")
        sum_label.setObjectName("field_label")
        self._summary_text = QLabel("Run analysis to see results.")
        self._summary_text.setWordWrap(True)
        self._summary_text.setStyleSheet("color: #9EA5B0; font-size: 12px; line-height: 1.5; padding: 4px 0;")
        results_panel.add_widget(sum_label)
        results_panel.add_widget(self._summary_text)
        results_panel.content_layout.addSpacing(8)

        # AI fields grid
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(20)

        left = QVBoxLayout()
        self._intent_row = FieldRow("Intent", "—")
        self._sentiment_row = FieldRow("Sentiment", "—")
        self._score_row = FieldRow("Lead Score", "—")
        self._priority_row = FieldRow("Priority", "—")
        self._timeline_row = FieldRow("Purchase Timeline", "—")
        for w in [self._intent_row, self._sentiment_row,
                  self._score_row, self._priority_row, self._timeline_row]:
            left.addWidget(w)

        right = QVBoxLayout()
        self._followup_row = FieldRow("Follow-up Required", "—")
        self._followup_reason_row = FieldRow("Follow-up Reason", "—")
        self._action_row = FieldRow("Recommended Action", "—")
        self._confidence_row = FieldRow("AI Confidence", "—")
        for w in [self._followup_row, self._followup_reason_row,
                  self._action_row, self._confidence_row]:
            right.addWidget(w)

        grid_layout.addLayout(left, 1)
        grid_layout.addLayout(right, 1)
        results_panel.add_widget(grid_widget)

        # Requirements + Objections
        req_label = QLabel("REQUIREMENTS")
        req_label.setObjectName("field_label")
        self._req_text = QLabel("—")
        self._req_text.setWordWrap(True)
        self._req_text.setStyleSheet("color: #9EA5B0; font-size: 12px;")

        obj_label = QLabel("OBJECTIONS")
        obj_label.setObjectName("field_label")
        self._obj_text = QLabel("—")
        self._obj_text.setWordWrap(True)
        self._obj_text.setStyleSheet("color: #9EA5B0; font-size: 12px;")

        results_panel.content_layout.addSpacing(8)
        results_panel.add_widget(req_label)
        results_panel.add_widget(self._req_text)
        results_panel.content_layout.addSpacing(8)
        results_panel.add_widget(obj_label)
        results_panel.add_widget(self._obj_text)

        self._content_layout.addWidget(results_panel)

        # Transcript panel
        transcript_panel = Panel("Transcript")
        self._transcript_text = QTextEdit()
        self._transcript_text.setObjectName("transcript_box")
        self._transcript_text.setReadOnly(True)
        self._transcript_text.setPlaceholderText("Transcript will appear here after analysis...")
        self._transcript_text.setFixedHeight(180)
        transcript_panel.add_widget(self._transcript_text)
        self._content_layout.addWidget(transcript_panel)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._update_crm_btn = QPushButton("Update CRM")
        self._update_crm_btn.setObjectName("btn_primary")
        self._update_crm_btn.setEnabled(False)

        self._reanalyze_btn = QPushButton("Re-analyze")
        self._reanalyze_btn.setEnabled(False)
        self._reanalyze_btn.clicked.connect(self._reanalyze)

        btn_row.addWidget(self._reanalyze_btn)
        btn_row.addWidget(self._update_crm_btn)
        self._content_layout.addLayout(btn_row)
        self._content_layout.addStretch()

    def _load_lead_info(self):
        lead = self.services.lead_repo.find_by_id(self.lead_id)
        if lead:
            self._lead_info_label.setText(f"{lead.name} · {lead.company or ''}")

    def _upload_recording(self):
        if not self.lead_id:
            QMessageBox.warning(self, "No Lead Selected",
                               "Please open a specific lead to upload a recording.")
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Upload Call Recording", "",
            "Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac)"
        )
        if not path:
            return

        source_path = Path(path)
        size_mb = source_path.stat().st_size / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            QMessageBox.critical(self, "File Too Large",
                               f"File size ({size_mb:.1f}MB) exceeds {settings.max_upload_size_mb}MB limit.")
            return

        # Copy to uploads directory
        try:
            upload_dir = Path(settings.upload_dir)
            upload_dir.mkdir(parents=True, exist_ok=True)

            ext = source_path.suffix.lower()
            filename = f"{uuid.uuid4()}{ext}"
            dest_path = upload_dir / filename

            shutil.copy2(str(source_path), str(dest_path))

            # Create call record
            lead = self.services.lead_repo.find_by_id(self.lead_id)
            record = CallRecordDB(
                lead_id=self.lead_id,
                lead_name=lead.name if lead else "",
                file_path=str(dest_path),
                file_name=source_path.name,
                file_size_bytes=source_path.stat().st_size,
                uploaded_by=self.services.current_user_id,
                uploaded_by_name=self.services.current_user_name,
            )
            record = self.services.call_repo.create_record(record)
            self._call_id = record.id

            # Reset pipeline
            self._reset_pipeline()
            self._steps["upload"].set_status("done")
            self._progress_bar.setValue(15)

            # Start analysis
            self._start_analysis(record.id)

        except Exception as e:
            QMessageBox.critical(self, "Upload Error", f"Failed to upload recording:\n{str(e)}")

    def _start_analysis(self, call_id: str):
        """Launch analysis in background thread."""
        if self._thread and self._thread.isRunning():
            return

        try:
            self.services.get_gemini_service()  # validate API key early
        except ValueError as e:
            QMessageBox.critical(self, "AI Configuration Error", str(e))
            return

        self._thread = QThread()
        self._worker = AnalysisWorker(self.services, call_id)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.step.connect(self._on_step)
        self._worker.done.connect(self._on_analysis_done)
        self._worker.error.connect(self._on_analysis_error)
        self._worker.done.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_step(self, step_name: str, percent: int):
        self._progress_bar.setValue(percent)

        # Map step name to step widget
        name_lower = step_name.lower()
        if "transcri" in name_lower:
            self._steps["transcribe"].set_status("active")
        elif "analyz" in name_lower and "complete" not in name_lower:
            self._steps["transcribe"].set_status("done")
            self._steps["analyze"].set_status("active")
        elif "validat" in name_lower:
            self._steps["analyze"].set_status("done")
            self._steps["validate"].set_status("active")
        elif "crm" in name_lower or "updating" in name_lower:
            self._steps["validate"].set_status("done")
            self._steps["crm"].set_status("active")
        elif "follow" in name_lower:
            self._steps["crm"].set_status("done")
            self._steps["followup"].set_status("active")
        elif "complet" in name_lower:
            self._steps["followup"].set_status("done")
            self._steps["complete"].set_status("done")

    def _on_analysis_done(self, analysis_id: str):
        self._progress_bar.setValue(100)
        for step in self._steps.values():
            step.set_status("done")

        # Load and display analysis
        try:
            record = self.services.call_repo.find_record_by_id(self._call_id)  # type: ignore
            analysis_db = self.services.call_repo.find_analysis_by_call(self._call_id)  # type: ignore

            if record and record.transcript:
                self._transcript_text.setPlainText(record.transcript)

            if analysis_db:
                a = analysis_db.analysis
                self._summary_text.setText(a.summary)
                self._intent_row.set_value(a.intent.value)
                self._sentiment_row.set_value(a.sentiment.value)
                self._score_row.set_value(f"{a.lead_score} / 100")
                self._priority_row.set_value(a.priority.value.upper())
                self._timeline_row.set_value(a.purchase_timeline or "Not specified")
                self._followup_row.set_value("Yes" if a.follow_up_required else "No")
                self._followup_reason_row.set_value(a.follow_up_reason or "—")
                self._action_row.set_value(a.recommended_action)
                self._confidence_row.set_value(f"{a.confidence:.0%}")

                self._req_text.setText(
                    "\n".join(f"• {r}" for r in a.requirements) if a.requirements else "None identified"
                )
                self._obj_text.setText(
                    "\n".join(f"• {o}" for o in a.objections) if a.objections else "None raised"
                )

                self._update_crm_btn.setEnabled(True)
                self._reanalyze_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"Display analysis error: {e}")

    def _on_analysis_error(self, msg: str):
        for step_id, step in self._steps.items():
            if step._status == "active":
                step.set_status("error")
                break

        QMessageBox.critical(
            self, "Analysis Failed",
            f"AI analysis could not be completed.\n\n{msg}\n\nPlease check your configuration and retry."
        )
        self._reanalyze_btn.setEnabled(True)

    def _reanalyze(self):
        if self._call_id:
            self._reset_pipeline()
            self._steps["upload"].set_status("done")
            self._start_analysis(self._call_id)

    def _reset_pipeline(self):
        for step in self._steps.values():
            step.set_status("pending")
        self._progress_bar.setValue(0)
        self._summary_text.setText("Processing...")
        self._transcript_text.clear()
        self._update_crm_btn.setEnabled(False)
        self._reanalyze_btn.setEnabled(False)

    def set_lead(self, lead_id: str):
        """Switch to a different lead."""
        self.lead_id = lead_id
        self._call_id = None
        self._reset_pipeline()
        self._steps["upload"].set_status("pending")
        self._summary_text.setText("Upload a recording to begin analysis.")
        self._load_lead_info()
