"""
LeadFlow — Analytics Page
Agentic pipeline + charts + AI insights + query interface.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QTextEdit,
    QLineEdit, QSplitter, QSizePolicy, QTabWidget,
    QTableWidgetItem,
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import (
    KPICard, Panel, DataTable, SentimentBadge,
    EmptyState, FieldRow, SectionHeader,
)
from app.analytics_engine.orchestrator import AnalyticsReport, AgentResult

logger = logging.getLogger(__name__)


class AnalyticsWorker(QObject):
    progress = Signal(str, str)      # agent_name, message
    done = Signal(object)            # AnalyticsReport
    error = Signal(str)

    def __init__(self, services: AppServices):
        super().__init__()
        self.services = services

    def run(self):
        try:
            orchestrator = self.services.get_analytics_orchestrator()

            def cb(agent: str, msg: str):
                self.progress.emit(agent, msg)

            report = orchestrator.run_full_pipeline(callback=cb)
            self.done.emit(report)
        except Exception as e:
            self.error.emit(str(e))


class QueryWorker(QObject):
    done = Signal(str)
    error = Signal(str)

    def __init__(self, services: AppServices, question: str):
        super().__init__()
        self.services = services
        self.question = question

    def run(self):
        try:
            orchestrator = self.services.get_analytics_orchestrator()
            answer = orchestrator.answer_query(self.question)
            self.done.emit(answer)
        except Exception as e:
            self.error.emit(str(e))


class AnalyticsPage(QWidget):
    """Full agentic analytics dashboard."""

    def __init__(self, services: AppServices, parent=None):
        super().__init__(parent)
        self.services = services
        self._report: Optional[AnalyticsReport] = None
        self._thread: Optional[QThread] = None
        self._worker = None
        self._setup_ui()

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

        title = QLabel("Sales Intelligence")
        title.setObjectName("page_title")
        subtitle = QLabel("AI-powered analysis of your sales pipeline")
        subtitle.setStyleSheet("color: #626975; font-size: 12px; margin-left: 12px; margin-top: 3px;")

        run_btn = QPushButton("▶ Run Analysis")
        run_btn.setObjectName("btn_primary")
        run_btn.setFixedHeight(28)
        run_btn.clicked.connect(self._run_analysis)

        h_layout.addWidget(title)
        h_layout.addWidget(subtitle)
        h_layout.addStretch()
        h_layout.addWidget(run_btn)
        layout.addWidget(header)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        # Overview tab
        overview = self._build_overview_tab()
        self._tabs.addTab(overview, "Overview")

        # Agent Pipeline tab
        agents = self._build_agents_tab()
        self._tabs.addTab(agents, "AI Pipeline")

        # Insights tab
        insights = self._build_insights_tab()
        self._tabs.addTab(insights, "Insights")

        # Ask LeadFlow tab
        query = self._build_query_tab()
        self._tabs.addTab(query, "Ask LeadFlow")

        layout.addWidget(self._tabs, 1)

    def _build_overview_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # KPI row
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)
        self._kpi_total = KPICard("Total Leads", "—")
        self._kpi_high = KPICard("High Priority", "—")
        self._kpi_score = KPICard("Avg Score", "—")
        self._kpi_conversion = KPICard("Conversion Rate", "—")
        self._kpi_calls = KPICard("Calls Analyzed", "—")
        for c in [self._kpi_total, self._kpi_high, self._kpi_score,
                  self._kpi_conversion, self._kpi_calls]:
            kpi_layout.addWidget(c)
        layout.addLayout(kpi_layout)

        # Mid row
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(12)

        # Status distribution
        self._status_panel = Panel("Lead Pipeline Status")
        self._status_rows: dict = {}
        for s in ["new", "contacted", "interested", "follow_up", "negotiation", "converted", "lost"]:
            row = self._make_dist_row(s.upper().replace("_", " "), 0)
            self._status_rows[s] = row
            self._status_panel.add_widget(row)
        mid_layout.addWidget(self._status_panel, 1)

        # Sentiment dist
        self._sent_panel = Panel("Conversation Sentiment")
        self._sent_rows: dict = {}
        colors = {"POSITIVE": "#2ECC71", "NEUTRAL": "#8B929E", "NEGATIVE": "#E05252", "MIXED": "#9B7FE8"}
        for s, color in colors.items():
            row = self._make_dist_row(s, 0, color)
            self._sent_rows[s] = row
            self._sent_panel.add_widget(row)
        mid_layout.addWidget(self._sent_panel, 1)

        # Score buckets
        self._score_panel = Panel("Lead Score Distribution")
        self._score_rows: dict = {}
        score_cfg = [("HIGH (70-100)", "high", "#2ECC71"), ("MEDIUM (40-69)", "medium", "#E8A845"), ("LOW (0-39)", "low", "#E05252")]
        for label, key, color in score_cfg:
            row = self._make_dist_row(label, 0, color)
            self._score_rows[key] = row
            self._score_panel.add_widget(row)
        mid_layout.addWidget(self._score_panel, 1)

        layout.addLayout(mid_layout)

        # Executive performance table
        exec_panel = Panel("Executive Performance")
        self._exec_table = DataTable(["Executive", "Leads", "Avg Score", "Converted"])
        self._exec_table.setFixedHeight(180)
        exec_panel.add_widget(self._exec_table)
        layout.addWidget(exec_panel)

        # Common objections
        obj_panel = Panel("Common Objections")
        self._obj_list_label = QLabel("Run analysis to see common objections.")
        self._obj_list_label.setWordWrap(True)
        self._obj_list_label.setStyleSheet("color: #9EA5B0; font-size: 12px;")
        obj_panel.add_widget(self._obj_list_label)
        layout.addWidget(obj_panel)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _make_dist_row(self, label: str, count: int, color: str = "#8B929E") -> QWidget:
        w = QWidget()
        row_layout = QHBoxLayout(w)
        row_layout.setContentsMargins(0, 3, 0, 3)
        row_layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setFixedWidth(120)
        lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")

        cnt = QLabel(str(count))
        cnt.setStyleSheet("color: #8B929E; font-size: 12px;")
        cnt.setFixedWidth(40)
        cnt.setAlignment(Qt.AlignmentFlag.AlignRight)

        row_layout.addWidget(lbl)
        row_layout.addWidget(cnt)
        w._cnt_label = cnt
        return w

    def _build_agents_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # Status
        self._pipeline_status = QLabel("Click 'Run Analysis' to execute the agentic pipeline.")
        self._pipeline_status.setStyleSheet("color: #626975; font-size: 12px;")
        layout.addWidget(self._pipeline_status)

        # Agent cards
        self._agent_cards: list[QWidget] = []
        for name in ["Analytics Agent", "Insight Agent", "Action Agent"]:
            card = self._make_agent_card(name)
            layout.addWidget(card)
            self._agent_cards.append(card)

        # Total time
        self._time_label = QLabel("")
        self._time_label.setStyleSheet("color: #626975; font-size: 11px;")
        layout.addWidget(self._time_label)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _make_agent_card(self, name: str) -> QWidget:
        card = QWidget()
        card.setObjectName("agent_card")
        card.setStyleSheet("""
            QWidget#agent_card {
                background-color: #191D24;
                border: 1px solid #1E2329;
                border-radius: 8px;
                padding: 0;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        name_row = QHBoxLayout()
        icon_lbl = QLabel("○")
        icon_lbl.setStyleSheet("color: #464D58; font-size: 14px;")
        icon_lbl.setFixedWidth(20)

        name_lbl = QLabel(name)
        name_lbl.setObjectName("agent_name")

        name_row.addWidget(icon_lbl)
        name_row.addWidget(name_lbl)
        name_row.addStretch()

        detail_lbl = QLabel("Waiting to run...")
        detail_lbl.setObjectName("agent_detail")

        layout.addLayout(name_row)
        layout.addWidget(detail_lbl)

        card._icon = icon_lbl
        card._name = name_lbl
        card._detail = detail_lbl
        return card

    def _build_insights_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # Insights
        insights_panel = Panel("AI Insights")
        self._insights_text = QTextEdit()
        self._insights_text.setReadOnly(True)
        self._insights_text.setObjectName("query_response")
        self._insights_text.setFixedHeight(220)
        self._insights_text.setPlaceholderText("Run the analysis pipeline to generate insights...")
        insights_panel.add_widget(self._insights_text)
        layout.addWidget(insights_panel)

        # Recommendations
        recs_panel = Panel("Recommendations")
        self._recs_text = QTextEdit()
        self._recs_text.setReadOnly(True)
        self._recs_text.setObjectName("query_response")
        self._recs_text.setFixedHeight(220)
        self._recs_text.setPlaceholderText("Recommendations will appear after running the analysis...")
        recs_panel.add_widget(self._recs_text)
        layout.addWidget(recs_panel)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _build_query_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        # Query header
        title = QLabel("Ask LeadFlow")
        title.setObjectName("section_title")
        desc = QLabel("Ask questions about your sales pipeline. Answers are grounded in your actual CRM data.")
        desc.setStyleSheet("color: #626975; font-size: 12px;")
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(desc)

        # Example questions
        examples_layout = QHBoxLayout()
        examples_layout.setSpacing(8)
        example_qs = [
            "Why are high-value leads not converting?",
            "Which objections are most common?",
            "Which leads need manager attention?",
        ]
        for q in example_qs:
            btn = QPushButton(q)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1D2229;
                    color: #8B929E;
                    border: 1px solid #292E36;
                    border-radius: 6px;
                    padding: 5px 10px;
                    font-size: 11px;
                    text-align: left;
                }
                QPushButton:hover { color: #C9CDD4; background-color: #242A33; }
            """)
            btn.clicked.connect(lambda checked, question=q: self._quick_query(question))
            examples_layout.addWidget(btn)
        examples_layout.addStretch()
        layout.addLayout(examples_layout)

        # Query input
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self._query_input = QLineEdit()
        self._query_input.setObjectName("query_input")
        self._query_input.setPlaceholderText("Ask a question about your sales pipeline...")
        self._query_input.setFixedHeight(38)
        self._query_input.returnPressed.connect(self._submit_query)

        ask_btn = QPushButton("Ask")
        ask_btn.setObjectName("btn_primary")
        ask_btn.setFixedHeight(38)
        ask_btn.setFixedWidth(80)
        ask_btn.clicked.connect(self._submit_query)

        input_row.addWidget(self._query_input, 1)
        input_row.addWidget(ask_btn)
        layout.addLayout(input_row)

        # Response area
        self._query_response = QTextEdit()
        self._query_response.setReadOnly(True)
        self._query_response.setObjectName("query_response")
        self._query_response.setPlaceholderText("Your answer will appear here...")
        layout.addWidget(self._query_response, 1)

        return container

    def _run_analysis(self):
        if self._thread and self._thread.isRunning():
            return

        # Reset agent cards
        for card in self._agent_cards:
            card._icon.setText("○")
            card._icon.setStyleSheet("color: #464D58;")
            card._detail.setText("Waiting...")

        self._pipeline_status.setText("Running analysis pipeline...")

        try:
            self.services.get_gemini_service()
        except ValueError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "AI Configuration Error", str(e))
            return

        self._thread = QThread()
        self._worker = AnalyticsWorker(self.services)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_agent_progress)
        self._worker.done.connect(self._on_analysis_done)
        self._worker.error.connect(self._on_analysis_error)
        self._worker.done.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_agent_progress(self, agent: str, msg: str):
        agent_map = {
            "Analytics": 0,
            "Insight": 1,
            "Action": 2,
        }
        for key, idx in agent_map.items():
            if key.lower() in agent.lower() or key.lower() in msg.lower():
                if idx < len(self._agent_cards):
                    card = self._agent_cards[idx]
                    card._icon.setText("◉")
                    card._icon.setStyleSheet("color: #4A9EFF;")
                    card._detail.setText(msg)
                break

        self._pipeline_status.setText(msg)

    def _on_analysis_done(self, report: AnalyticsReport):
        self._report = report
        m = report.metrics

        # Update agent cards
        for i, result in enumerate(report.agent_results):
            if i < len(self._agent_cards):
                card = self._agent_cards[i]
                if result.status == "completed":
                    card._icon.setText("✓")
                    card._icon.setStyleSheet("color: #2ECC71;")
                    card._detail.setText(f"{result.summary}  ·  {result.duration_seconds:.1f}s")
                else:
                    card._icon.setText("✗")
                    card._icon.setStyleSheet("color: #E05252;")
                    card._detail.setText(result.error or "Failed")

        self._time_label.setText(
            f"Pipeline completed in {report.total_duration:.1f}s"
        )
        self._pipeline_status.setText("Analysis complete.")

        if not m:
            return

        # Update KPIs
        self._kpi_total.set_value(f"{m.total_leads:,}")
        self._kpi_high.set_value(f"{m.high_priority_count:,}")
        self._kpi_score.set_value(f"{m.avg_lead_score:.1f}")
        self._kpi_conversion.set_value(f"{m.conversion_rate:.1f}%")
        self._kpi_calls.set_value(f"{m.analyzed_calls:,}")

        # Status rows
        for s, row in self._status_rows.items():
            count = m.leads_by_status.get(s, 0)
            row._cnt_label.setText(str(count))

        # Sentiment rows
        for s, row in self._sent_rows.items():
            count = m.sentiment_distribution.get(s, 0)
            row._cnt_label.setText(str(count))

        # Score rows
        self._score_rows["high"]._cnt_label.setText(str(m.score_high))
        self._score_rows["medium"]._cnt_label.setText(str(m.score_medium))
        self._score_rows["low"]._cnt_label.setText(str(m.score_low))

        # Executive table
        self._exec_table.setRowCount(0)
        self._exec_table.setSortingEnabled(False)
        for exec_data in m.executive_performance:
            row = self._exec_table.rowCount()
            self._exec_table.insertRow(row)
            for col, val in enumerate([
                exec_data.get("name", "—"),
                str(exec_data.get("leads", 0)),
                f"{exec_data.get('avg_score', 0):.1f}",
                str(exec_data.get("converted", 0)),
            ]):
                item = QTableWidgetItem(val)
                item.setForeground(QColor("#C9CDD4"))
                self._exec_table.setItem(row, col, item)
        self._exec_table.setSortingEnabled(True)

        # Objections
        if m.common_objections:
            self._obj_list_label.setText(
                "\n".join(f"• {o}" for o in m.common_objections[:8])
            )
        else:
            self._obj_list_label.setText("No objections data available yet.")

        # Insights text
        if report.patterns:
            insights = []
            for p in report.patterns:
                insights.append(f"◆ {p.get('title', '')}")
                insights.append(f"  {p.get('observation', '')}")
                insights.append(f"  → {p.get('significance', '')}")
                insights.append("")
            self._insights_text.setPlainText("\n".join(insights))

        # Recommendations text
        if report.recommendations:
            recs = []
            for i, r in enumerate(report.recommendations, 1):
                priority = r.get("priority", "")
                action = r.get("action", "")
                reason = r.get("reason", "")
                impact = r.get("expected_impact", "")
                recs.append(f"{i}. [{priority}] {action}")
                recs.append(f"   Reason: {reason}")
                recs.append(f"   Impact: {impact}")
                recs.append("")
            self._recs_text.setPlainText("\n".join(recs))

    def _on_analysis_error(self, msg: str):
        self._pipeline_status.setText(f"Analysis failed: {msg}")
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(
            self, "Analysis Failed",
            f"Analytics pipeline encountered an error:\n\n{msg}"
        )

    def _quick_query(self, question: str):
        self._query_input.setText(question)
        self._submit_query()

    def _submit_query(self):
        question = self._query_input.text().strip()
        if not question:
            return

        self._query_response.setPlainText("Analyzing your question...")

        try:
            self.services.get_gemini_service()
        except ValueError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "AI Configuration Error", str(e))
            return

        self._q_thread = QThread()
        self._q_worker = QueryWorker(self.services, question)
        self._q_worker.moveToThread(self._q_thread)
        self._q_thread.started.connect(self._q_worker.run)
        self._q_worker.done.connect(self._on_query_done)
        self._q_worker.error.connect(self._on_query_error)
        self._q_worker.done.connect(self._q_thread.quit)
        self._q_worker.error.connect(self._q_thread.quit)
        self._q_thread.start()

    def _on_query_done(self, answer: str):
        self._query_response.setPlainText(answer)

    def _on_query_error(self, msg: str):
        self._query_response.setPlainText(
            f"Unable to answer query at this time.\n\nError: {msg}\n\n"
            "Ensure your Gemini API key is configured and MongoDB is connected."
        )
