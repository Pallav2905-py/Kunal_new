"""
LeadFlow — Enterprise Dark Theme QSS
Professional desktop application styling inspired by VS Code / Linear / Attio.
"""

LEADFLOW_STYLESHEET = """
/* ─────────────────────────────────────────────────────────
   ROOT / APPLICATION
───────────────────────────────────────────────────────── */
QMainWindow, QWidget {
    background-color: #0F1115;
    color: #E6E9ED;
    font-family: "Inter", "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QDialog {
    background-color: #191D24;
    color: #E6E9ED;
}

/* ─────────────────────────────────────────────────────────
   SCROLL BARS
───────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #0F1115;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #292E36;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #3A4049;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #0F1115;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #292E36;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover {
    background: #3A4049;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ─────────────────────────────────────────────────────────
   SIDEBAR
───────────────────────────────────────────────────────── */
#sidebar {
    background-color: #14171C;
    border-right: 1px solid #1E2329;
    min-width: 220px;
    max-width: 220px;
}

#sidebar_logo_area {
    background-color: #14171C;
    border-bottom: 1px solid #1E2329;
    padding: 0;
}

#app_name_label {
    color: #E6E9ED;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

#app_subtitle_label {
    color: #626975;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.3px;
}

#nav_section_label {
    color: #626975;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.0px;
    text-transform: uppercase;
    padding: 12px 16px 4px 16px;
}

QPushButton#nav_button {
    background-color: transparent;
    color: #8B929E;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 7px 12px;
    font-size: 13px;
    font-weight: 400;
    margin: 1px 8px;
}

QPushButton#nav_button:hover {
    background-color: #1D2229;
    color: #E6E9ED;
}

QPushButton#nav_button[active="true"] {
    background-color: #1D2229;
    color: #4A9EFF;
    font-weight: 500;
}

#sidebar_user_area {
    background-color: #14171C;
    border-top: 1px solid #1E2329;
    padding: 12px 16px;
}

#user_name_label {
    color: #C9CDD4;
    font-size: 12px;
    font-weight: 500;
}

#user_role_label {
    color: #626975;
    font-size: 11px;
}

#connection_dot {
    color: #2ECC71;
    font-size: 8px;
}

QPushButton#logout_button {
    background-color: transparent;
    color: #626975;
    border: none;
    font-size: 11px;
    padding: 2px 0;
    text-align: left;
}

QPushButton#logout_button:hover {
    color: #E05252;
}

/* ─────────────────────────────────────────────────────────
   TOP BAR
───────────────────────────────────────────────────────── */
#topbar {
    background-color: #161A20;
    border-bottom: 1px solid #1E2329;
    min-height: 44px;
    max-height: 44px;
}

#topbar_title {
    color: #E6E9ED;
    font-size: 13px;
    font-weight: 500;
}

#topbar_breadcrumb {
    color: #626975;
    font-size: 12px;
}

/* ─────────────────────────────────────────────────────────
   SEARCH
───────────────────────────────────────────────────────── */
QLineEdit#search_input {
    background-color: #1D2229;
    border: 1px solid #292E36;
    border-radius: 6px;
    color: #E6E9ED;
    padding: 5px 10px 5px 28px;
    font-size: 12px;
    selection-background-color: #2D5FA8;
}

QLineEdit#search_input:focus {
    border-color: #3A5FA0;
    background-color: #1D2229;
}

QLineEdit#search_input::placeholder {
    color: #626975;
}

/* ─────────────────────────────────────────────────────────
   MAIN CONTENT AREA
───────────────────────────────────────────────────────── */
#content_area {
    background-color: #0F1115;
}

#page_header {
    background-color: #0F1115;
    border-bottom: 1px solid #1A1E25;
    padding: 16px 20px 12px 20px;
}

#page_title {
    color: #E6E9ED;
    font-size: 18px;
    font-weight: 600;
}

#page_subtitle {
    color: #626975;
    font-size: 12px;
}

/* ─────────────────────────────────────────────────────────
   PANELS / CARDS
───────────────────────────────────────────────────────── */
#panel {
    background-color: #191D24;
    border: 1px solid #1E2329;
    border-radius: 8px;
}

#panel_header {
    background-color: #191D24;
    border-bottom: 1px solid #1E2329;
    padding: 10px 16px;
    border-radius: 8px 8px 0 0;
}

#panel_title {
    color: #C9CDD4;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* KPI cards — no rainbow colors */
#kpi_card {
    background-color: #191D24;
    border: 1px solid #1E2329;
    border-radius: 8px;
    padding: 16px;
}

#kpi_value {
    color: #E6E9ED;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

#kpi_label {
    color: #626975;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

#kpi_delta {
    color: #2ECC71;
    font-size: 11px;
}

#kpi_delta_neg {
    color: #E05252;
    font-size: 11px;
}

/* ─────────────────────────────────────────────────────────
   DATA TABLES
───────────────────────────────────────────────────────── */
QTableWidget, QTableView {
    background-color: #191D24;
    gridline-color: #1A1E25;
    border: none;
    selection-background-color: #1E3A5F;
    selection-color: #E6E9ED;
    alternate-background-color: #191D24;
    font-size: 12px;
    color: #C9CDD4;
}

QTableWidget::item, QTableView::item {
    padding: 6px 12px;
    border-bottom: 1px solid #1A1E25;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #1D2229;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #1E3A5F;
    color: #E6E9ED;
}

QHeaderView::section {
    background-color: #14171C;
    color: #8B929E;
    padding: 6px 12px;
    border: none;
    border-bottom: 1px solid #1E2329;
    border-right: 1px solid #1A1E25;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background-color: #1D2229;
    color: #C9CDD4;
}

/* ─────────────────────────────────────────────────────────
   BUTTONS
───────────────────────────────────────────────────────── */
QPushButton {
    background-color: #1D2229;
    color: #C9CDD4;
    border: 1px solid #292E36;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #242A33;
    color: #E6E9ED;
    border-color: #3A4049;
}

QPushButton:pressed {
    background-color: #1A1F27;
}

QPushButton#btn_primary {
    background-color: #2B5FA8;
    color: #FFFFFF;
    border: 1px solid #3A6FBB;
}

QPushButton#btn_primary:hover {
    background-color: #3569B8;
    border-color: #4A7FCB;
}

QPushButton#btn_primary:pressed {
    background-color: #214F98;
}

QPushButton#btn_danger {
    background-color: #5A1F1F;
    color: #E88;
    border: 1px solid #7A2F2F;
}

QPushButton#btn_danger:hover {
    background-color: #6A2525;
    color: #F99;
}

QPushButton#btn_success {
    background-color: #1A4A2E;
    color: #2ECC71;
    border: 1px solid #2A6A3E;
}

QPushButton#btn_success:hover {
    background-color: #1E5A36;
}

QPushButton:disabled {
    background-color: #14171C;
    color: #464D58;
    border-color: #1E2329;
}

/* Icon-only buttons */
QPushButton#icon_btn {
    background-color: transparent;
    border: none;
    color: #626975;
    padding: 4px;
    border-radius: 4px;
}

QPushButton#icon_btn:hover {
    background-color: #1D2229;
    color: #C9CDD4;
}

/* ─────────────────────────────────────────────────────────
   INPUT FIELDS
───────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1D2229;
    color: #E6E9ED;
    border: 1px solid #292E36;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: #2D5FA8;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #3A5FA0;
}

QLineEdit:read-only, QTextEdit:read-only {
    background-color: #14171C;
    color: #8B929E;
}

/* ─────────────────────────────────────────────────────────
   COMBO BOXES
───────────────────────────────────────────────────────── */
QComboBox {
    background-color: #1D2229;
    color: #E6E9ED;
    border: 1px solid #292E36;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}

QComboBox:hover {
    border-color: #3A4049;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 20px;
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #191D24;
    color: #E6E9ED;
    border: 1px solid #292E36;
    selection-background-color: #2B5FA8;
}

/* ─────────────────────────────────────────────────────────
   LABELS
───────────────────────────────────────────────────────── */
QLabel {
    color: #C9CDD4;
}

QLabel#section_title {
    color: #E6E9ED;
    font-size: 14px;
    font-weight: 600;
}

QLabel#field_label {
    color: #626975;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel#field_value {
    color: #C9CDD4;
    font-size: 13px;
}

QLabel#muted {
    color: #626975;
    font-size: 11px;
}

/* ─────────────────────────────────────────────────────────
   TABS
───────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background-color: #0F1115;
}

QTabBar::tab {
    background-color: transparent;
    color: #626975;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}

QTabBar::tab:hover {
    color: #C9CDD4;
}

QTabBar::tab:selected {
    color: #4A9EFF;
    border-bottom: 2px solid #4A9EFF;
}

QTabBar {
    background-color: #161A20;
    border-bottom: 1px solid #1E2329;
}

/* ─────────────────────────────────────────────────────────
   STATUS BADGES
───────────────────────────────────────────────────────── */
QLabel#badge_new {
    background-color: #1D2229;
    color: #8B929E;
    border: 1px solid #292E36;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_interested {
    background-color: #162A3E;
    color: #4A9EFF;
    border: 1px solid #1E3A5F;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_converted {
    background-color: #132A1E;
    color: #2ECC71;
    border: 1px solid #1A4A2E;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_lost {
    background-color: #2A1515;
    color: #E05252;
    border: 1px solid #4A2020;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_high {
    background-color: #2A1F0E;
    color: #E8A845;
    border: 1px solid #4A3520;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_medium {
    background-color: #1A1F14;
    color: #9ECC5A;
    border: 1px solid #2A3A18;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_low {
    background-color: #1D2229;
    color: #626975;
    border: 1px solid #292E36;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_positive {
    background-color: #132A1E;
    color: #2ECC71;
    border: 1px solid #1A4A2E;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_negative {
    background-color: #2A1515;
    color: #E05252;
    border: 1px solid #4A2020;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_neutral {
    background-color: #1D2229;
    color: #8B929E;
    border: 1px solid #292E36;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

QLabel#badge_mixed {
    background-color: #1F1A2A;
    color: #9B7FE8;
    border: 1px solid #3A2A5A;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

/* ─────────────────────────────────────────────────────────
   STATUS BAR
───────────────────────────────────────────────────────── */
QStatusBar {
    background-color: #14171C;
    color: #626975;
    border-top: 1px solid #1E2329;
    font-size: 11px;
}

/* ─────────────────────────────────────────────────────────
   PROGRESS BAR
───────────────────────────────────────────────────────── */
QProgressBar {
    background-color: #1D2229;
    border: none;
    border-radius: 3px;
    height: 4px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #2B5FA8;
    border-radius: 3px;
}

/* ─────────────────────────────────────────────────────────
   MESSAGE BOX
───────────────────────────────────────────────────────── */
QMessageBox {
    background-color: #191D24;
    color: #E6E9ED;
}

QMessageBox QLabel {
    color: #C9CDD4;
    font-size: 13px;
}

/* ─────────────────────────────────────────────────────────
   SPLITTER
───────────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #1E2329;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

/* ─────────────────────────────────────────────────────────
   TOOL TIPS
───────────────────────────────────────────────────────── */
QToolTip {
    background-color: #1D2229;
    color: #E6E9ED;
    border: 1px solid #292E36;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

/* ─────────────────────────────────────────────────────────
   CHECKBOX
───────────────────────────────────────────────────────── */
QCheckBox {
    color: #C9CDD4;
    font-size: 12px;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #3A4049;
    border-radius: 3px;
    background-color: #1D2229;
}

QCheckBox::indicator:checked {
    background-color: #2B5FA8;
    border-color: #3A6FBB;
}

/* ─────────────────────────────────────────────────────────
   SEPARATOR
───────────────────────────────────────────────────────── */
QFrame[frameShape="4"] {  /* HLine */
    color: #1E2329;
    border: none;
    border-top: 1px solid #1E2329;
    max-height: 1px;
}

/* ─────────────────────────────────────────────────────────
   LOGIN WINDOW
───────────────────────────────────────────────────────── */
QDialog#LoginWindow {
    background-color: #0F1115;
}

#login_container {
    background-color: #181C23;
    border: 1px solid #282E38;
    border-radius: 12px;
}

#login_close_btn {
    background: transparent;
    color: #8B929E;
    border: none;
    font-size: 16px;
    font-weight: bold;
    border-radius: 4px;
}

#login_close_btn:hover {
    background-color: #282E38;
    color: #FFFFFF;
}

#login_logo {
    color: #E6E9ED;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
}

#login_tagline {
    color: #626975;
    font-size: 12px;
}

QLineEdit#login_input {
    background-color: #14171C;
    border: 1px solid #292E36;
    border-radius: 6px;
    color: #E6E9ED;
    padding: 9px 12px;
    font-size: 13px;
}

QLineEdit#login_input:focus {
    border-color: #3A5FA0;
}

QPushButton#login_btn {
    background-color: #2B5FA8;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#login_btn:hover {
    background-color: #3569B8;
}

QPushButton#login_btn:pressed {
    background-color: #214F98;
}

/* ─────────────────────────────────────────────────────────
   SCORE BAR
───────────────────────────────────────────────────────── */
#score_bar_bg {
    background-color: #1D2229;
    border-radius: 2px;
}

#score_bar_fill_high {
    background-color: #2ECC71;
    border-radius: 2px;
}

#score_bar_fill_medium {
    background-color: #E8A845;
    border-radius: 2px;
}

#score_bar_fill_low {
    background-color: #E05252;
    border-radius: 2px;
}

/* ─────────────────────────────────────────────────────────
   PIPELINE STEPS
───────────────────────────────────────────────────────── */
#pipeline_step_pending {
    color: #626975;
}

#pipeline_step_active {
    color: #4A9EFF;
}

#pipeline_step_done {
    color: #2ECC71;
}

#pipeline_step_error {
    color: #E05252;
}

/* ─────────────────────────────────────────────────────────
   AGENT PANEL
───────────────────────────────────────────────────────── */
#agent_card {
    background-color: #191D24;
    border: 1px solid #1E2329;
    border-radius: 8px;
    padding: 12px;
}

#agent_name {
    color: #C9CDD4;
    font-size: 12px;
    font-weight: 600;
}

#agent_status_ok {
    color: #2ECC71;
}

#agent_status_fail {
    color: #E05252;
}

#agent_detail {
    color: #626975;
    font-size: 11px;
}

/* ─────────────────────────────────────────────────────────
   TRANSCRIPT VIEWER
───────────────────────────────────────────────────────── */
#transcript_box {
    background-color: #14171C;
    border: 1px solid #1E2329;
    border-radius: 6px;
    color: #9EA5B0;
    font-size: 12px;
    line-height: 1.6;
    padding: 12px;
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
}

/* ─────────────────────────────────────────────────────────
   AI QUERY BOX
───────────────────────────────────────────────────────── */
#query_input {
    background-color: #1D2229;
    border: 1px solid #292E36;
    border-radius: 8px;
    color: #E6E9ED;
    padding: 10px 14px;
    font-size: 13px;
}

#query_input:focus {
    border-color: #3A5FA0;
}

#query_response {
    background-color: #14171C;
    border: 1px solid #1E2329;
    border-radius: 6px;
    color: #C9CDD4;
    font-size: 13px;
    line-height: 1.6;
    padding: 12px;
}
"""


def get_status_color(status: str) -> str:
    """Return text color for a lead status."""
    colors = {
        "new": "#8B929E",
        "contacted": "#4A9EFF",
        "interested": "#2ECC71",
        "follow_up": "#E8A845",
        "negotiation": "#9B7FE8",
        "converted": "#2ECC71",
        "lost": "#E05252",
    }
    return colors.get(status.lower(), "#8B929E")


def get_priority_color(priority: str) -> str:
    """Return text color for a lead priority."""
    colors = {
        "high": "#E8A845",
        "medium": "#9ECC5A",
        "low": "#626975",
    }
    return colors.get(priority.lower(), "#8B929E")


def get_sentiment_color(sentiment: str) -> str:
    """Return text color for sentiment."""
    colors = {
        "POSITIVE": "#2ECC71",
        "NEGATIVE": "#E05252",
        "NEUTRAL": "#8B929E",
        "MIXED": "#9B7FE8",
    }
    return colors.get(sentiment.upper(), "#8B929E")


def score_to_color(score: int) -> str:
    if score >= 70:
        return "#2ECC71"
    elif score >= 40:
        return "#E8A845"
    else:
        return "#E05252"
