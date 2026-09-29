"""
LeadFlow — Reusable UI Components
Enterprise-grade widget library for consistent UI.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QFrame, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QProgressBar,
)

from app.desktop.styles import (
    get_status_color, get_priority_color, get_sentiment_color, score_to_color
)


# ─────────────────────────────────────────────────────────
# Section Divider
# ─────────────────────────────────────────────────────────

class HLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet("color: #1E2329; border: none; border-top: 1px solid #1E2329;")
        self.setFixedHeight(1)


# ─────────────────────────────────────────────────────────
# KPI Card — uniform surface, no rainbow
# ─────────────────────────────────────────────────────────

class KPICard(QWidget):
    def __init__(self, label: str, value: str = "—", delta: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("kpi_card")
        self.setMinimumWidth(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self._label = QLabel(label.upper())
        self._label.setObjectName("kpi_label")

        self._value = QLabel(value)
        self._value.setObjectName("kpi_value")

        self._delta = QLabel(delta)
        self._delta.setObjectName("kpi_delta" if not delta.startswith("-") else "kpi_delta_neg")
        self._delta.setVisible(bool(delta))

        layout.addWidget(self._label)
        layout.addWidget(self._value)
        if delta:
            layout.addWidget(self._delta)

    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_delta(self, delta: str) -> None:
        self._delta.setText(delta)
        self._delta.setVisible(bool(delta))


# ─────────────────────────────────────────────────────────
# Panel Widget
# ─────────────────────────────────────────────────────────

class Panel(QWidget):
    """Standard panel with optional header."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("panel")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        if title:
            header = QWidget()
            header.setObjectName("panel_header")
            header.setFixedHeight(36)
            h_layout = QHBoxLayout(header)
            h_layout.setContentsMargins(14, 0, 14, 0)

            title_label = QLabel(title.upper())
            title_label.setObjectName("panel_title")
            h_layout.addWidget(title_label)
            h_layout.addStretch()

            self._layout.addWidget(header)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(14, 12, 14, 12)
        self.content_layout.setSpacing(8)
        self._layout.addWidget(self.content)

    def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.content_layout.addLayout(layout)


# ─────────────────────────────────────────────────────────
# Status Badge Label
# ─────────────────────────────────────────────────────────

class StatusBadge(QLabel):
    STATUS_NAMES = {
        "new": "NEW",
        "contacted": "CONTACTED",
        "interested": "INTERESTED",
        "follow_up": "FOLLOW-UP",
        "negotiation": "NEGOTIATION",
        "converted": "CONVERTED",
        "lost": "LOST",
    }

    OBJECT_NAMES = {
        "new": "badge_new",
        "contacted": "badge_neutral",
        "interested": "badge_interested",
        "follow_up": "badge_high",
        "negotiation": "badge_mixed",
        "converted": "badge_converted",
        "lost": "badge_lost",
    }

    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)

    def set_status(self, status: str) -> None:
        key = status.lower()
        text = self.STATUS_NAMES.get(key, status.upper())
        obj_name = self.OBJECT_NAMES.get(key, "badge_new")
        self.setText(text)
        self.setObjectName(obj_name)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class PriorityBadge(QLabel):
    OBJECT_NAMES = {
        "high": "badge_high",
        "medium": "badge_medium",
        "low": "badge_low",
    }

    def __init__(self, priority: str, parent=None):
        super().__init__(priority.upper(), parent)
        key = priority.lower()
        self.setObjectName(self.OBJECT_NAMES.get(key, "badge_low"))


class SentimentBadge(QLabel):
    OBJECT_NAMES = {
        "POSITIVE": "badge_positive",
        "NEGATIVE": "badge_negative",
        "NEUTRAL": "badge_neutral",
        "MIXED": "badge_mixed",
    }

    def __init__(self, sentiment: str, parent=None):
        super().__init__(sentiment, parent)
        self.setObjectName(self.OBJECT_NAMES.get(sentiment.upper(), "badge_neutral"))


# ─────────────────────────────────────────────────────────
# Score Progress Widget
# ─────────────────────────────────────────────────────────

class ScoreWidget(QWidget):
    """Compact score display: number + thin bar."""

    def __init__(self, score: int = 0, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        color = score_to_color(score)
        self._score_label = QLabel(str(score))
        self._score_label.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 12px;")
        self._score_label.setFixedWidth(28)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(score)
        self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(
            f"QProgressBar {{ background-color: #1D2229; border: none; border-radius: 2px; }}"
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 2px; }}"
        )

        layout.addWidget(self._score_label)
        layout.addWidget(self._bar)

    def set_score(self, score: int) -> None:
        color = score_to_color(score)
        self._score_label.setText(str(score))
        self._score_label.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 12px;")
        self._bar.setValue(score)
        self._bar.setStyleSheet(
            f"QProgressBar {{ background-color: #1D2229; border: none; border-radius: 2px; }}"
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 2px; }}"
        )


