"""
LeadFlow — Lead Detail Page
CRM record view with tabs: Overview, Calls, AI Analysis, Follow-ups, Activity.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QScrollArea,
    QTableWidgetItem, QHeaderView, QFrame, QTextEdit, QSplitter,
    QSizePolicy,
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import (
    Panel, DataTable, StatusBadge, PriorityBadge,
    SentimentBadge, ScoreWidget, FieldRow,
    SectionHeader, EmptyState,
)
from app.backend.models.domain import LeadDB

logger = logging.getLogger(__name__)


class LeadDetailPage(QWidget):
    """Full lead detail workspace."""

    go_back = Signal()
    open_call_analysis = Signal(str)  # call_id
    open_upload_recording = Signal(str)  # lead_id

    def __init__(self, services: AppServices, lead_id: str, parent=None):
        super().__init__(parent)
        self.services = services
        self.lead_id = lead_id
        self._lead: Optional[LeadDB] = None
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        self._header = QWidget()
        self._header.setObjectName("page_header")
        self._header.setFixedHeight(56)
        h_layout = QHBoxLayout(self._header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        back_btn = QPushButton("← Leads")
        back_btn.setObjectName("icon_btn")
        back_btn.setStyleSheet("color: #8B929E; font-size: 12px; background: transparent; border: none;")
        back_btn.clicked.connect(self.go_back.emit)

        sep = QLabel("/")
        sep.setStyleSheet("color: #464D58; margin: 0 6px;")

        self._breadcrumb = QLabel("Loading...")
        self._breadcrumb.setStyleSheet("color: #C9CDD4; font-size: 13px; font-weight: 500;")

        h_layout.addWidget(back_btn)
        h_layout.addWidget(sep)
        h_layout.addWidget(self._breadcrumb)
        h_layout.addStretch()

        if self.services.can_upload_recordings():
            upload_btn = QPushButton("↑ Upload Recording")
            upload_btn.setObjectName("btn_primary")
            upload_btn.setFixedHeight(28)
            upload_btn.clicked.connect(
                lambda: self.open_upload_recording.emit(self.lead_id)
            )
            h_layout.addWidget(upload_btn)

        layout.addWidget(self._header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left: tabs
        tabs_container = QWidget()
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        # Overview tab
        self._overview_tab = self._build_overview_tab()
        self._tabs.addTab(self._overview_tab, "Overview")

        # Calls tab
        self._calls_tab = self._build_calls_tab()
        self._tabs.addTab(self._calls_tab, "Calls")

        # AI Analysis tab
        self._ai_tab = self._build_ai_tab()
        self._tabs.addTab(self._ai_tab, "AI Analysis")

        # Follow-ups tab
        self._followups_tab = self._build_followups_tab()
        self._tabs.addTab(self._followups_tab, "Follow-ups")

        tabs_layout.addWidget(self._tabs)
        splitter.addWidget(tabs_container)

        # Right: properties panel
        self._props_panel = self._build_properties_panel()
        self._props_panel.setFixedWidth(240)
        splitter.addWidget(self._props_panel)

        splitter.setSizes([700, 240])
        layout.addWidget(splitter, 1)

    def _build_overview_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # Lead header
        self._lead_name_label = QLabel("—")
        self._lead_name_label.setStyleSheet(
            "color: #E6E9ED; font-size: 20px; font-weight: 600;"
        )
        self._lead_company_label = QLabel("—")
        self._lead_company_label.setStyleSheet("color: #8B929E; font-size: 13px;")

        layout.addWidget(self._lead_name_label)
        layout.addWidget(self._lead_company_label)

        # Contact info
        contact_panel = Panel("Contact Information")
        self._frow_phone = FieldRow("Phone", "—")
        self._frow_email = FieldRow("Email", "—")
        self._frow_location = FieldRow("Location", "—")
        self._frow_source = FieldRow("Source", "—")
        self._frow_campaign = FieldRow("Campaign", "—")

        for w in [self._frow_phone, self._frow_email, self._frow_location,
                  self._frow_source, self._frow_campaign]:
            contact_panel.add_widget(w)
        layout.addWidget(contact_panel)

        # AI Summary panel (shows if available)
        self._ai_summary_panel = Panel("AI Summary")
        self._ai_summary_text = QLabel("No AI analysis available yet.")
        self._ai_summary_text.setWordWrap(True)
        self._ai_summary_text.setStyleSheet("color: #9EA5B0; font-size: 12px; line-height: 1.5;")
        self._ai_summary_panel.add_widget(self._ai_summary_text)
        layout.addWidget(self._ai_summary_panel)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _build_calls_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self._calls_table = DataTable(["Date", "Duration", "Status", "Transcript"])
        self._calls_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self._calls_table.doubleClicked.connect(self._on_call_click)
        layout.addWidget(self._calls_table)
        return container

    def _build_ai_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # Latest analysis
        self._ai_panel = Panel("Latest AI Analysis")
        self._ai_intent_row = FieldRow("Intent", "—")
        self._ai_sentiment_row = FieldRow("Sentiment", "—")
        self._ai_score_row = FieldRow("Lead Score", "—")
        self._ai_priority_row = FieldRow("Priority", "—")
        self._ai_timeline_row = FieldRow("Purchase Timeline", "—")
        self._ai_followup_row = FieldRow("Follow-up Required", "—")
        self._ai_action_row = FieldRow("Recommended Action", "—")
        self._ai_confidence_row = FieldRow("AI Confidence", "—")

        for w in [
            self._ai_intent_row, self._ai_sentiment_row,
            self._ai_score_row, self._ai_priority_row,
            self._ai_timeline_row, self._ai_followup_row,
            self._ai_action_row, self._ai_confidence_row,
        ]:
            self._ai_panel.add_widget(w)
        layout.addWidget(self._ai_panel)

        # Requirements panel
        self._req_panel = Panel("Customer Requirements")
        self._req_label = QLabel("—")
        self._req_label.setWordWrap(True)
        self._req_label.setStyleSheet("color: #9EA5B0; font-size: 12px;")
        self._req_panel.add_widget(self._req_label)
        layout.addWidget(self._req_panel)

        # Objections panel
        self._obj_panel = Panel("Objections Raised")
        self._obj_label = QLabel("—")
        self._obj_label.setWordWrap(True)
        self._obj_label.setStyleSheet("color: #9EA5B0; font-size: 12px;")
        self._obj_panel.add_widget(self._obj_label)
        layout.addWidget(self._obj_panel)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _build_followups_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self._followups_table = DataTable(["Due Date", "Reason", "Priority", "Status"])
        layout.addWidget(self._followups_table)
        return container

    def _build_properties_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: #14171C; border-left: 1px solid #1E2329;")

        container = QWidget()
        container.setStyleSheet("background-color: #14171C;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        def _prop_section(title: str) -> QLabel:
            lbl = QLabel(title.upper())
            lbl.setStyleSheet("color: #626975; font-size: 10px; font-weight: 600; letter-spacing: 0.8px;")
            return lbl

        def _prop_value() -> QLabel:
            lbl = QLabel("—")
            lbl.setStyleSheet("color: #C9CDD4; font-size: 13px; font-weight: 500;")
            lbl.setWordWrap(True)
            return lbl

        layout.addWidget(_prop_section("Status"))
        self._prop_status = _prop_value()
        layout.addWidget(self._prop_status)

        layout.addWidget(_prop_section("Lead Score"))
        self._prop_score = _prop_value()
        layout.addWidget(self._prop_score)

        layout.addWidget(_prop_section("Priority"))
        self._prop_priority = _prop_value()
        layout.addWidget(self._prop_priority)

        layout.addWidget(_prop_section("Assigned To"))
        self._prop_assigned = _prop_value()
        layout.addWidget(self._prop_assigned)

        layout.addWidget(_prop_section("Intent"))
        self._prop_intent = _prop_value()
        layout.addWidget(self._prop_intent)

        layout.addWidget(_prop_section("Sentiment"))
        self._prop_sentiment = _prop_value()
        layout.addWidget(self._prop_sentiment)

        layout.addWidget(_prop_section("Last Contact"))
        self._prop_last_contact = _prop_value()
        layout.addWidget(self._prop_last_contact)

        layout.addWidget(_prop_section("Next Follow-up"))
        self._prop_next_followup = _prop_value()
        layout.addWidget(self._prop_next_followup)

        layout.addWidget(_prop_section("Created"))
        self._prop_created = _prop_value()
        layout.addWidget(self._prop_created)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _load(self):
        lead = self.services.lead_repo.find_by_id(self.lead_id)
        if not lead:
            self._breadcrumb.setText("Lead Not Found")
            return

        self._lead = lead
        self._populate(lead)

    def _populate(self, lead: LeadDB):
        self._breadcrumb.setText(lead.name)
        self._lead_name_label.setText(lead.name)
        self._lead_company_label.setText(lead.company or "—")

        # Contact
        self._frow_phone.set_value(lead.phone or "—")
        self._frow_email.set_value(lead.email or "—")
        self._frow_location.set_value(lead.location or "—")
        self._frow_source.set_value(lead.source.value.replace("_", " ").title())
        self._frow_campaign.set_value(lead.campaign or "—")

        # AI Summary
        if lead.ai_summary:
            self._ai_summary_text.setText(lead.ai_summary)
        else:
            self._ai_summary_text.setText("No AI analysis has been performed for this lead yet.")

        # Properties panel
        from app.desktop.styles import get_status_color, get_priority_color, get_sentiment_color, score_to_color
        status = lead.status.value
        self._prop_status.setText(status.upper().replace("_", " "))
        self._prop_status.setStyleSheet(f"color: {get_status_color(status)}; font-size: 13px; font-weight: 600;")

        score = lead.lead_score
        self._prop_score.setText(f"{score} / 100")
        self._prop_score.setStyleSheet(f"color: {score_to_color(score)}; font-size: 13px; font-weight: 600;")

        priority = lead.priority.value
        self._prop_priority.setText(priority.upper())
        self._prop_priority.setStyleSheet(f"color: {get_priority_color(priority)}; font-size: 13px; font-weight: 600;")

        self._prop_assigned.setText(lead.assigned_to_name or "Unassigned")
        self._prop_intent.setText(lead.intent or "—")
        self._prop_sentiment.setText(lead.sentiment or "—")

        if lead.sentiment:
            self._prop_sentiment.setStyleSheet(
                f"color: {get_sentiment_color(lead.sentiment)}; font-size: 13px; font-weight: 500;"
            )

        self._prop_last_contact.setText(
            lead.last_contact.strftime("%b %d, %Y") if lead.last_contact else "—"
        )
        self._prop_next_followup.setText(
            lead.next_followup.strftime("%b %d, %Y") if lead.next_followup else "—"
        )
        self._prop_created.setText(
            lead.created_at.strftime("%b %d, %Y") if lead.created_at else "—"
        )

        # Load calls
        self._load_calls(lead)

        # Load follow-ups
        self._load_followups(lead)

        # Load latest analysis
        self._load_ai_analysis(lead)

    def _load_calls(self, lead: LeadDB):
        calls = self.services.call_repo.list_records_for_lead(lead.id)  # type: ignore
        self._calls_table.setSortingEnabled(False)
        self._calls_table.setRowCount(0)

        for call in calls:
            row = self._calls_table.rowCount()
            self._calls_table.insertRow(row)

            date = call.created_at.strftime("%b %d, %Y %H:%M") if call.created_at else "—"
            duration = f"{int(call.duration_seconds or 0)}s" if call.duration_seconds else "—"
            status = call.analysis_status.value.title()
            transcript_preview = (call.transcript or "")[:60] + "..." if call.transcript else "—"

            for col, val in enumerate([date, duration, status, transcript_preview]):
                item = QTableWidgetItem(val)
                item.setForeground(QColor("#C9CDD4"))
                item.setData(Qt.ItemDataRole.UserRole, call.id)
                self._calls_table.setItem(row, col, item)

        self._calls_table.setSortingEnabled(True)

    def _load_ai_analysis(self, lead: LeadDB):
        calls = self.services.call_repo.list_records_for_lead(lead.id)  # type: ignore
        latest_analysis = None

        for call in calls:
            if call.analysis_status.value == "completed":
                analysis = self.services.call_repo.find_analysis_by_call(call.id)  # type: ignore
                if analysis:
                    latest_analysis = analysis
                    break

        if not latest_analysis:
            return

        a = latest_analysis.analysis
        self._ai_intent_row.set_value(a.intent.value)
        self._ai_sentiment_row.set_value(a.sentiment.value)
        self._ai_score_row.set_value(f"{a.lead_score} / 100")
        self._ai_priority_row.set_value(a.priority.value.upper())
        self._ai_timeline_row.set_value(a.purchase_timeline or "Not specified")
        self._ai_followup_row.set_value("Yes" if a.follow_up_required else "No")
        self._ai_action_row.set_value(a.recommended_action)
        self._ai_confidence_row.set_value(f"{a.confidence:.0%}")

        if a.requirements:
            self._req_label.setText("\n".join(f"• {r}" for r in a.requirements))
        else:
            self._req_label.setText("No requirements explicitly stated.")

        if a.objections:
            self._obj_label.setText("\n".join(f"• {o}" for o in a.objections))
        else:
            self._obj_label.setText("No objections raised.")

    def _load_followups(self, lead: LeadDB):
        followups = self.services.followup_repo.list_for_lead(lead.id)  # type: ignore
        self._followups_table.setSortingEnabled(False)
        self._followups_table.setRowCount(0)

        for fu in followups:
            row = self._followups_table.rowCount()
            self._followups_table.insertRow(row)
            due = fu.due_date.strftime("%b %d, %Y") if fu.due_date else "—"

            for col, val in enumerate([due, fu.reason, fu.priority.value.upper(), fu.status.value.upper()]):
                item = QTableWidgetItem(val)
                item.setForeground(QColor("#C9CDD4"))
                self._followups_table.setItem(row, col, item)

        self._followups_table.setSortingEnabled(True)

    def _on_call_click(self, index):
        item = self._calls_table.item(index.row(), 0)
        if item:
            call_id = item.data(Qt.ItemDataRole.UserRole)
            if call_id:
                self.open_call_analysis.emit(call_id)
