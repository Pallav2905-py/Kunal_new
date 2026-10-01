"""
LeadFlow — Secondary Sidebar
Contextual explorer panel that changes content based on active section.
"""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame,
    QStackedWidget, QSizePolicy,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Base contextual panel
# ─────────────────────────────────────────────────────────

class _BasePanel(QWidget):
    navigate = Signal(str, dict)  # (page_id, context)

    def __init__(self, services, parent=None):
        super().__init__(parent)
        self._services = services

    def refresh(self) -> None:
        """Called when panel becomes visible."""


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("sidebar_section_header")
    return lbl


def _nav_btn(text: str, page_id: str, panel: _BasePanel, context: dict | None = None) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("sidebar_nav_btn")
    btn.setFixedHeight(28)
    ctx = context or {}
    btn.clicked.connect(lambda: panel.navigate.emit(page_id, ctx))
    return btn


def _stat_widget(num: str, label: str) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(12, 6, 12, 6)
    lay.setSpacing(1)
    n = QLabel(num)
    n.setObjectName("sidebar_stat_num")
    l = QLabel(label)
    l.setObjectName("sidebar_stat_label")
    lay.addWidget(n)
    lay.addWidget(l)
    return w


# ─────────────────────────────────────────────────────────
# Dashboard panel
# ─────────────────────────────────────────────────────────

class _DashboardPanel(_BasePanel):
    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Overview"))

        self._total_lbl = QLabel("—")
        self._total_lbl.setObjectName("sidebar_stat_num")
        self._hp_lbl = QLabel("—")
        self._hp_lbl.setObjectName("sidebar_stat_num")
        self._pf_lbl = QLabel("—")
        self._pf_lbl.setObjectName("sidebar_stat_num")

        stats_w = QWidget()
        stats_lay = QHBoxLayout(stats_w)
        stats_lay.setContentsMargins(8, 8, 8, 8)
        stats_lay.setSpacing(4)

        for num_lbl, label in [
            (self._total_lbl, "Total"),
            (self._hp_lbl, "High Pri"),
            (self._pf_lbl, "Follow-ups"),
        ]:
            card = QWidget()
            card.setStyleSheet("background:#161E2B; border:1px solid #1F2B3E; border-radius:3px;")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(8, 6, 8, 6)
            cl.setSpacing(1)
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub = QLabel(label)
            sub.setObjectName("sidebar_stat_label")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(num_lbl)
            cl.addWidget(sub)
            stats_lay.addWidget(card)

        lay.addWidget(stats_w)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #18202F;")
        lay.addWidget(sep)

        lay.addWidget(_section_label("Quick Access"))
        self._leads_btn = _nav_btn("  ◉  All Leads", "leads", self)
        self._hp_btn = _nav_btn("  ◈  High Priority Leads", "leads", self, {"priority": "high"})
        self._overdue_btn = _nav_btn("  ◇  Overdue Follow-ups", "followups", self, {"status": "overdue"})
        self._calls_btn = _nav_btn("  ◎  Call Analysis", "calls", self)
        for btn in [self._leads_btn, self._hp_btn, self._overdue_btn, self._calls_btn]:
            lay.addWidget(btn)

        lay.addStretch(1)

    def refresh(self) -> None:
        try:
            total = self._services.lead_repo.count_total()
            hp = self._services.lead_repo.count_high_priority()
            pf = self._services.followup_repo.count_pending()
            self._total_lbl.setText(str(total))
            self._hp_lbl.setText(str(hp))
            self._pf_lbl.setText(str(pf))
        except Exception:
            pass


# ─────────────────────────────────────────────────────────
# Leads panel
# ─────────────────────────────────────────────────────────