# ─────────────────────────────────────────────────────────
# Enterprise Data Table
# ─────────────────────────────────────────────────────────

class DataTable(QTableWidget):
    """Styled enterprise data table."""

    def __init__(self, columns: list[str], parent=None):
        super().__init__(0, len(columns), parent)
        self.setHorizontalHeaderLabels(columns)
        self._configure()

    def _configure(self):
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(36)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def add_row(self, cells: list) -> int:
        row = self.rowCount()
        self.insertRow(row)
        for col, cell in enumerate(cells):
            if isinstance(cell, QWidget):
                self.setCellWidget(row, col, cell)
            elif isinstance(cell, QTableWidgetItem):
                self.setItem(row, col, cell)
            else:
                item = QTableWidgetItem(str(cell) if cell is not None else "")
                item.setForeground(QColor("#C9CDD4"))
                self.setItem(row, col, item)
        return row

    def clear_rows(self):
        self.setRowCount(0)


# ─────────────────────────────────────────────────────────
# Separator with label
# ─────────────────────────────────────────────────────────

class SectionHeader(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 4)
        layout.setSpacing(8)

        label = QLabel(text.upper())
        label.setObjectName("nav_section_label")
        label.setStyleSheet("color: #626975; font-size: 10px; font-weight: 600; letter-spacing: 1.0px; padding: 0;")

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #1E2329; border: none; border-top: 1px solid #1E2329;")

        layout.addWidget(label)
        layout.addWidget(line, 1)


# ─────────────────────────────────────────────────────────
# Field row (label + value)
# ─────────────────────────────────────────────────────────

class FieldRow(QWidget):
    def __init__(self, label: str, value: str = "—", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(12)

        lbl = QLabel(label)
        lbl.setObjectName("field_label")
        lbl.setFixedWidth(130)

        self._val = QLabel(value)
        self._val.setObjectName("field_value")
        self._val.setWordWrap(True)

        layout.addWidget(lbl)
        layout.addWidget(self._val, 1)

    def set_value(self, value: str) -> None:
        self._val.setText(value)


# ─────────────────────────────────────────────────────────
# Processing Step Widget
# ─────────────────────────────────────────────────────────

class ProcessingStep(QWidget):
    """One step in a pipeline progress view."""

    STATUS_ICONS = {
        "pending": "○",
        "active": "◉",
        "done": "✓",
        "error": "✗",
    }

    STATUS_COLORS = {
        "pending": "#464D58",
        "active": "#4A9EFF",
        "done": "#2ECC71",
        "error": "#E05252",
    }

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._label_text = label
        self._status = "pending"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(10)

        self._icon = QLabel("○")
        self._icon.setFixedWidth(16)
        self._icon.setStyleSheet(f"color: #464D58; font-size: 12px;")

        self._text = QLabel(label)
        self._text.setStyleSheet("color: #464D58; font-size: 12px;")

        layout.addWidget(self._icon)
        layout.addWidget(self._text, 1)

    def set_status(self, status: str) -> None:
        self._status = status
        color = self.STATUS_COLORS.get(status, "#464D58")
        icon = self.STATUS_ICONS.get(status, "○")
        self._icon.setText(icon)
        self._icon.setStyleSheet(f"color: {color}; font-size: 12px;")
        self._text.setStyleSheet(f"color: {color}; font-size: 12px;")


# ─────────────────────────────────────────────────────────
# Empty State Widget
# ─────────────────────────────────────────────────────────

class EmptyState(QWidget):
    """Professional empty state with icon and message."""

    def __init__(self, icon: str, title: str, message: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("color: #3A4049; font-size: 28px;")

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #626975; font-size: 13px; font-weight: 500;")

        layout.addWidget(icon_label)
        layout.addWidget(title_label)

        if message:
            msg_label = QLabel(message)
            msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg_label.setStyleSheet("color: #464D58; font-size: 12px;")
            msg_label.setWordWrap(True)
            layout.addWidget(msg_label)


# ─────────────────────────────────────────────────────────
# Toolbar Widget
# ─────────────────────────────────────────────────────────

class Toolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #161A20; border-bottom: 1px solid #1E2329;")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 0, 12, 0)
        self._layout.setSpacing(6)

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)

    def add_stretch(self) -> None:
        self._layout.addStretch()

    def add_spacing(self, px: int) -> None:
        self._layout.addSpacing(px)
