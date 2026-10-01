"""
LeadFlow — Inspector Panel
Right-side contextual detail panel that shows properties of the selected record.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy,
)

from app.desktop.components.widgets import StatusBadge, PriorityBadge, ScoreWidget


def _field_row(label: str, value: str) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(12, 3, 12, 3)
    lay.setSpacing(8)
    lbl = QLabel(label)
    lbl.setObjectName("inspector_field_label")
    lbl.setFixedWidth(70)
    val = QLabel(value or "—")
    val.setObjectName("inspector_field_value")
    val.setWordWrap(True)
    lay.addWidget(lbl)
    lay.addWidget(val, 1)
    return w


def _section_divider(title: str) -> QLabel:
    lbl = QLabel(title.upper())
    lbl.setObjectName("inspector_section_title")
    return lbl


class InspectorPanel(QWidget):
    """
    Collapsible right-side inspector.
    Call show_lead(lead) to populate, or clear() to reset.
    """

    open_lead_requested = Signal(str)  # lead_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inspector_panel")
        self.setMinimumWidth(220)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("inspector_header")
        header.setFixedHeight(32)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(12, 0, 6, 0)
        h_lay.setSpacing(4)

        title = QLabel("INSPECTOR")
        title.setObjectName("inspector_title")
        h_lay.addWidget(title)
        h_lay.addStretch(1)

        self._collapse_btn = QPushButton("›")
        self._collapse_btn.setObjectName("inspector_toggle")
        self._collapse_btn.setFixedSize(20, 20)
        self._collapse_btn.clicked.connect(self._toggle_collapse)
        h_lay.addWidget(self._collapse_btn)

        outer.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #18202F;")
        outer.addWidget(sep)

        # ── Scrollable content ────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(self._scroll, 1)

        self._content = QWidget()
        self._content_lay = QVBoxLayout(self._content)
        self._content_lay.setContentsMargins(0, 4, 0, 8)
        self._content_lay.setSpacing(0)
        self._scroll.setWidget(self._content)

        # Placeholder
        self._placeholder = QLabel("No item selected")
        self._placeholder.setObjectName("inspector_placeholder")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_lay.addWidget(self._placeholder)
        self._content_lay.addStretch(1)

        self._collapsed = False
        self._lead_id: Optional[str] = None

    def show_lead(self, lead) -> None:
        """Populate inspector with a lead's properties."""
        self._lead_id = str(lead.id)
        self._rebuild(lead)

    def clear(self) -> None:
        self._lead_id = None
        self._rebuild(None)

    def _rebuild(self, lead) -> None:
        # Remove all children
        while self._content_lay.count():
            item = self._content_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if lead is None:
            placeholder = QLabel("No item selected")
            placeholder.setObjectName("inspector_placeholder")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._content_lay.addWidget(placeholder)
            self._content_lay.addStretch(1)
            return

        # ── Identity ──────────────────────────────────────────
        name_lbl = QLabel(lead.name)
        name_lbl.setStyleSheet("color: #DCE4EF; font-size: 13px; font-weight: 600; padding: 10px 12px 4px 12px;")
        name_lbl.setWordWrap(True)
        self._content_lay.addWidget(name_lbl)

        # Badges row
        badge_row = QWidget()
        badge_lay = QHBoxLayout(badge_row)
        badge_lay.setContentsMargins(12, 0, 12, 8)
        badge_lay.setSpacing(4)
        badge_lay.addWidget(StatusBadge(lead.status.value))
        badge_lay.addWidget(PriorityBadge(lead.priority.value))
        badge_lay.addStretch(1)
        score_w = ScoreWidget(lead.lead_score)
        badge_lay.addWidget(score_w)
        self._content_lay.addWidget(badge_row)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #18202F; margin: 0 0;")
        self._content_lay.addWidget(sep1)

        # ── Contact info ──────────────────────────────────────
        self._content_lay.addWidget(_section_divider("Contact"))
        self._content_lay.addWidget(_field_row("Company", lead.company or "—"))
        self._content_lay.addWidget(_field_row("Phone", lead.phone or "—"))
        self._content_lay.addWidget(_field_row("Email", lead.email or "—"))

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #18202F;")
        self._content_lay.addWidget(sep2)

        # ── Assignment ────────────────────────────────────────
        self._content_lay.addWidget(_section_divider("Assignment"))
        self._content_lay.addWidget(_field_row("Assigned To", lead.assigned_to_name or "—"))

        if lead.last_contact:
            self._content_lay.addWidget(_field_row("Last Contact", lead.last_contact.strftime("%b %d, %Y")))
        if lead.next_followup:
            self._content_lay.addWidget(_field_row("Next Follow-up", lead.next_followup.strftime("%b %d, %Y")))

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("color: #18202F;")
        self._content_lay.addWidget(sep3)

        # ── Actions ───────────────────────────────────────────
        self._content_lay.addWidget(_section_divider("Actions"))
        btn_w = QWidget()
        btn_lay = QVBoxLayout(btn_w)
        btn_lay.setContentsMargins(12, 4, 12, 4)
        btn_lay.setSpacing(4)

        open_btn = QPushButton("Open Lead Detail")
        open_btn.setObjectName("btn_primary")
        open_btn.setFixedHeight(26)
        open_btn.clicked.connect(lambda: self.open_lead_requested.emit(self._lead_id))
        btn_lay.addWidget(open_btn)

        self._content_lay.addWidget(btn_w)
        self._content_lay.addStretch(1)

    def _toggle_collapse(self) -> None:
        if self._collapsed:
            self._scroll.show()
            self._collapsed = False
            self.setMaximumWidth(16777215)
            self.setMinimumWidth(220)
            self._collapse_btn.setText("›")
        else:
            self._scroll.hide()
            self._collapsed = True
            self.setMaximumWidth(32)
            self.setMinimumWidth(32)
            self._collapse_btn.setText("‹")
