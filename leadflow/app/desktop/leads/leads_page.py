"""
LeadFlow — Leads Page
Enterprise CRM lead management table with import, search, filter, pagination.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox,
    QDialog, QProgressBar, QFrame, QScrollArea,
    QSizePolicy,
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import (
    DataTable, StatusBadge, PriorityBadge, ScoreWidget,
    EmptyState, Toolbar, Panel
)
from app.backend.models.domain import UserRole

logger = logging.getLogger(__name__)

PAGE_SIZE = 50


class LeadLoadWorker(QObject):
    done = Signal(list, int)
    error = Signal(str)

    def __init__(self, services, page, search, status_filter, priority_filter):
        super().__init__()
        self.services = services
        self.page = page
        self.search = search
        self.status_filter = status_filter
        self.priority_filter = priority_filter

    def run(self):
        try:
            leads, total = self.services.lead_repo.list_all(
                page=self.page,
                page_size=PAGE_SIZE,
                status=self.status_filter or None,
                priority=self.priority_filter or None,
                search=self.search or None,
            )
            self.done.emit(leads, total)
        except Exception as e:
            self.error.emit(str(e))


class ImportWorker(QObject):
    progress = Signal(str)
    done = Signal(int)
    error = Signal(str)

    def __init__(self, services, valid_leads):
        super().__init__()
        self.services = services
        self.valid_leads = valid_leads

    def run(self):
        try:
            self.progress.emit("Importing leads...")
            count = self.services.import_service.import_leads(
                self.valid_leads,
                assigned_to=self.services.current_user_id,
                assigned_to_name=self.services.current_user_name,
            )
            self.done.emit(count)
        except Exception as e:
            self.error.emit(str(e))


class ImportPreviewDialog(QDialog):
    """Preview validation results before import."""

    confirmed = Signal(list)  # valid_leads

    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.result = result
        self.setWindowTitle("Import Preview")
        self.setFixedSize(540, 420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Import Preview")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #E6E9ED;")
        layout.addWidget(title)

        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        for label, value, color in [
            ("Total Records", str(self.result.total), "#C9CDD4"),
            ("Valid", str(self.result.valid), "#2ECC71"),
            ("Duplicates", str(self.result.duplicates), "#E8A845"),
            ("Invalid", str(self.result.invalid), "#E05252"),
        ]:
            card = QFrame()
            card.setStyleSheet("background-color: #1D2229; border: 1px solid #292E36; border-radius: 6px; padding: 8px;")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(2)
            val_label = QLabel(value)
            val_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
            lbl_label = QLabel(label)
            lbl_label.setStyleSheet("color: #626975; font-size: 10px; font-weight: 600;")
            card_layout.addWidget(val_label)
            card_layout.addWidget(lbl_label)
            stats_layout.addWidget(card)

        layout.addLayout(stats_layout)

        # Errors
        if self.result.errors:
            errors_label = QLabel("Issues Found:")
            errors_label.setStyleSheet("color: #8B929E; font-size: 12px; font-weight: 500;")
            layout.addWidget(errors_label)

            error_scroll = QScrollArea()
            error_scroll.setFixedHeight(120)
            error_scroll.setWidgetResizable(True)
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_layout.setSpacing(2)
            error_layout.setContentsMargins(8, 8, 8, 8)

            for err in self.result.errors[:10]:
                lbl = QLabel(err.get("error", "Unknown error"))
                lbl.setStyleSheet("color: #8B929E; font-size: 11px;")
                lbl.setWordWrap(True)
                error_layout.addWidget(lbl)

            if len(self.result.errors) > 10:
                more = QLabel(f"... and {len(self.result.errors) - 10} more issues")
                more.setStyleSheet("color: #626975; font-size: 11px;")
                error_layout.addWidget(more)

            error_layout.addStretch()
            error_scroll.setWidget(error_widget)
            layout.addWidget(error_scroll)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        import_btn = QPushButton(f"Import {self.result.valid} Leads")
        import_btn.setObjectName("btn_primary")
        import_btn.setEnabled(self.result.valid > 0)
        import_btn.clicked.connect(self._confirm)
        btn_layout.addWidget(import_btn)

        layout.addLayout(btn_layout)

    def _confirm(self):
        self.confirmed.emit(self.result.valid_leads)
        self.accept()


class LeadsPage(QWidget):
    """Enterprise CRM lead management table."""

    open_lead = Signal(str)  # lead_id

    def __init__(self, services: AppServices, parent=None):
        super().__init__(parent)
        self.services = services
        self._current_page = 1
        self._total_leads = 0
        self._thread = None
        self._worker = None
        self._setup_ui()
        self._load_leads()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Page header
        header = QWidget()
        header.setObjectName("page_header")
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Leads")
        title.setObjectName("page_title")
        self._count_label = QLabel("Loading...")
        self._count_label.setStyleSheet("color: #626975; font-size: 12px; margin-left: 12px; margin-top: 3px;")

        header_layout.addWidget(title)
        header_layout.addWidget(self._count_label)
        header_layout.addStretch()

        if self.services.can_import_leads():
            import_btn = QPushButton("↑ Import")
            import_btn.setObjectName("btn_primary")
            import_btn.setFixedHeight(28)
            import_btn.clicked.connect(self._import_leads)
            header_layout.addWidget(import_btn)

        layout.addWidget(header)

        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(44)
        toolbar.setStyleSheet("background-color: #161A20; border-bottom: 1px solid #1E2329;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 0, 12, 0)
        tb_layout.setSpacing(8)

        # Search
        self._search = QLineEdit()
        self._search.setObjectName("search_input")
        self._search.setPlaceholderText("Search leads, companies, phones...")
        self._search.setFixedWidth(280)
        self._search.setFixedHeight(28)
        self._search.returnPressed.connect(self._do_search)
        tb_layout.addWidget(self._search)

        # Status filter
        self._status_combo = QComboBox()
        self._status_combo.setFixedHeight(28)
        self._status_combo.addItems([
            "All Statuses", "new", "contacted", "interested",
            "follow_up", "negotiation", "converted", "lost"
        ])
        self._status_combo.currentTextChanged.connect(self._do_search)
        tb_layout.addWidget(self._status_combo)

        # Priority filter
        self._priority_combo = QComboBox()
        self._priority_combo.setFixedHeight(28)
        self._priority_combo.addItems(["All Priorities", "high", "medium", "low"])
        self._priority_combo.currentTextChanged.connect(self._do_search)
        tb_layout.addWidget(self._priority_combo)

        tb_layout.addStretch()

        # Refresh
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.clicked.connect(self._load_leads)
        tb_layout.addWidget(refresh_btn)

        layout.addWidget(toolbar)

        # Table
        self._table = DataTable([
            "Lead", "Company", "Phone", "Status", "Score",
            "Priority", "Assigned To", "Last Contact", "Next Follow-up"
        ])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.doubleClicked.connect(self._on_row_double_click)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._context_menu)
        layout.addWidget(self._table, 1)

        # Pagination
        pag_widget = QWidget()
        pag_widget.setFixedHeight(36)
        pag_widget.setStyleSheet("background-color: #14171C; border-top: 1px solid #1E2329;")
        pag_layout = QHBoxLayout(pag_widget)
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
        layout.addWidget(pag_widget)

    def _do_search(self):
        self._current_page = 1
        self._load_leads()

    def _load_leads(self):
        if self._thread and self._thread.isRunning():
            return

        search = self._search.text().strip()
        status = self._status_combo.currentText()
        priority = self._priority_combo.currentText()

        if status.startswith("All"):
            status = ""
        if priority.startswith("All"):
            priority = ""

        self._thread = QThread()
        self._worker = LeadLoadWorker(
            self.services, self._current_page, search, status, priority
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.done.connect(self._on_leads_loaded)
        self._worker.error.connect(lambda e: logger.error(f"Lead load error: {e}"))
        self._worker.done.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_leads_loaded(self, leads, total):
        self._total_leads = total
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        self._count_label.setText(f"{total:,} leads")
        self._page_label.setText(f"Page {self._current_page} of {total_pages}")
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < total_pages)

        self._table.setSortingEnabled(False)
        self._table.clear_rows()
        self._table.setRowCount(0)

        from PySide6.QtWidgets import QTableWidgetItem
        for lead in leads:
            row = self._table.rowCount()
            self._table.insertRow(row)

            name_item = QTableWidgetItem(lead.name)
            name_item.setData(Qt.ItemDataRole.UserRole, lead.id)
            name_item.setForeground(QColor("#C9CDD4"))
            self._table.setItem(row, 0, name_item)

            self._table.setItem(row, 1, self._item(lead.company or "—"))
            self._table.setItem(row, 2, self._item(lead.phone or "—"))
            self._table.setCellWidget(row, 3, StatusBadge(lead.status.value))
            self._table.setCellWidget(row, 4, ScoreWidget(lead.lead_score))
            self._table.setCellWidget(row, 5, PriorityBadge(lead.priority.value))
            self._table.setItem(row, 6, self._item(lead.assigned_to_name or "—"))

            last_contact = lead.last_contact.strftime("%b %d") if lead.last_contact else "—"
            next_followup = lead.next_followup.strftime("%b %d") if lead.next_followup else "—"
            self._table.setItem(row, 7, self._item(last_contact))
            self._table.setItem(row, 8, self._item(next_followup))

        self._table.setSortingEnabled(True)

    def _item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor("#C9CDD4"))
        return item

    def _on_row_double_click(self, index):
        item = self._table.item(index.row(), 0)
        if item:
            lead_id = item.data(Qt.ItemDataRole.UserRole)
            if lead_id:
                self.open_lead.emit(lead_id)

    def _context_menu(self, pos):
        from PySide6.QtWidgets import QMenu
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        item = self._table.item(row, 0)
        if not item:
            return
        lead_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #191D24; border: 1px solid #292E36; color: #C9CDD4; }
            QMenu::item:selected { background-color: #1E3A5F; }
        """)
        open_action = menu.addAction("Open Lead Detail")
        open_action.triggered.connect(lambda: self.open_lead.emit(lead_id))
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _import_leads(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Leads", "",
            "Spreadsheet Files (*.xlsx *.xls *.csv)"
        )
        if not path:
            return

        try:
            result = self.services.import_service.validate_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to read file:\n{str(e)}")
            return

        dialog = ImportPreviewDialog(result, self)
        dialog.confirmed.connect(self._do_import)
        dialog.exec()

    def _do_import(self, valid_leads: list):
        self._thread = QThread()
        self._imp_worker = ImportWorker(self.services, valid_leads)
        self._imp_worker.moveToThread(self._thread)
        self._thread.started.connect(self._imp_worker.run)
        self._imp_worker.done.connect(self._on_import_done)
        self._imp_worker.error.connect(self._on_import_error)
        self._imp_worker.done.connect(self._thread.quit)
        self._imp_worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_import_done(self, count: int):
        QMessageBox.information(
            self, "Import Complete",
            f"Successfully imported {count} leads."
        )
        self._load_leads()

    def _on_import_error(self, msg: str):
        QMessageBox.critical(self, "Import Failed", f"Import failed:\n{msg}")

    def _prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._load_leads()

    def _next_page(self):
        total_pages = max(1, (self._total_leads + PAGE_SIZE - 1) // PAGE_SIZE)
        if self._current_page < total_pages:
            self._current_page += 1
            self._load_leads()

    def refresh(self):
        self._load_leads()
