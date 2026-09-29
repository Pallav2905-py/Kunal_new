"""
LeadFlow — Login Window
Professional dark enterprise login screen.
"""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QKeyEvent, QPixmap, QColor
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QFrame, QSizePolicy, QApplication
)

from app.backend.models.domain import LoginRequest, AuthToken
from app.backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class LoginWorker(QObject):
    """Performs login in background thread."""
    success = Signal(object)  # AuthToken
    error = Signal(str)

    def __init__(self, auth_service: AuthService, email: str, password: str):
        super().__init__()
        self.auth_service = auth_service
        self.email = email
        self.password = password

    def run(self):
        try:
            result = self.auth_service.login(
                LoginRequest(email=self.email, password=self.password)
            )
            if result:
                self.success.emit(result)
            else:
                self.error.emit("Invalid email or password. Please try again.")
        except Exception as e:
            self.error.emit(f"Login failed: {str(e)}")


class LoginWindow(QDialog):
    """Professional enterprise login dialog with solid opaque dark design."""

    login_success = Signal(object)  # AuthToken

    def __init__(self, auth_service: AuthService, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginWindow")
        self.auth_service = auth_service
        self._thread: Optional[QThread] = None
        self._worker: Optional[LoginWorker] = None
        self._drag_pos = None

        self.setWindowTitle("LeadFlow — Sign In")
        self.setFixedSize(460, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("QDialog#LoginWindow { background-color: #0F1115; }")
        self.setAutoFillBackground(True)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main card container
        container = QFrame()
        container.setObjectName("login_container")
        container.setFixedSize(420, 480)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        # Header bar with Logo and Close button
        header = QHBoxLayout()
        header.setSpacing(8)

        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(2)

        logo_label = QLabel("LEADFLOW")
        logo_label.setObjectName("login_logo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        tagline = QLabel("AI-Powered CRM & Conversation Intelligence")
        tagline.setObjectName("login_tagline")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(tagline)
        header.addLayout(logo_layout, stretch=1)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("login_close_btn")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Close")
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header)
        layout.addSpacing(28)

        # Welcome text
        welcome = QLabel("Sign in to your workspace")
        welcome.setStyleSheet("color: #E6E9ED; font-size: 14px; font-weight: 600;")
        layout.addWidget(welcome)
        layout.addSpacing(18)

        # Email
        email_label = QLabel("EMAIL")
        email_label.setObjectName("field_label")
        self._email_input = QLineEdit()
        self._email_input.setObjectName("login_input")
        self._email_input.setPlaceholderText("you@company.com")
        self._email_input.setFixedHeight(40)

        layout.addWidget(email_label)
        layout.addSpacing(4)
        layout.addWidget(self._email_input)
        layout.addSpacing(14)

        # Password
        pass_label = QLabel("PASSWORD")
        pass_label.setObjectName("field_label")
        self._pass_input = QLineEdit()
        self._pass_input.setObjectName("login_input")
        self._pass_input.setPlaceholderText("••••••••")
        self._pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._pass_input.setFixedHeight(40)

        layout.addWidget(pass_label)
        layout.addSpacing(4)
        layout.addWidget(self._pass_input)
        layout.addSpacing(16)

        # Remember me
        self._remember = QCheckBox("Keep me signed in")
        self._remember.setStyleSheet("color: #8B929E; font-size: 12px;")
        layout.addWidget(self._remember)
        layout.addSpacing(18)

        # Sign in button
        self._login_btn = QPushButton("Sign In")
        self._login_btn.setObjectName("login_btn")
        self._login_btn.setFixedHeight(42)
        self._login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._login_btn.clicked.connect(self._do_login)
        layout.addWidget(self._login_btn)
        layout.addSpacing(10)

        # Error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #E05252; font-size: 12px; font-weight: 500;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        layout.addStretch()

        # Demo Credentials Hint & Version
        demo_hint = QLabel("Demo: manager@leadflow.local / manager123")
        demo_hint.setStyleSheet("color: #626975; font-size: 11px;")
        demo_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(demo_hint)
        layout.addSpacing(4)

        version = QLabel("v1.0.0  ·  LeadFlow Enterprise Platform")
        version.setStyleSheet("color: #464D58; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        outer.addWidget(container)

        # Connect enter key
        self._pass_input.returnPressed.connect(self._do_login)
        self._email_input.returnPressed.connect(lambda: self._pass_input.setFocus())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def _do_login(self):
        email = self._email_input.text().strip()
        password = self._pass_input.text()

        if not email or not password:
            self._show_error("Please enter both email and password.")
            return

        self._set_loading(True)
        self._hide_error()

        # Run in thread
        self._thread = QThread()
        self._worker = LoginWorker(self.auth_service, email, password)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._worker.success.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_success(self, token: AuthToken):
        self._set_loading(False)
        logger.info(f"Login successful: {token.user.email}")
        self.login_success.emit(token)
        self.accept()

    def _on_error(self, msg: str):
        self._set_loading(False)
        self._show_error(msg)

    def _set_loading(self, loading: bool):
        self._login_btn.setEnabled(not loading)
        self._email_input.setEnabled(not loading)
        self._pass_input.setEnabled(not loading)
        if loading:
            self._login_btn.setText("Signing in...")
        else:
            self._login_btn.setText("Sign In")

    def _show_error(self, msg: str):
        self._error_label.setText(msg)
        self._error_label.show()

    def _hide_error(self):
        self._error_label.hide()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            pass  # Don't close on escape
        else:
            super().keyPressEvent(event)
