"""
LeadFlow — Dashboard Page
Role-aware CRM intelligence dashboard.
"""

from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtCore import Qt, QThread, QObject, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSizePolicy, QTableWidgetItem, QFrame
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import (
    KPICard, Panel, DataTable, StatusBadge,
    PriorityBadge, SentimentBadge, ScoreWidget,
    EmptyState, SectionHeader,
)
from app.backend.models.domain import UserRole

logger = logging.getLogger(__name__)


class DashboardWorker(QObject):
    """Load dashboard data off the UI thread."""
    data_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, services: AppServices):
        super().__init__()
        self.services = services

    def run(self):
        try:
            lead_repo = self.services.lead_repo
            call_repo = self.services.call_repo
            followup_repo = self.services.followup_repo

            total_leads = lead_repo.count_total()
            high_priority = lead_repo.count_high_priority()
            avg_score = lead_repo.average_score()
            pending_followups = followup_repo.count_pending()
            overdue_followups = followup_repo.count_overdue()

            # Auto-mark overdue
            followup_repo.auto_mark_overdue()

            high_leads = lead_repo.get_high_priority_leads(8)
            recent_analyses = call_repo.list_recent_analyses(6)
            sentiment_dist = call_repo.sentiment_distribution()
            status_dist = lead_repo.count_by_status()

            self.data_ready.emit({
                "total_leads": total_leads,
                "high_priority": high_priority,
                "avg_score": avg_score,
                "pending_followups": pending_followups,
                "overdue_followups": overdue_followups,
                "high_leads": high_leads,
                "recent_analyses": recent_analyses,
                "sentiment_dist": sentiment_dist,
                "status_dist": status_dist,
            })
        except Exception as e:
            self.error.emit(str(e))


