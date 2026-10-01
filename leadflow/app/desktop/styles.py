"""
LeadFlow — Professional Desktop Workspace Theme
Surface layer system:
  L0 #080C12  application chrome (deepest)
  L1 #0D1219  activity rail + secondary sidebar chrome
  L2 #111822  workspace background
  L3 #161E2B  panels / cards (elevated)
  L4 #1A2334  panel headers / tab headers
  L5 #1E2940  hover
  L6 #1C3258  active / selected
"""

LEADFLOW_STYLESHEET = """
/* BASE */
QMainWindow, QWidget {
    background-color: #111822;
    color: #DCE4EF;
    font-family: "Inter", "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
}

QDialog {
    background-color: #111822;
    color: #DCE4EF;
}

/* SCROLLBARS */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #273347;
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #2E3D55; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #273347;
    border-radius: 3px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #2E3D55; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ACTIVITY RAIL */
#activity_rail {
    background-color: #0D1219;
    border-right: 1px solid #18202F;
}
#rail_logo {
    color: #3D7EFF;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
QPushButton#rail_btn {
    background-color: transparent;
    color: #3D4E65;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    padding: 0;
    margin: 0 6px;
}
QPushButton#rail_btn:hover {
    background-color: #161E2B;
    color: #8A9AB0;
}
QPushButton#rail_btn[active="true"] {
    background-color: #1C3258;
    color: #3D7EFF;
}
#rail_separator {
    background-color: #18202F;
    max-height: 1px;
    min-height: 1px;
    margin: 0 10px;
}

/* SECONDARY SIDEBAR */
#secondary_sidebar {
    background-color: #0D1219;
    border-right: 1px solid #18202F;
}
#sidebar_section_header {
    color: #3D4E65;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.8px;
    padding: 12px 12px 4px 12px;
}
QPushButton#sidebar_nav_btn {
    background-color: transparent;
    color: #8A9AB0;
    border: none;
    border-left: 2px solid transparent;
    border-radius: 0;
    text-align: left;
    padding: 5px 12px;
    font-size: 12px;
    margin: 0;
}
QPushButton#sidebar_nav_btn:hover {
    background-color: #111822;
    color: #C4D0DF;
}
QPushButton#sidebar_nav_btn[active="true"] {
    background-color: #131E30;
    color: #3D7EFF;
    font-weight: 500;
    border-left: 2px solid #3D7EFF;
}
QLineEdit#sidebar_search {
    background-color: #111822;
    border: 1px solid #1F2B3E;
    border-radius: 3px;
    color: #C4D0DF;
    padding: 4px 8px;
    font-size: 11px;
}
QLineEdit#sidebar_search:focus {
    border-color: #3D7EFF;
}
#sidebar_stat_num {
    color: #DCE4EF;
    font-size: 14px;
    font-weight: 600;
}
#sidebar_stat_label {
    color: #3D4E65;
    font-size: 10px;
}

/* TOP APPLICATION BAR */
#topbar {
    background-color: #0D1219;
    border-bottom: 1px solid #18202F;
    min-height: 36px;
    max-height: 36px;
}
#topbar_logo {
    color: #3D7EFF;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}
#topbar_section {
    color: #8A9AB0;
    font-size: 12px;
    font-weight: 500;
}
#topbar_user_badge {
    color: #8A9AB0;
    font-size: 11px;
}
QPushButton#topbar_btn {
    background-color: transparent;
    color: #3D4E65;
    border: none;
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 11px;
}
QPushButton#topbar_btn:hover {
    background-color: #161E2B;
    color: #8A9AB0;
}
QPushButton#topbar_search_trigger {
    background-color: #161E2B;
    border: 1px solid #1F2B3E;
    border-radius: 3px;
    color: #3D4E65;
    padding: 3px 10px;
    font-size: 11px;
    text-align: left;
}
QPushButton#topbar_search_trigger:hover {
    border-color: #273347;
    color: #8A9AB0;
}

/* WORKSPACE */
#workspace_area {
    background-color: #111822;
}
#workspace_tab_bar {
    background-color: #0D1219;
    border-bottom: 1px solid #18202F;
    min-height: 32px;
    max-height: 32px;
}
QPushButton#workspace_tab {
    background-color: transparent;
    color: #3D4E65;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    padding: 0 12px;
    font-size: 11px;
    min-height: 32px;
    max-height: 32px;
}
QPushButton#workspace_tab:hover {
    background-color: #111822;
    color: #8A9AB0;
}
QPushButton#workspace_tab[active="true"] {
    background-color: #111822;
    color: #DCE4EF;
    border-bottom: 2px solid #3D7EFF;
    font-weight: 500;
}
QPushButton#tab_close_btn {
    background-color: transparent;
    color: transparent;
    border: none;
    border-radius: 2px;
    padding: 0;
    font-size: 10px;
    max-width: 14px;
    min-width: 14px;
    max-height: 14px;
    min-height: 14px;
}
QPushButton#tab_close_btn:hover {
    background-color: #273347;
    color: #DCE4EF;
}
QPushButton#tab_add_btn {
    background-color: transparent;
    color: #3D4E65;
    border: none;
    border-radius: 3px;
    padding: 0 8px;
    font-size: 14px;
    min-height: 32px;
    max-height: 32px;
}
QPushButton#tab_add_btn:hover {
    background-color: #161E2B;
    color: #8A9AB0;
}

/* INSPECTOR PANEL */
#inspector_panel {
    background-color: #0D1219;
    border-left: 1px solid #18202F;
}
#inspector_header {
    background-color: #0D1219;
    border-bottom: 1px solid #18202F;
    min-height: 32px;
    max-height: 32px;
}
#inspector_title {
    color: #3D4E65;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.7px;
}
QPushButton#inspector_toggle {
    background-color: transparent;
    border: none;
    color: #3D4E65;
    padding: 0 4px;
    font-size: 12px;
    border-radius: 2px;
}
QPushButton#inspector_toggle:hover {
    background-color: #161E2B;
    color: #8A9AB0;
}
#inspector_section_title {
    color: #3D4E65;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.6px;
    padding: 8px 12px 3px 12px;
}
#inspector_field_label { color: #3D4E65; font-size: 10px; font-weight: 500; }
#inspector_field_value { color: #C4D0DF; font-size: 11px; }
#inspector_placeholder { color: #273347; font-size: 12px; }

/* BOTTOM PANEL */
#bottom_panel {
    background-color: #0D1219;
    border-top: 1px solid #18202F;
}
#bottom_panel_header {
    background-color: #0D1219;
    border-bottom: 1px solid #18202F;
    min-height: 28px;
    max-height: 28px;
}
QPushButton#bottom_tab_btn {
    background-color: transparent;
    color: #3D4E65;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    padding: 0 12px;
    font-size: 11px;
    min-height: 28px;
    max-height: 28px;
}
QPushButton#bottom_tab_btn:hover { color: #8A9AB0; }
QPushButton#bottom_tab_btn[active="true"] {
    color: #C4D0DF;
    border-bottom: 2px solid #3D7EFF;
}
QPushButton#panel_collapse_btn {
    background-color: transparent;
    color: #3D4E65;
    border: none;
    border-radius: 2px;
    padding: 0 6px;
    font-size: 11px;
    min-height: 28px;
}
QPushButton#panel_collapse_btn:hover {
    background-color: #161E2B;
    color: #8A9AB0;
}
#bottom_output {
    background-color: #080C12;
    border: none;
    color: #5A6E88;
    font-size: 11px;
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    padding: 8px;
}

/* STATUS BAR */
#app_status_bar {
    background-color: #080C12;
    border-top: 1px solid #18202F;
    min-height: 22px;
    max-height: 22px;
}
#status_item { color: #3D4E65; font-size: 10px; padding: 0 8px; }
#status_item_accent { color: #3D7EFF; font-size: 10px; padding: 0 8px; }
#status_ok_dot { color: #22C55E; font-size: 8px; }
#status_error_dot { color: #EF4444; font-size: 8px; }
QPushButton#status_btn {
    background-color: transparent; color: #3D4E65; border: none;
    font-size: 10px; padding: 0 8px; min-height: 22px; border-radius: 0;
}
QPushButton#status_btn:hover { background-color: #161E2B; color: #8A9AB0; }

/* COMMAND PALETTE */
#command_palette {
    background-color: #161E2B;
    border: 1px solid #273347;
    border-radius: 6px;
}
QLineEdit#palette_input {
    background-color: transparent;
    border: none;
    border-bottom: 1px solid #1F2B3E;
    border-radius: 0;
    color: #DCE4EF;
    padding: 10px 14px;
    font-size: 13px;
}
QLineEdit#palette_input:focus { border-bottom: 1px solid #3D7EFF; }
QPushButton#palette_item {
    background-color: transparent;
    color: #8A9AB0;
    border: none;
    border-radius: 3px;
    text-align: left;
    padding: 7px 12px;
    font-size: 12px;
    margin: 1px 4px;
}
QPushButton#palette_item:hover { background-color: #1A2334; color: #DCE4EF; }
QPushButton#palette_item[active="true"] { background-color: #1C3258; color: #DCE4EF; }
#palette_empty { color: #273347; font-size: 12px; }

/* SPLITTER HANDLES */
QSplitter::handle { background-color: #18202F; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }
QSplitter::handle:hover { background-color: #3D7EFF; }

/* PAGE CONTENT */
#content_area { background-color: #111822; }
#page_header {
    background-color: #111822;
    border-bottom: 1px solid #18202F;
    padding: 0 16px;
}
#page_title { color: #DCE4EF; font-size: 14px; font-weight: 600; }
#page_subtitle { color: #3D4E65; font-size: 11px; }

/* PANELS */
#panel {
    background-color: #161E2B;
    border: 1px solid #1F2B3E;
    border-radius: 4px;
}
#panel_header {
    background-color: #1A2334;
    border-bottom: 1px solid #1F2B3E;
    padding: 0 12px;
    border-radius: 4px 4px 0 0;
    min-height: 30px;
    max-height: 30px;
}
#panel_title {
    color: #3D4E65;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
#kpi_card {
    background-color: #161E2B;
    border: 1px solid #1F2B3E;
    border-radius: 4px;
    padding: 12px 14px;
}
#kpi_value { color: #DCE4EF; font-size: 22px; font-weight: 700; }
#kpi_label { color: #3D4E65; font-size: 10px; font-weight: 600; letter-spacing: 0.6px; }
#kpi_delta { color: #22C55E; font-size: 10px; }
#kpi_delta_neg { color: #EF4444; font-size: 10px; }

/* DATA TABLES */
QTableWidget, QTableView {
    background-color: #161E2B;
    gridline-color: transparent;
    border: none;
    selection-background-color: #1C3258;
    selection-color: #DCE4EF;
    alternate-background-color: #161E2B;
    font-size: 11px;
    color: #C4D0DF;
}
QTableWidget::item, QTableView::item {
    padding: 4px 10px;
    border-bottom: 1px solid #18202F;
}
QTableWidget::item:hover, QTableView::item:hover { background-color: #1A2334; }
QTableWidget::item:selected, QTableView::item:selected {
    background-color: #1C3258; color: #DCE4EF;
}
QHeaderView::section {
    background-color: #0D1219;
    color: #3D4E65;
    padding: 4px 10px;
    border: none;
    border-bottom: 1px solid #18202F;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QHeaderView::section:hover { background-color: #111822; color: #8A9AB0; }

/* BUTTONS */
QPushButton {
    background-color: #1A2334;
    color: #C4D0DF;
    border: 1px solid #273347;
    border-radius: 3px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 500;
}
QPushButton:hover { background-color: #1E2940; color: #DCE4EF; border-color: #2E3D55; }
QPushButton:pressed { background-color: #161E2B; }
QPushButton#btn_primary { background-color: #1A3E7A; color: #BEDAFF; border: 1px solid #2452A0; }
QPushButton#btn_primary:hover { background-color: #1E4A8E; color: #D4E8FF; }
QPushButton#btn_primary:pressed { background-color: #153268; }
QPushButton#btn_danger { background-color: #3A1414; color: #FCA5A5; border: 1px solid #571E1E; }
QPushButton#btn_danger:hover { background-color: #461818; color: #FECACA; }
QPushButton#btn_success { background-color: #0F3020; color: #6EE7B7; border: 1px solid #185A38; }
QPushButton#btn_success:hover { background-color: #133A26; }
QPushButton:disabled { background-color: #0D1219; color: #273347; border-color: #18202F; }
QPushButton#icon_btn {
    background-color: transparent; border: none; color: #3D4E65; padding: 2px; border-radius: 2px;
}
QPushButton#icon_btn:hover { background-color: #161E2B; color: #C4D0DF; }

/* INPUTS */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #161E2B; color: #DCE4EF;
    border: 1px solid #273347; border-radius: 3px;
    padding: 4px 8px; font-size: 12px;
    selection-background-color: #1C3258;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border-color: #3D7EFF; }
QLineEdit:read-only, QTextEdit:read-only { background-color: #0D1219; color: #3D4E65; }

/* COMBO BOXES */
QComboBox {
    background-color: #161E2B; color: #DCE4EF;
    border: 1px solid #273347; border-radius: 3px;
    padding: 3px 8px; font-size: 11px;
}
QComboBox:hover { border-color: #2E3D55; }
QComboBox:focus { border-color: #3D7EFF; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: right center; width: 16px; border: none; }
QComboBox QAbstractItemView {
    background-color: #161E2B; color: #DCE4EF;
    border: 1px solid #273347;
    selection-background-color: #1A3E7A; selection-color: #DCE4EF; outline: none;
}

/* LABELS */
QLabel { color: #C4D0DF; }
QLabel#section_title { color: #DCE4EF; font-size: 13px; font-weight: 600; }
QLabel#field_label { color: #3D4E65; font-size: 10px; font-weight: 500; letter-spacing: 0.3px; }
QLabel#field_value { color: #C4D0DF; font-size: 12px; }
QLabel#muted { color: #3D4E65; font-size: 10px; }

/* TABS (internal, e.g. lead detail) */
QTabWidget::pane { border: none; background-color: #111822; }
QTabBar::tab {
    background-color: transparent; color: #3D4E65;
    border: none; border-bottom: 2px solid transparent;
    padding: 6px 14px; font-size: 11px; font-weight: 500;
}
QTabBar::tab:hover { color: #8A9AB0; }
QTabBar::tab:selected { color: #DCE4EF; border-bottom: 2px solid #3D7EFF; }
QTabBar { background-color: #0D1219; border-bottom: 1px solid #18202F; }

/* BADGES */
QLabel#badge_new { background-color: #1A2334; color: #8A9AB0; border: 1px solid #273347; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_interested { background-color: #0B2040; color: #60A5FA; border: 1px solid #163A6B; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_converted { background-color: #082B1A; color: #34D399; border: 1px solid #0F5232; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_lost { background-color: #2A0A0A; color: #F87171; border: 1px solid #4A1414; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_high { background-color: #2B1A06; color: #FBBF24; border: 1px solid #4A2D08; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_medium { background-color: #101E0A; color: #86EFAC; border: 1px solid #1A3A10; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_low { background-color: #1A2334; color: #3D4E65; border: 1px solid #273347; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_positive { background-color: #082B1A; color: #34D399; border: 1px solid #0F5232; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_negative { background-color: #2A0A0A; color: #F87171; border: 1px solid #4A1414; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_neutral { background-color: #1A2334; color: #8A9AB0; border: 1px solid #273347; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }
QLabel#badge_mixed { background-color: #180E28; color: #A78BFA; border: 1px solid #30185A; border-radius: 2px; padding: 0 5px; font-size: 9px; font-weight: 700; }

/* MISC */
QStatusBar { background-color: #080C12; color: #3D4E65; border-top: 1px solid #18202F; font-size: 10px; }
QProgressBar { background-color: #1A2334; border: none; border-radius: 2px; height: 3px; color: transparent; }
QProgressBar::chunk { background-color: #3D7EFF; border-radius: 2px; }
QMessageBox { background-color: #161E2B; color: #DCE4EF; }
QMessageBox QLabel { color: #C4D0DF; font-size: 12px; }
QToolTip { background-color: #1A2334; color: #DCE4EF; border: 1px solid #273347; border-radius: 3px; padding: 4px 8px; font-size: 11px; }
QCheckBox { color: #C4D0DF; font-size: 11px; spacing: 5px; }
QCheckBox::indicator { width: 12px; height: 12px; border: 1px solid #2E3D55; border-radius: 2px; background-color: #161E2B; }
QCheckBox::indicator:checked { background-color: #1A3E7A; border-color: #2452A0; }
QFrame[frameShape="4"] { color: #18202F; border: none; border-top: 1px solid #18202F; max-height: 1px; }

/* SEARCH INPUT */
QLineEdit#search_input {
    background-color: #161E2B; border: 1px solid #1F2B3E; border-radius: 3px;
    color: #DCE4EF; padding: 3px 8px 3px 24px; font-size: 11px;
}
QLineEdit#search_input:focus { border-color: #3D7EFF; }

/* SCORE BAR */
#score_bar_bg { background-color: #1A2334; border-radius: 2px; }
#score_bar_fill_high { background-color: #22C55E; border-radius: 2px; }
#score_bar_fill_medium { background-color: #FBBF24; border-radius: 2px; }
#score_bar_fill_low { background-color: #EF4444; border-radius: 2px; }

#pipeline_step_pending { color: #3D4E65; }
#pipeline_step_active { color: #3D7EFF; }
#pipeline_step_done { color: #22C55E; }
#pipeline_step_error { color: #EF4444; }

#agent_card { background-color: #161E2B; border: 1px solid #1F2B3E; border-radius: 4px; padding: 10px; }
#agent_name { color: #C4D0DF; font-size: 11px; font-weight: 600; }
#agent_status_ok { color: #22C55E; }
#agent_status_fail { color: #EF4444; }
#agent_detail { color: #3D4E65; font-size: 10px; }

#transcript_box {
    background-color: #080C12; border: 1px solid #18202F; border-radius: 3px;
    color: #8A9AB0; font-size: 11px; padding: 10px;
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
}

#query_input { background-color: #161E2B; border: 1px solid #273347; border-radius: 3px; color: #DCE4EF; padding: 8px 12px; font-size: 12px; }
#query_input:focus { border-color: #3D7EFF; }
#query_response { background-color: #0D1219; border: 1px solid #18202F; border-radius: 3px; color: #C4D0DF; font-size: 12px; padding: 10px; }

/* LOGIN WINDOW */
QDialog#LoginWindow { background-color: #080C12; }
#login_container { background-color: #111822; border: 1px solid #273347; border-radius: 6px; }
#login_close_btn { background: transparent; color: #3D4E65; border: none; font-size: 14px; border-radius: 2px; }
#login_close_btn:hover { background-color: #1A2334; color: #DCE4EF; }
#login_logo { color: #DCE4EF; font-size: 18px; font-weight: 700; letter-spacing: 0.5px; }
#login_tagline { color: #3D4E65; font-size: 11px; }
QLineEdit#login_input { background-color: #0D1219; border: 1px solid #273347; border-radius: 3px; color: #DCE4EF; padding: 8px 10px; font-size: 12px; }
QLineEdit#login_input:focus { border-color: #3D7EFF; }
QPushButton#login_btn { background-color: #1A3E7A; color: #BEDAFF; border: 1px solid #2452A0; border-radius: 3px; padding: 8px; font-size: 12px; font-weight: 600; }
QPushButton#login_btn:hover { background-color: #1E4A8E; color: #D4E8FF; }
QPushButton#login_btn:pressed { background-color: #153268; }

/* LEGACY IDS from old main_window.py (kept for backward compat) */
#sidebar { background-color: #0D1219; border-right: 1px solid #18202F; }
#sidebar_logo_area { background-color: #0D1219; border-bottom: 1px solid #18202F; }
#app_name_label { color: #DCE4EF; font-size: 13px; font-weight: 600; }
#app_subtitle_label { color: #3D4E65; font-size: 10px; }
#nav_section_label { color: #3D4E65; font-size: 10px; font-weight: 600; letter-spacing: 0.8px; padding: 12px 14px 4px 14px; }
QPushButton#nav_button { background-color: transparent; color: #8A9AB0; border: none; border-left: 2px solid transparent; border-radius: 0; text-align: left; padding: 6px 14px; font-size: 12px; margin: 0; }
QPushButton#nav_button:hover { background-color: #111822; color: #C4D0DF; }
QPushButton#nav_button[active="true"] { background-color: #131E30; color: #3D7EFF; font-weight: 500; border-left: 2px solid #3D7EFF; }
#sidebar_user_area { background-color: #0D1219; border-top: 1px solid #18202F; padding: 10px 14px; }
#user_name_label { color: #C4D0DF; font-size: 12px; font-weight: 500; }
#user_role_label { color: #3D4E65; font-size: 10px; }
#connection_dot { color: #22C55E; font-size: 8px; }
QPushButton#logout_button { background-color: transparent; color: #3D4E65; border: none; font-size: 10px; padding: 2px 0; text-align: left; }
QPushButton#logout_button:hover { color: #EF4444; }
#topbar_title { color: #C4D0DF; font-size: 12px; font-weight: 500; }
#topbar_breadcrumb { color: #3D4E65; font-size: 11px; }
"""


def get_status_color(status: str) -> str:
    """Return text color for a lead status."""
    colors = {
        "new": "#8A9AB0",
        "contacted": "#60A5FA",
        "interested": "#34D399",
        "follow_up": "#FBBF24",
        "negotiation": "#A78BFA",
        "converted": "#34D399",
        "lost": "#F87171",
    }
    return colors.get(status.lower(), "#8A9AB0")


def get_priority_color(priority: str) -> str:
    """Return text color for a lead priority."""
    colors = {
        "high": "#FBBF24",
        "medium": "#86EFAC",
        "low": "#3D4E65",
    }
    return colors.get(priority.lower(), "#8A9AB0")


def get_sentiment_color(sentiment: str) -> str:
    """Return text color for sentiment."""
    colors = {
        "POSITIVE": "#34D399",
        "NEGATIVE": "#F87171",
        "NEUTRAL": "#8A9AB0",
        "MIXED": "#A78BFA",
    }
    return colors.get(sentiment.upper(), "#8A9AB0")


def score_to_color(score: int) -> str:
    if score >= 70:
        return "#22C55E"
    elif score >= 40:
        return "#FBBF24"
    else:
        return "#EF4444"