class _LeadsPanel(_BasePanel):
    filter_changed = Signal(str, str)  # status, priority

    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Filter by Status"))

        self._status_btns: dict[str, QPushButton] = {}
        statuses = [
            ("all",         "  All Leads"),
            ("new",         "  New"),
            ("contacted",   "  Contacted"),
            ("interested",  "  Interested"),
            ("follow_up",   "  Follow-up"),
            ("negotiation", "  Negotiation"),
            ("converted",   "  Converted"),
            ("lost",        "  Lost"),
        ]
        for key, label in statuses:
            btn = QPushButton(label)
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedHeight(26)
            btn.clicked.connect(lambda _, k=key: self._set_status(k))
            self._status_btns[key] = btn
            lay.addWidget(btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #18202F; margin: 4px 0;")
        lay.addWidget(sep)

        lay.addWidget(_section_label("Filter by Priority"))

        self._prio_btns: dict[str, QPushButton] = {}
        prios = [("all", "  All Priorities"), ("high", "  High"), ("medium", "  Medium"), ("low", "  Low")]
        for key, label in prios:
            btn = QPushButton(label)
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedHeight(26)
            btn.clicked.connect(lambda _, k=key: self._set_priority(k))
            self._prio_btns[key] = btn
            lay.addWidget(btn)

        lay.addStretch(1)

        self._cur_status = "all"
        self._cur_prio = "all"
        self._update_active()

    def _set_status(self, key: str) -> None:
        self._cur_status = key
        self._update_active()
        self.filter_changed.emit(
            "" if key == "all" else key,
            "" if self._cur_prio == "all" else self._cur_prio,
        )
        self.navigate.emit("leads", {"status": key, "priority": self._cur_prio})

    def _set_priority(self, key: str) -> None:
        self._cur_prio = key
        self._update_active()
        self.filter_changed.emit(
            "" if self._cur_status == "all" else self._cur_status,
            "" if key == "all" else key,
        )
        self.navigate.emit("leads", {"status": self._cur_status, "priority": key})

    def _update_active(self) -> None:
        for key, btn in self._status_btns.items():
            btn.setProperty("active", "true" if key == self._cur_status else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        for key, btn in self._prio_btns.items():
            btn.setProperty("active", "true" if key == self._cur_prio else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def reset_filters(self) -> None:
        self._cur_status = "all"
        self._cur_prio = "all"
        self._update_active()


# ─────────────────────────────────────────────────────────
# Calls panel
# ─────────────────────────────────────────────────────────

class _CallsPanel(_BasePanel):
    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Actions"))

        upload_btn = _nav_btn("  ↑  Upload Recording", "calls", self)
        lay.addWidget(upload_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #18202F; margin: 4px 0;")
        lay.addWidget(sep)

        lay.addWidget(_section_label("Recent Analyses"))

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch(1)
        scroll.setWidget(self._list_widget)
        lay.addWidget(scroll, 1)

    def refresh(self) -> None:
        try:
            analyses = self._services.call_repo.list_recent_analyses(8)
            # Clear
            while self._list_layout.count() > 1:
                item = self._list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            for rec in analyses:
                row = QPushButton(f"  {getattr(rec, 'lead_name', 'Unknown Lead')}")
                row.setObjectName("sidebar_nav_btn")
                row.setFixedHeight(26)
                row.clicked.connect(lambda _, rid=str(rec.id): self.navigate.emit("calls", {"call_id": rid}))
                self._list_layout.insertWidget(self._list_layout.count() - 1, row)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────
# Follow-ups panel
# ─────────────────────────────────────────────────────────

class _FollowupsPanel(_BasePanel):
    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Filter by Status"))

        self._status_btns: dict[str, QPushButton] = {}
        for key, label in [
            ("all",       "  All Follow-ups"),
            ("pending",   "  Pending"),
            ("overdue",   "  Overdue"),
            ("completed", "  Completed"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedHeight(26)
            btn.clicked.connect(lambda _, k=key: self._set_status(k))
            self._status_btns[key] = btn
            lay.addWidget(btn)

        lay.addStretch(1)
        self._cur = "all"
        self._update_active()

    def _set_status(self, key: str) -> None:
        self._cur = key
        self._update_active()
        self.navigate.emit("followups", {"status": key})

    def _update_active(self) -> None:
        for key, btn in self._status_btns.items():
            btn.setProperty("active", "true" if key == self._cur else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)


# ─────────────────────────────────────────────────────────
# Analytics panel
# ─────────────────────────────────────────────────────────

class _AnalyticsPanel(_BasePanel):
    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Run Analysis"))
        run_btn = _nav_btn("  ◈  Run Analytics", "analytics", self)
        lay.addWidget(run_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #18202F; margin: 4px 0;")
        lay.addWidget(sep)

        lay.addWidget(_section_label("Recent Reports"))
        self._reports_lay = QVBoxLayout()
        self._reports_lay.setContentsMargins(0, 0, 0, 0)
        self._reports_lay.setSpacing(0)
        lay.addLayout(self._reports_lay)

        lay.addStretch(1)

    def refresh(self) -> None:
        # Clear old buttons
        while self._reports_lay.count():
            item = self._reports_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        try:
            analyses = self._services.call_repo.list_recent_analyses(5)
            for rec in analyses:
                from datetime import datetime
                date_str = ""
                if hasattr(rec, "created_at") and rec.created_at:
                    date_str = f" ({rec.created_at.strftime('%b %d')})"
                lead_name = getattr(rec, "lead_name", "Unknown")
                btn = QPushButton(f"  {lead_name}{date_str}")
                btn.setObjectName("sidebar_nav_btn")
                btn.setFixedHeight(26)
                self._reports_lay.addWidget(btn)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────
# Users panel (admin only)
# ─────────────────────────────────────────────────────────

class _UsersPanel(_BasePanel):
    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Filter by Role"))
        for key, label in [
            ("all",            "  All Users"),
            ("admin",          "  Admin"),
            ("sales_manager",  "  Sales Manager"),
            ("sales_executive","  Sales Rep"),
            ("ai_analyst",     "  AI Analyst"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedHeight(26)
            lay.addWidget(btn)

        lay.addStretch(1)


# ─────────────────────────────────────────────────────────
# Settings panel
# ─────────────────────────────────────────────────────────

class _SettingsPanel(_BasePanel):
    def __init__(self, services, parent=None):
        super().__init__(services, parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_section_label("Configuration"))
        for label in ["  General", "  AI Settings", "  Database", "  About"]:
            btn = QPushButton(label)
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedHeight(26)
            lay.addWidget(btn)

        lay.addStretch(1)


# ─────────────────────────────────────────────────────────
# Main secondary sidebar container
# ─────────────────────────────────────────────────────────

SECTION_TO_TITLE = {
    "dashboard": "OVERVIEW",
    "leads":     "LEADS",
    "calls":     "CALLS",
    "followups": "FOLLOW-UPS",
    "analytics": "ANALYTICS",
    "users":     "USERS",
    "settings":  "SETTINGS",
}


class SecondarySidebar(QWidget):
    """
    Contextual sidebar with stacked per-section panels.
    Emits navigate(page_id, context) when a sidebar item is clicked.
    """

    navigate = Signal(str, dict)

    def __init__(self, services, parent=None):
        super().__init__(parent)
        self.setObjectName("secondary_sidebar")
        self.setMinimumWidth(180)
        self._services = services

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Section title header
        self._header = QLabel("OVERVIEW")
        self._header.setObjectName("sidebar_section_header")
        self._header.setFixedHeight(30)
        outer.addWidget(self._header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #18202F;")
        outer.addWidget(sep)

        # Stacked panels
        self._stack = QStackedWidget()
        outer.addWidget(self._stack, 1)

        # Create panels
        self._panels: dict[str, _BasePanel] = {}
        panel_classes = {
            "dashboard": _DashboardPanel,
            "leads":     _LeadsPanel,
            "calls":     _CallsPanel,
            "followups": _FollowupsPanel,
            "analytics": _AnalyticsPanel,
            "users":     _UsersPanel,
            "settings":  _SettingsPanel,
        }
        for section_id, cls in panel_classes.items():
            panel = cls(services)
            panel.navigate.connect(self.navigate)
            self._panels[section_id] = panel
            self._stack.addWidget(panel)

        self._cur_section = "dashboard"

    def show_section(self, section_id: str) -> None:
        """Switch to the panel for the given section."""
        panel = self._panels.get(section_id)
        if panel:
            self._stack.setCurrentWidget(panel)
            self._header.setText(SECTION_TO_TITLE.get(section_id, section_id.upper()))
            panel.refresh()
            self._cur_section = section_id

    @property
    def leads_panel(self) -> _LeadsPanel:
        return self._panels["leads"]  # type: ignore
