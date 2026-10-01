"""
LeadFlow — Bottom Panel
Collapsible / resizable bottom panel with tabbed views (Output, Activity).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QStackedWidget, QFrame,
    QSizePolicy,
)


class BottomPanel(QWidget):
    """
    Collapsible bottom panel.
    Contains: Output log, Activity feed.
    """

    collapse_toggled = Signal(bool)  # True=expanded, False=collapsed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottom_panel")
        self._collapsed = True

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Panel header (always visible) ─────────────────────
        self._header = QWidget()
        self._header.setObjectName("bottom_panel_header")
        self._header.setFixedHeight(28)
        h_lay = QHBoxLayout(self._header)
        h_lay.setContentsMargins(0, 0, 8, 0)
        h_lay.setSpacing(0)

        # Tab buttons
        self._tab_btns: dict[str, QPushButton] = {}
        for tab_id, label in [("output", "Output"), ("activity", "Activity")]:
            btn = QPushButton(label)
            btn.setObjectName("bottom_tab_btn")
            btn.clicked.connect(lambda _, tid=tab_id: self._show_tab(tid))
            self._tab_btns[tab_id] = btn
            h_lay.addWidget(btn)

        h_lay.addStretch(1)

        # Collapse toggle button
        self._toggle_btn = QPushButton("∧")
        self._toggle_btn.setObjectName("panel_collapse_btn")
        self._toggle_btn.setToolTip("Expand/collapse panel")
        self._toggle_btn.clicked.connect(self._toggle)
        h_lay.addWidget(self._toggle_btn)

        outer.addWidget(self._header)

        sep = QFrame()
        sep.setFixedHeight(0)
        outer.addWidget(sep)

        # ── Tab content (collapsible) ─────────────────────────
        self._content = QWidget()
        content_lay = QVBoxLayout(self._content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        self._stack = QStackedWidget()
        content_lay.addWidget(self._stack)

        # Output tab
        self._output = QTextEdit()
        self._output.setObjectName("bottom_output")
        self._output.setReadOnly(True)
        self._output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._stack.addWidget(self._output)

        # Activity tab
        self._activity = QTextEdit()
        self._activity.setObjectName("bottom_output")
        self._activity.setReadOnly(True)
        self._stack.addWidget(self._activity)

        outer.addWidget(self._content)

        # Start collapsed
        self._content.hide()
        self.setFixedHeight(28)  # just the header
        self._cur_tab = "output"
        self._update_tab_state()

    # ─────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────

    def log_output(self, message: str) -> None:
        self._output.append(message)

    def log_activity(self, message: str) -> None:
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self._activity.append(f"[{ts}] {message}")

    def expand(self) -> None:
        if self._collapsed:
            self._toggle()

    def collapse(self) -> None:
        if not self._collapsed:
            self._toggle()

    # ─────────────────────────────────────────────────────
    # Internal
    # ─────────────────────────────────────────────────────

    def _toggle(self) -> None:
        self._collapsed = not self._collapsed
        if self._collapsed:
            self._content.hide()
            self.setFixedHeight(28)
            self._toggle_btn.setText("∧")
        else:
            self._content.show()
            self.setMinimumHeight(28)
            self.setMaximumHeight(16777215)
            self.setFixedHeight(160)
            self._toggle_btn.setText("∨")
        self.collapse_toggled.emit(not self._collapsed)

    def _show_tab(self, tab_id: str) -> None:
        self._cur_tab = tab_id
        tab_index = {"output": 0, "activity": 1}.get(tab_id, 0)
        self._stack.setCurrentIndex(tab_index)
        self._update_tab_state()
        if self._collapsed:
            self.expand()

    def _update_tab_state(self) -> None:
        for tid, btn in self._tab_btns.items():
            btn.setProperty("active", "true" if tid == self._cur_tab else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
