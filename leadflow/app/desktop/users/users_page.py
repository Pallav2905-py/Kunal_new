"""
LeadFlow — Users Page (Admin only)
"""

from __future__ import annotations
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidgetItem, QDialog,
    QLineEdit, QComboBox, QFormLayout, QMessageBox,
)

from app.desktop.app_services import AppServices
from app.desktop.components.widgets import DataTable
from app.backend.models.domain import UserCreate, UserRole

logger = logging.getLogger(__name__)

ROLE_DISPLAY = {
    UserRole.ADMIN: "Admin",
    UserRole.SALES_MANAGER: "Sales Manager",
    UserRole.SALES_EXECUTIVE: "Sales Executive",
    UserRole.SUPPORT: "Support",
}


class AddUserDialog(QDialog):
    user_created = Signal()

    def __init__(self, services: AppServices, parent=None):
        super().__init__(parent)
        self.services = services
        self.setWindowTitle("Add User")
        self.setFixedSize(400, 340)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Add New User")
        title.setStyleSheet("font-size: 15px; font-weight: 600; color: #E6E9ED;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._name = QLineEdit()
        self._name.setFixedHeight(32)
        self._email = QLineEdit()
        self._email.setFixedHeight(32)
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setFixedHeight(32)
        self._role = QComboBox()
        self._role.setFixedHeight(32)
        self._role.addItems([r.value for r in UserRole])

        form.addRow("Name:", self._name)
        form.addRow("Email:", self._email)
        form.addRow("Password:", self._password)
        form.addRow("Role:", self._role)
        layout.addLayout(form)

        self._error = QLabel("")
        self._error.setStyleSheet("color: #E05252; font-size: 12px;")
        self._error.hide()
        layout.addWidget(self._error)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        create = QPushButton("Create User")
        create.setObjectName("btn_primary")
        create.clicked.connect(self._create)
        btn_row.addWidget(cancel)
        btn_row.addWidget(create)
        layout.addLayout(btn_row)

    def _create(self):
        try:
            data = UserCreate(
                name=self._name.text().strip(),
                email=self._email.text().strip(),
                password=self._password.text(),
                role=UserRole(self._role.currentText()),
            )
            self.services.auth_service.create_user(data)
            self.user_created.emit()
            self.accept()
        except Exception as e:
            self._error.setText(str(e))
            self._error.show()


class UsersPage(QWidget):
    def __init__(self, services: AppServices, parent=None):
        super().__init__(parent)
        self.services = services
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("page_header")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Users")
        title.setObjectName("page_title")
        self._count = QLabel("")
        self._count.setStyleSheet("color: #626975; font-size: 12px; margin-left: 12px; margin-top: 3px;")

        add_btn = QPushButton("+ Add User")
        add_btn.setObjectName("btn_primary")
        add_btn.setFixedHeight(28)
        add_btn.clicked.connect(self._add_user)

        h_layout.addWidget(title)
        h_layout.addWidget(self._count)
        h_layout.addStretch()
        h_layout.addWidget(add_btn)
        layout.addWidget(header)

        self._table = DataTable([
            "Name", "Email", "Role", "Status", "Last Login", "Created"
        ])
        layout.addWidget(self._table, 1)

    def _load(self):
        users = self.services.user_repo.list_all()
        self._count.setText(f"{len(users)} users")
        self._table.setRowCount(0)
        self._table.setSortingEnabled(False)

        ROLE_COLORS = {
            "admin": "#E8A845",
            "sales_manager": "#4A9EFF",
            "sales_executive": "#2ECC71",
            "support": "#9B7FE8",
        }

        for u in users:
            row = self._table.rowCount()
            self._table.insertRow(row)

            color = ROLE_COLORS.get(u.role.value, "#8B929E")
            role_item = QTableWidgetItem(ROLE_DISPLAY.get(u.role, u.role.value))
            role_item.setForeground(QColor(color))

            status_item = QTableWidgetItem("Active" if u.is_active else "Inactive")
            status_item.setForeground(QColor("#2ECC71" if u.is_active else "#E05252"))

            last_login = u.last_login.strftime("%b %d, %Y") if u.last_login else "Never"
            created = u.created_at.strftime("%b %d, %Y") if u.created_at else "—"

            self._table.setItem(row, 0, self._item(u.name))
            self._table.setItem(row, 1, self._item(u.email))
            self._table.setItem(row, 2, role_item)
            self._table.setItem(row, 3, status_item)
            self._table.setItem(row, 4, self._item(last_login))
            self._table.setItem(row, 5, self._item(created))

        self._table.setSortingEnabled(True)

    def _item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor("#C9CDD4"))
        return item

    def _add_user(self):
        dialog = AddUserDialog(self.services, self)
        dialog.user_created.connect(self._load)
        dialog.exec()

    def refresh(self):
        self._load()
