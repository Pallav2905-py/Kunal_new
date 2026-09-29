"""
LeadFlow — Application Entry Point
Initializes database, services, shows login, launches main window.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Setup path before local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logging_config import setup_logging
from app.config import settings


def main():
    """Application entry point."""
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting LeadFlow v{settings.app_version}")

    # Ensure upload directory exists
    settings.upload_path.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    app.setApplicationName("LeadFlow")
    app.setOrganizationName("LeadFlow")
    app.setApplicationVersion(settings.app_version)

    # Set application stylesheet & default font
    from app.desktop.styles import LEADFLOW_STYLESHEET
    app.setStyleSheet(LEADFLOW_STYLESHEET)

    font = QFont("Inter", 12)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)

    # Connect to MongoDB
    from app.database.mongodb import MongoDB
    try:
        MongoDB.connect(settings.mongodb_uri, settings.database_name)
        logger.info("MongoDB connected successfully")
    except Exception as e:
        QMessageBox.critical(
            None,
            "Database Connection Failed",
            f"Could not connect to MongoDB at:\n{settings.mongodb_uri}\n\n"
            f"Error: {str(e)}\n\n"
            "Please ensure MongoDB is running and check your .env configuration."
        )
        sys.exit(1)

    # Create services
    from app.desktop.app_services import AppServices
    db = MongoDB.get_db()
    services = AppServices(db)

    # Show login
    from app.desktop.login_window import LoginWindow
    login = LoginWindow(services.auth_service)

    auth_token = None

    def on_login_success(token):
        nonlocal auth_token
        auth_token = token

    login.login_success.connect(on_login_success)
    result = login.exec()

    if result != LoginWindow.DialogCode.Accepted or not auth_token:
        logger.info("Login cancelled or failed. Exiting.")
        MongoDB.disconnect()
        sys.exit(0)

    # Launch main window
    from app.desktop.main_window import MainWindow
    window = MainWindow(services, auth_token)
    window.show()

    logger.info(f"Application started for user: {auth_token.user.email}")

    exit_code = app.exec()

    MongoDB.disconnect()
    logger.info("Application exited cleanly")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
