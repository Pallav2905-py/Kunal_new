"""
LeadFlow — Workspace Tabs
Tab bar + stacked content area for the main workspace.
Implements desktop-IDE-style tabs that can be opened/closed.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QScrollArea, QSizePolicy,
    QFrame,
)


class _TabButton(QWidget):
    """Single tab widget: [icon] title [×]"""

    clicked = Signal()
    close_requested = Signal()

    def __init__(self, title: str, closeable: bool = True, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._main_btn = QPushButton(title)
        self._main_btn.setObjectName("workspace_tab")
        self._main_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._main_btn.clicked.connect(self.clicked)
        layout.addWidget(self._main_btn)

        if closeable:
            self._close = QPushButton("×")
            self._close.setObjectName("tab_close_btn")
            self._close.clicked.connect(self.close_requested)
            layout.addWidget(self._close)

    def set_active(self, active: bool) -> None:
        self._main_btn.setProperty("active", "true" if active else "false")
        self._main_btn.style().unpolish(self._main_btn)
        self._main_btn.style().polish(self._main_btn)

        # Show/hide close button indicator via color
        if hasattr(self, "_close"):
            if active:
                self._close.setStyleSheet("QPushButton#tab_close_btn { color: #3D4E65; }")
            else:
                self._close.setStyleSheet("QPushButton#tab_close_btn { color: transparent; }")

    def set_title(self, title: str) -> None:
        self._main_btn.setText(title)


class WorkspaceArea(QWidget):
    """
    Main workspace: tab bar at top, stacked content below.

    API:
        open_tab(page_id, widget, title, closeable=True) → ensure tab open + show
        close_tab(page_id)
        focus_tab(page_id)
        current_page_id → str
    """

    tab_closed = Signal(str)  # page_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workspace_area")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Tab bar row ───────────────────────────────────────
        tab_bar_row = QWidget()
        tab_bar_row.setObjectName("workspace_tab_bar")
        tab_bar_row.setFixedHeight(32)
        tab_row_layout = QHBoxLayout(tab_bar_row)
        tab_row_layout.setContentsMargins(0, 0, 0, 0)
        tab_row_layout.setSpacing(0)

        # Scrollable tab area
        self._tab_scroll = QScrollArea()
        self._tab_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._tab_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._tab_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._tab_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._tab_scroll.setFixedHeight(32)

        self._tab_container = QWidget()
        self._tab_container_layout = QHBoxLayout(self._tab_container)
        self._tab_container_layout.setContentsMargins(0, 0, 0, 0)
        self._tab_container_layout.setSpacing(0)
        self._tab_container_layout.addStretch(1)

        self._tab_scroll.setWidget(self._tab_container)
        self._tab_scroll.setWidgetResizable(True)
        tab_row_layout.addWidget(self._tab_scroll)

        outer.addWidget(tab_bar_row)

        # Thin line under tab bar
        sep = QFrame()
        sep.setFixedHeight(0)
        outer.addWidget(sep)

        # ── Content stack ─────────────────────────────────────
        self._stack = QStackedWidget()
        outer.addWidget(self._stack, 1)

        # ── Empty-state placeholder ───────────────────────────
        self._placeholder = self._build_placeholder()
        self._stack.addWidget(self._placeholder)

        # State
        self._tabs: dict[str, dict] = {}  # page_id → {tab_btn, widget}
        self._active_page_id: str | None = None

    def _build_placeholder(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(6)

        ico = QLabel("⊞")
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("color: #1F2B3E; font-size: 32px;")
        lbl = QLabel("Select a section from the left rail")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #273347; font-size: 12px;")
        lay.addWidget(ico)
        lay.addWidget(lbl)
        return w

    # ─────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────

    def open_tab(self, page_id: str, widget: QWidget, title: str, closeable: bool = True) -> None:
        """Open a tab or focus it if already open."""
        if page_id in self._tabs:
            self.focus_tab(page_id)
            return

        tab_btn = _TabButton(title, closeable)
        tab_btn.clicked.connect(lambda: self.focus_tab(page_id))
        tab_btn.close_requested.connect(lambda: self._close_tab(page_id))

        # Insert before stretch
        count = self._tab_container_layout.count()
        self._tab_container_layout.insertWidget(count - 1, tab_btn)

        self._stack.addWidget(widget)
        self._tabs[page_id] = {"tab_btn": tab_btn, "widget": widget}

        self.focus_tab(page_id)

    def focus_tab(self, page_id: str) -> None:
        if page_id not in self._tabs:
            return
        # Deactivate all
        for pid, info in self._tabs.items():
            info["tab_btn"].set_active(pid == page_id)
        # Show content
        self._stack.setCurrentWidget(self._tabs[page_id]["widget"])
        self._active_page_id = page_id

    def close_tab(self, page_id: str) -> None:
        self._close_tab(page_id)

    def replace_tab(self, page_id: str, new_widget: QWidget) -> None:
        """Replace the widget in an existing tab (for refreshed lead details)."""
        if page_id not in self._tabs:
            return
        old_widget = self._tabs[page_id]["widget"]
        idx = self._stack.indexOf(old_widget)
        self._stack.removeWidget(old_widget)
        old_widget.deleteLater()
        self._stack.insertWidget(idx, new_widget)
        self._tabs[page_id]["widget"] = new_widget
        if self._active_page_id == page_id:
            self._stack.setCurrentWidget(new_widget)

    def has_tab(self, page_id: str) -> bool:
        return page_id in self._tabs

    def rename_tab(self, page_id: str, title: str) -> None:
        if page_id in self._tabs:
            self._tabs[page_id]["tab_btn"].set_title(title)

    @property
    def current_page_id(self) -> Optional[str]:
        return self._active_page_id

    def show_placeholder(self) -> None:
        self._stack.setCurrentWidget(self._placeholder)
        self._active_page_id = None

    # ─────────────────────────────────────────────────────
    # Internal
    # ─────────────────────────────────────────────────────

    def _close_tab(self, page_id: str) -> None:
        if page_id not in self._tabs:
            return
        info = self._tabs.pop(page_id)
        tab_btn = info["tab_btn"]
        widget = info["widget"]

        self._tab_container_layout.removeWidget(tab_btn)
        tab_btn.deleteLater()

        self._stack.removeWidget(widget)
        widget.deleteLater()

        self.tab_closed.emit(page_id)

        # Focus another tab or placeholder
        if self._tabs:
            last_id = list(self._tabs.keys())[-1]
            self.focus_tab(last_id)
        else:
            self.show_placeholder()
            self._active_page_id = None
