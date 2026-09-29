"""
LeadFlow — Follow-ups Page
"""

from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTableWidgetItem, QMessageBox,
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import DataTable, PriorityBadge, EmptyState
from app.backend.models.domain import FollowUpStatus

logger = logging.getLogger(__name__)


class FollowupsWorker(QObject):
    done = Signal(list, int)
    error = Signal(str)

    def __init__(self, services, status_filter, page):
        super().__init__()
        self.services = services
        self.status_filter = status_filter
        self.page = page

    def run(self):
        try:
            self.services.followup_repo.auto_mark_overdue()
            followups, total = self.services.followup_repo.list_all(
                status=self.status_filter or None,
                page=self.page,
            )
            self.done.emit(followups, total)
        except Exception as e:
            self.error.emit(str(e))


class FollowupsPage(QWidget):
    open_lead = Signal(str)

    def __init__(self, services: AppServices, parent=None):
        super().__init__(parent)
        self.services = services
        self._page = 1
        self._total = 0
        self._thread = None
        self._worker = None
        self._setup_ui()
        self._load()

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

        title = QLabel("Follow-ups")
        title.setObjectName("page_title")
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("color: #626975; font-size: 12px; margin-left: 12px; margin-top: 3px;")

        h_layout.addWidget(title)
        h_layout.addWidget(self._count_label)
        h_layout.addStretch()

        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setFixedHeight(28)
        refresh_btn.clicked.connect(self._load)
        h_layout.addWidget(refresh_btn)
        layout.addWidget(header)

        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(44)
        toolbar.setStyleSheet("background-color: #161A20; border-bottom: 1px solid #1E2329;")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(12, 0, 12, 0)
        tb.setSpacing(8)

        self._status_combo = QComboBox()
        self._status_combo.setFixedHeight(28)
        self._status_combo.addItems(["All Statuses", "pending", "overdue", "completed", "cancelled"])
        self._status_combo.currentTextChanged.connect(self._load)
        tb.addWidget(self._status_combo)
        tb.addStretch()
        layout.addWidget(toolbar)

        # Table
        self._table = DataTable([
            "Lead", "Reason", "Due Date", "Assigned To", "Priority", "Status"
        ])
        self._table.doubleClicked.connect(self._on_row_click)
        layout.addWidget(self._table, 1)

        # Pagination
        pag = QWidget()
        pag.setFixedHeight(36)
        pag.setStyleSheet("background-color: #14171C; border-top: 1px solid #1E2329;")
        pag_layout = QHBoxLayout(pag)
        pag_layout.setContentsMargins(12, 0, 12, 0)

        self._prev_btn = QPushButton("← Prev")
        self._prev_btn.setFixedHeight(24)
        self._prev_btn.clicked.connect(self._prev_page)

        self._page_label = QLabel("Page 1")
        self._page_label.setStyleSheet("color: #8B929E; font-size: 11px;")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._next_btn = QPushButton("Next →")
        self._next_btn.setFixedHeight(24)
        self._next_btn.clicked.connect(self._next_page)

        pag_layout.addWidget(self._prev_btn)
        pag_layout.addStretch()
        pag_layout.addWidget(self._page_label)
        pag_layout.addStretch()
        pag_layout.addWidget(self._next_btn)
        layout.addWidget(pag)

    def _load(self):
        if self._thread and self._thread.isRunning():
            return
        status = self._status_combo.currentText()
        if status.startswith("All"):
            status = ""

        self._thread = QThread()
        self._worker = FollowupsWorker(self.services, status, self._page)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.done.connect(self._on_loaded)
        self._worker.error.connect(lambda e: logger.error(e))
        self._worker.done.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_loaded(self, followups, total):
        self._total = total
        self._count_label.setText(f"{total:,} follow-ups")

        total_pages = max(1, (total + 49) // 50)
        self._page_label.setText(f"Page {self._page} of {total_pages}")
        self._prev_btn.setEnabled(self._page > 1)
        self._next_btn.setEnabled(self._page < total_pages)

        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)

        STATUS_COLORS = {
            "pending": "#4A9EFF",
            "overdue": "#E05252",
            "completed": "#2ECC71",
            "cancelled": "#626975",
        }

        for fu in followups:
            row = self._table.rowCount()
            self._table.insertRow(row)

            due_str = fu.due_date.strftime("%b %d, %Y") if fu.due_date else "—"
            status = fu.status.value
            color = STATUS_COLORS.get(status, "#8B929E")

            lead_item = QTableWidgetItem(fu.lead_name or "—")
            lead_item.setData(Qt.ItemDataRole.UserRole, fu.lead_id)
            lead_item.setForeground(QColor("#C9CDD4"))

            status_item = QTableWidgetItem(status.upper())
            status_item.setForeground(QColor(color))

            self._table.setItem(row, 0, lead_item)
            self._table.setItem(row, 1, self._item(fu.reason[:60]))
            self._table.setItem(row, 2, self._item(due_str))
            self._table.setItem(row, 3, self._item(fu.assigned_to_name or "—"))
            self._table.setCellWidget(row, 4, PriorityBadge(fu.priority.value))
            self._table.setItem(row, 5, status_item)

        self._table.setSortingEnabled(True)

    def _item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor("#C9CDD4"))
        return item

    def _on_row_click(self, index):
        item = self._table.item(index.row(), 0)
        if item:
            lead_id = item.data(Qt.ItemDataRole.UserRole)
            if lead_id:
                self.open_lead.emit(lead_id)

    def _prev_page(self):
        if self._page > 1:
            self._page -= 1
            self._load()

    def _next_page(self):
        total_pages = max(1, (self._total + 49) // 50)
        if self._page < total_pages:
            self._page += 1
            self._load()

    def refresh(self):
        self._page = 1
        self._load()