class DashboardPage(QWidget):
    """Main CRM dashboard with KPIs, lead table, and recent conversations."""

    open_lead = Signal(str)  # lead_id
    open_call = Signal(str)  # call_id

    def __init__(self, services: AppServices, parent=None):
        super().__init__(parent)
        self.services = services
        self._thread = None
        self._worker = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Page header
        header = QWidget()
        header.setObjectName("page_header")
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Dashboard")
        title.setObjectName("page_title")
        subtitle = QLabel("Sales intelligence overview")
        subtitle.setObjectName("page_subtitle")
        subtitle.setStyleSheet("color: #626975; font-size: 12px; margin-left: 12px; margin-top: 3px;")

        refresh_btn = self._make_toolbar_btn("↻ Refresh")
        refresh_btn.clicked.connect(self.refresh)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        main_layout.addWidget(header)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(20, 16, 20, 20)
        self._content_layout.setSpacing(16)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self._build_content()

    def _make_toolbar_btn(self, text: str) -> "QPushButton":
        from PySide6.QtWidgets import QPushButton
        btn = QPushButton(text)
        btn.setFixedHeight(28)
        return btn

    def _build_content(self):
        # ── KPI Row ──────────────────────────────────────────
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        self._kpi_leads = KPICard("Total Leads", "—")
        self._kpi_priority = KPICard("High Priority", "—")
        self._kpi_score = KPICard("Avg Lead Score", "—")
        self._kpi_followups = KPICard("Pending Follow-ups", "—")
        self._kpi_overdue = KPICard("Overdue", "—")

        for card in [
            self._kpi_leads, self._kpi_priority,
            self._kpi_score, self._kpi_followups, self._kpi_overdue
        ]:
            kpi_layout.addWidget(card)

        self._content_layout.addLayout(kpi_layout)

        # ── Middle Row ───────────────────────────────────────
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(12)

        # Pipeline distribution panel
        self._pipeline_panel = Panel("Lead Pipeline")
        self._pipeline_rows = {}
        statuses = ["new", "contacted", "interested", "follow_up", "negotiation", "converted", "lost"]
        for s in statuses:
            row = self._make_pipeline_row(s, 0)
            self._pipeline_rows[s] = row
            self._pipeline_panel.add_widget(row)
        mid_layout.addWidget(self._pipeline_panel, 1)

        # Sentiment panel
        self._sentiment_panel = Panel("Conversation Sentiment")
        self._sentiment_rows = {}
        for s in ["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"]:
            row = self._make_sentiment_row(s, 0)
            self._sentiment_rows[s] = row
            self._sentiment_panel.add_widget(row)
        mid_layout.addWidget(self._sentiment_panel, 1)

        self._content_layout.addLayout(mid_layout)

        # ── High Priority Leads ──────────────────────────────
        leads_panel = Panel("High-Priority Leads")
        self._leads_table = DataTable([
            "Lead", "Company", "Score", "Intent", "Sentiment", "Status", "Priority"
        ])
        self._leads_table.setFixedHeight(220)
        self._leads_table.doubleClicked.connect(self._on_lead_double_click)
        leads_panel.add_widget(self._leads_table)
        self._content_layout.addWidget(leads_panel)

        # ── Recent Conversations ──────────────────────────────
        conv_panel = Panel("Recent Conversations")
        self._conv_table = DataTable([
            "Lead", "Summary", "Intent", "Sentiment", "Score", "Date"
        ])
        self._conv_table.setFixedHeight(200)
        conv_panel.add_widget(self._conv_table)
        self._content_layout.addWidget(conv_panel)

        self._content_layout.addStretch()

    def _make_pipeline_row(self, status: str, count: int) -> QWidget:
        from app.desktop.styles import get_status_color
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(8)

        label = QLabel(status.upper().replace("_", " "))
        label.setFixedWidth(100)
        label.setStyleSheet(f"color: {get_status_color(status)}; font-size: 11px; font-weight: 600;")

        count_label = QLabel(str(count))
        count_label.setStyleSheet("color: #8B929E; font-size: 12px;")
        count_label.setFixedWidth(40)
        count_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(label)
        layout.addWidget(count_label)
        w._count_label = count_label
        w._status = status
        return w

    def _make_sentiment_row(self, sentiment: str, count: int) -> QWidget:
        from app.desktop.styles import get_sentiment_color
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(8)

        label = QLabel(sentiment)
        label.setFixedWidth(80)
        label.setStyleSheet(f"color: {get_sentiment_color(sentiment)}; font-size: 11px; font-weight: 600;")

        count_label = QLabel(str(count))
        count_label.setStyleSheet("color: #8B929E; font-size: 12px;")
        count_label.setFixedWidth(40)
        count_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(label)
        layout.addWidget(count_label)
        w._count_label = count_label
        return w

    def refresh(self):
        """Reload dashboard data in background thread."""
        if self._thread and self._thread.isRunning():
            return

        self._thread = QThread()
        self._worker = DashboardWorker(self.services)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.data_ready.connect(self._on_data_ready)
        self._worker.error.connect(self._on_error)
        self._worker.data_ready.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_data_ready(self, data: dict):
        # KPIs
        self._kpi_leads.set_value(f"{data['total_leads']:,}")
        self._kpi_priority.set_value(f"{data['high_priority']:,}")
        self._kpi_score.set_value(f"{data['avg_score']:.1f}")
        self._kpi_followups.set_value(f"{data['pending_followups']:,}")
        self._kpi_overdue.set_value(f"{data['overdue_followups']:,}")

        # Pipeline
        status_dist = data.get("status_dist", {})
        for status, row_widget in self._pipeline_rows.items():
            count = status_dist.get(status, 0)
            row_widget._count_label.setText(str(count))

        # Sentiment
        sent_dist = data.get("sentiment_dist", {})
        for sent, row_widget in self._sentiment_rows.items():
            count = sent_dist.get(sent, 0)
            row_widget._count_label.setText(str(count))

        # High priority leads table
        self._leads_table.clear_rows()
        self._leads_table.setSortingEnabled(False)
        for lead in data.get("high_leads", []):
            score_widget = ScoreWidget(lead.lead_score)
            status_badge = StatusBadge(lead.status.value)
            priority_badge = PriorityBadge(lead.priority.value)
            sentiment_badge = SentimentBadge(lead.sentiment) if lead.sentiment else QLabel("—")

            row = self._leads_table.rowCount()
            self._leads_table.insertRow(row)
            self._leads_table.setItem(row, 0, self._item(lead.name))
            self._leads_table.setItem(row, 1, self._item(lead.company or "—"))
            self._leads_table.setCellWidget(row, 2, score_widget)
            self._leads_table.setItem(row, 3, self._item(lead.intent or "—"))
            self._leads_table.setCellWidget(row, 4, sentiment_badge)
            self._leads_table.setCellWidget(row, 5, status_badge)
            self._leads_table.setCellWidget(row, 6, priority_badge)
            # Store lead id
            self._leads_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, lead.id)

        self._leads_table.setSortingEnabled(True)

        # Recent conversations
        self._conv_table.clear_rows()
        self._conv_table.setSortingEnabled(False)
        for analysis in data.get("recent_analyses", []):
            a = analysis.analysis
            date_str = analysis.created_at.strftime("%b %d, %H:%M") if analysis.created_at else "—"

            self._conv_table.insertRow(self._conv_table.rowCount())
            row = self._conv_table.rowCount() - 1
            # Get lead name
            lead = self.services.lead_repo.find_by_id(analysis.lead_id)
            lead_name = lead.name if lead else "Unknown"

            summary = a.summary[:80] + "..." if len(a.summary) > 80 else a.summary

            self._conv_table.setItem(row, 0, self._item(lead_name))
            self._conv_table.setItem(row, 1, self._item(summary))
            self._conv_table.setItem(row, 2, self._item(a.intent.value))
            self._conv_table.setCellWidget(row, 3, SentimentBadge(a.sentiment.value))
            self._conv_table.setItem(row, 4, self._item(str(a.lead_score)))
            self._conv_table.setItem(row, 5, self._item(date_str))
        self._conv_table.setSortingEnabled(True)

    def _item(self, text: str) -> QTableWidgetItem:
        from PySide6.QtGui import QColor
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor("#C9CDD4"))
        return item

    def _on_error(self, msg: str):
        logger.error(f"Dashboard error: {msg}")

    def _on_lead_double_click(self, index):
        item = self._leads_table.item(index.row(), 0)
        if item:
            lead_id = item.data(Qt.ItemDataRole.UserRole)
            if lead_id:
                self.open_lead.emit(lead_id)
