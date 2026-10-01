"""
LeadFlow — Activity Rail
Narrow persistent icon navigation strip on the far left.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy,
)

# (section_id, tooltip, icon_char)
RAIL_SECTIONS = [
    ("dashboard",  "Dashboard",   "⊞"),
    ("leads",      "Leads",       "◉"),
    ("calls",      "Calls",       "◎"),
    ("followups",  "Follow-ups",  "◇"),
    ("analytics",  "Analytics",   "◈"),
]

ADMIN_SECTIONS = [
    ("users",      "Users",       "⬡"),
]


class _RailButton(QPushButton):
    def __init__(self, section_id: str, icon: str, tooltip: str, parent=None):
        super().__init__(icon, parent)
        self.section_id = section_id
        self.setObjectName("rail_btn")
        self.setFixedSize(48, 40)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(False)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class ActivityRail(QWidget):
    """
    Narrow 48-px vertical icon strip.
    Emits section_changed(section_id) when user clicks a section.
    """

    section_changed = Signal(str)

    def __init__(self, services, parent=None):
        super().__init__(parent)
        self.setObjectName("activity_rail")
        self.setFixedWidth(48)
        self._services = services
        self._buttons: dict[str, _RailButton] = {}
        self._active_id: str | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(0)

        # Logo mark
        logo = QLabel("LF")
        logo.setObjectName("rail_logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedHeight(36)
        layout.addWidget(logo)

        sep = self._sep()
        layout.addWidget(sep)
        layout.addSpacing(4)

        # Main nav
        for section_id, tooltip, icon in RAIL_SECTIONS:
            btn = _RailButton(section_id, icon, tooltip)
            btn.clicked.connect(lambda _, sid=section_id: self.section_changed.emit(sid))
            self._buttons[section_id] = btn
            layout.addWidget(btn)

        # Admin sections (role-gated)
        from app.backend.models.domain import UserRole
        if self._services.current_role in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            layout.addSpacing(4)
            layout.addWidget(self._sep())
            layout.addSpacing(4)
            for section_id, tooltip, icon in ADMIN_SECTIONS:
                btn = _RailButton(section_id, icon, tooltip)
                btn.clicked.connect(lambda _, sid=section_id: self.section_changed.emit(sid))
                self._buttons[section_id] = btn
                layout.addWidget(btn)

        layout.addStretch(1)

        # Bottom: Settings
        layout.addWidget(self._sep())
        layout.addSpacing(4)
        settings_btn = _RailButton("settings", "⚙", "Settings")
        settings_btn.clicked.connect(lambda: self.section_changed.emit("settings"))
        self._buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)
        layout.addSpacing(4)

    def _sep(self) -> QFrame:
        line = QFrame()
        line.setObjectName("rail_separator")
        line.setFixedHeight(1)
        line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return line

    def set_active(self, section_id: str) -> None:
        for sid, btn in self._buttons.items():
            btn.set_active(sid == section_id)
        self._active_id = section_id
