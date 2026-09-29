"""
LeadFlow — Main Application Window
Professional enterprise desktop shell with sidebar navigation.
"""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSizePolicy,
    QFrame, QStatusBar, QSplitter, QSpacerItem,
)

from app.desktop.app_services import AppServices
from app.desktop.styles import LEADFLOW_STYLESHEET
from app.backend.models.domain import UserRole, AuthToken

logger = logging.getLogger(__name__)

NAV_ITEMS = [
    ("dashboard", "Dashboard", "⬜"),
    ("leads", "Leads", "⬡"),
    ("calls", "Calls", "◎"),
    ("followups", "Follow-ups", "◇"),
    ("analytics", "Analytics", "◈"),
]

ADMIN_ITEMS = [
    ("users", "Users", "◉"),
    ("settings", "Settings", "⚙"),
]


class NavButton(QPushButton):
    def __init__(self, page_id: str, text: str, parent=None):
        super().__init__(text, parent)
        self.page_id = page_id
        self.setObjectName("nav_button")
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(False)

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class MainWindow(QMainWindow):
    """Enterprise application shell."""

    def __init__(self, services: AppServices, auth_token: AuthToken, parent=None):
        super().__init__(parent)
        self.services = services
        services.current_user = auth_token

        self.setWindowTitle(f"LeadFlow — {auth_token.user.name}")
        self.setMinimumSize(1280, 720)
        self.resize(1440, 900)

        self._nav_buttons: dict[str, NavButton] = {}
        self._current_page = "dashboard"
        self._pages: dict[str, QWidget] = {}

        self._apply_theme()
        self._setup_ui()
        self._navigate("dashboard")

    def _apply_theme(self):
        self.setStyleSheet(LEADFLOW_STYLESHEET)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer_layout = QVBoxLayout(central)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # ── Top Bar ──────────────────────────────────────
        topbar = self._build_topbar()
        outer_layout.addWidget(topbar)

        # ── Body: Sidebar + Content ───────────────────────
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        body_layout.addWidget(sidebar)

        # Thin divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet("color: #1E2329; border: none; border-left: 1px solid #1E2329;")
        div.setFixedWidth(1)
        body_layout.addWidget(div)

        # Main content stack
        self._stack = QStackedWidget()
        self._stack.setObjectName("content_area")
        body_layout.addWidget(self._stack, 1)

        outer_layout.addWidget(body, 1)

        # ── Status Bar ────────────────────────────────────
        self._status_bar = QStatusBar()
        self._status_bar.showMessage(
            f"Connected to MongoDB  ·  {self.services.current_user.user.name}  ·  "
            f"{self.services.current_role.value.replace('_', ' ').title()}"
        )
        self.setStatusBar(self._status_bar)

    def _build_topbar(self) -> QWidget:
        topbar = QWidget()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(44)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # Logo
        logo = QLabel("LEADFLOW")
        logo.setStyleSheet(
            "color: #E6E9ED; font-size: 13px; font-weight: 700; "
            "letter-spacing: 1.5px;"
        )
        logo.setFixedWidth(200)
        layout.addWidget(logo)

        # Breadcrumb / title
        self._topbar_title = QLabel("Dashboard")
        self._topbar_title.setObjectName("topbar_title")
        layout.addWidget(self._topbar_title)
        layout.addStretch()

        # User info
        user = self.services.current_user.user
        user_label = QLabel(f"{user.name}  ·  {user.role.value.replace('_', ' ').title()}")
        user_label.setStyleSheet("color: #8B929E; font-size: 11px;")
        layout.addWidget(user_label)

        return topbar

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo area
        logo_area = QWidget()
        logo_area.setObjectName("sidebar_logo_area")
        logo_area.setFixedHeight(56)
        la_layout = QVBoxLayout(logo_area)
        la_layout.setContentsMargins(16, 10, 16, 10)
        la_layout.setSpacing(2)

        app_name = QLabel("LeadFlow")
        app_name.setObjectName("app_name_label")
        app_subtitle = QLabel("CRM Intelligence Platform")
        app_subtitle.setObjectName("app_subtitle_label")

        la_layout.addWidget(app_name)
        la_layout.addWidget(app_subtitle)
        layout.addWidget(logo_area)

        # Workspace nav
        workspace_label = QLabel("WORKSPACE")
        workspace_label.setObjectName("nav_section_label")
        layout.addWidget(workspace_label)
        layout.addSpacing(2)

        for page_id, text, icon in NAV_ITEMS:
            btn = NavButton(page_id, f"  {text}")
            btn.clicked.connect(lambda checked, pid=page_id: self._navigate(pid))
            self._nav_buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addSpacing(8)

        # Admin nav (only for admin/manager)
        role = self.services.current_role
        if role in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            admin_label = QLabel("ADMINISTRATION")
            admin_label.setObjectName("nav_section_label")
            layout.addWidget(admin_label)
            layout.addSpacing(2)

            for page_id, text, icon in ADMIN_ITEMS:
                if page_id == "users" and not self.services.can_manage_users():
                    continue
                btn = NavButton(page_id, f"  {text}")
                btn.clicked.connect(lambda checked, pid=page_id: self._navigate(pid))
                self._nav_buttons[page_id] = btn
                layout.addWidget(btn)

        layout.addStretch()

        # User area at bottom
        user_area = QWidget()
        user_area.setObjectName("sidebar_user_area")
        ua_layout = QVBoxLayout(user_area)
        ua_layout.setContentsMargins(0, 8, 0, 8)
        ua_layout.setSpacing(2)

        dot_row = QHBoxLayout()
        dot_row.setContentsMargins(0, 0, 0, 0)
        dot = QLabel("●")
        dot.setObjectName("connection_dot")
        dot.setStyleSheet("color: #2ECC71; font-size: 8px;")
        conn_label = QLabel("MongoDB Connected")
        conn_label.setStyleSheet("color: #626975; font-size: 10px;")
        dot_row.addWidget(dot)
        dot_row.addWidget(conn_label)
        dot_row.addStretch()
        ua_layout.addLayout(dot_row)

        user = self.services.current_user.user
        user_name = QLabel(user.name)
        user_name.setObjectName("user_name_label")
        user_role = QLabel(user.role.value.replace("_", " ").title())
        user_role.setObjectName("user_role_label")

        logout_btn = QPushButton("Sign out")
        logout_btn.setObjectName("logout_button")
        logout_btn.clicked.connect(self._logout)

        ua_layout.addWidget(user_name)
        ua_layout.addWidget(user_role)
        ua_layout.addSpacing(4)
        ua_layout.addWidget(logout_btn)

        layout.addWidget(user_area)

        return sidebar

    def _navigate(self, page_id: str):
        """Navigate to a page, creating it if needed."""
        if page_id not in self._pages:
            page = self._create_page(page_id)
            if page:
                self._pages[page_id] = page
                self._stack.addWidget(page)
            else:
                return

        # Update nav button states
        for pid, btn in self._nav_buttons.items():
            btn.set_active(pid == page_id)

        self._stack.setCurrentWidget(self._pages[page_id])
        self._current_page = page_id

        # Update top bar title
        display_name = {
            "dashboard": "Dashboard",
            "leads": "Leads",
            "calls": "Call Analysis",
            "followups": "Follow-ups",
            "analytics": "Sales Intelligence",
            "users": "Users",
            "settings": "Settings",
        }.get(page_id, page_id.title())
        self._topbar_title.setText(display_name)

    def _create_page(self, page_id: str) -> Optional[QWidget]:
        """Lazy-create page widgets."""
        try:
            if page_id == "dashboard":
                from app.desktop.dashboard.dashboard_page import DashboardPage
                page = DashboardPage(self.services)
                page.open_lead.connect(self._open_lead)
                return page

            elif page_id == "leads":
                from app.desktop.leads.leads_page import LeadsPage
                page = LeadsPage(self.services)
                page.open_lead.connect(self._open_lead)
                return page

            elif page_id == "calls":
                from app.desktop.calls.calls_page import CallsPage
                return CallsPage(self.services)

            elif page_id == "followups":
                from app.desktop.followups.followups_page import FollowupsPage
                page = FollowupsPage(self.services)
                page.open_lead.connect(self._open_lead)
                return page

            elif page_id == "analytics":
                from app.desktop.analytics.analytics_page import AnalyticsPage
                return AnalyticsPage(self.services)

            elif page_id == "users":
                if not self.services.can_manage_users():
                    return self._access_denied_page()
                from app.desktop.users.users_page import UsersPage
                return UsersPage(self.services)

            elif page_id == "settings":
                return self._settings_page()

            elif page_id.startswith("lead_detail:"):
                lead_id = page_id.split(":", 1)[1]
                from app.desktop.leads.lead_detail_page import LeadDetailPage
                page = LeadDetailPage(self.services, lead_id)
                page.go_back.connect(lambda: self._navigate("leads"))
                page.open_call_analysis.connect(self._open_call_analysis)
                page.open_upload_recording.connect(self._open_upload_for_lead)
                return page

        except Exception as e:
            logger.error(f"Failed to create page {page_id}: {e}")
            return self._error_page(str(e))

        return None

    def _open_lead(self, lead_id: str):
        page_id = f"lead_detail:{lead_id}"
        if page_id in self._pages:
            del self._pages[page_id]  # Refresh
        self._navigate(page_id)

    def _open_call_analysis(self, call_id: str):
        page_id = f"call_analysis:{call_id}"
        if page_id not in self._pages:
            from app.desktop.calls.calls_page import CallsPage
            record = self.services.call_repo.find_record_by_id(call_id)
            if record:
                page = CallsPage(self.services, record.lead_id)
                page._call_id = call_id
                self._pages[page_id] = page
                self._stack.addWidget(page)
        self._navigate_direct(page_id)

    def _navigate_direct(self, page_id: str):
        if page_id in self._pages:
            for pid, btn in self._nav_buttons.items():
                btn.set_active(False)
            self._stack.setCurrentWidget(self._pages[page_id])
            self._current_page = page_id

    def _open_upload_for_lead(self, lead_id: str):
        if "calls" not in self._pages:
            from app.desktop.calls.calls_page import CallsPage
            page = CallsPage(self.services, lead_id)
            self._pages["calls"] = page
            self._stack.addWidget(page)
        else:
            calls_page = self._pages["calls"]
            if hasattr(calls_page, 'set_lead'):
                calls_page.set_lead(lead_id)
        self._navigate("calls")

    def _access_denied_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Access Denied")
        label.setStyleSheet("color: #E05252; font-size: 18px; font-weight: 600;")
        sub = QLabel("You do not have permission to view this page.")
        sub.setStyleSheet("color: #626975; font-size: 13px;")
        layout.addWidget(label)
        layout.addWidget(sub)
        return w

    def _error_page(self, error: str) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Page Load Error")
        label.setStyleSheet("color: #E05252; font-size: 16px; font-weight: 600;")
        err = QLabel(error)
        err.setStyleSheet("color: #8B929E; font-size: 12px;")
        err.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(err)
        return w

    def _settings_page(self) -> QWidget:
        from app.config import settings
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Settings")
        title.setObjectName("page_title")
        layout.addWidget(title)

        from app.desktop.components.widgets import FieldRow, Panel
        panel = Panel("Configuration")
        panel.add_widget(FieldRow("Gemini Model", settings.gemini_model))
        panel.add_widget(FieldRow("Whisper Model", settings.whisper_model_size))
        panel.add_widget(FieldRow("Database", settings.database_name))
        panel.add_widget(FieldRow("Environment", settings.app_env))
        panel.add_widget(FieldRow("API Key Configured",
            "Yes" if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here" else "No — set GEMINI_API_KEY in .env"))
        layout.addWidget(panel)
        layout.addStretch()
        return w

    def _logout(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Sign Out",
            "Are you sure you want to sign out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.services.current_user = None
            self.close()
