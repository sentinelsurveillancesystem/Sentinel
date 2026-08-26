import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGridLayout, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QStatusBar, QMessageBox, QFileDialog, QListWidget,
    QListWidgetItem, QTabWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui  import QFont, QPixmap, QPainter, QColor, QBrush

import users_db
from theme import (
    BG_COLOR, PANEL_COLOR, INPUT_COLOR, BORDER_COLOR, TEXT_PRIMARY,
    TEXT_LIGHT, TEXT_MUTED, ACCENT_BLUE, ACCENT_RED, ACCENT_GREEN,
    ACCENT_PURPLE, ACCENT_TEAL, ACCENT_DANGER, HOVER_BLUE, FONT_FAMILY
)


# ============================================================================
# Logo
# ============================================================================
class LogoCircle(QWidget):
    def __init__(self, diameter=40, parent=None):
        super().__init__(parent)
        self.setFixedSize(diameter, diameter)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(ACCENT_RED)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())
        p.setPen(QColor("white"))
        p.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "S")


# ============================================================================
# Stat card
# ============================================================================
class StatCard(QFrame):
    """Coloured card showing one metric."""

    def __init__(self, label: str, value: str, color: str, icon: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-left: 4px solid {color};
                border-radius: 6px;
            }}
            QLabel {{ color: {TEXT_PRIMARY}; background: transparent; border: none; }}
        """)
        v = QVBoxLayout(self)
        v.setContentsMargins(15, 12, 15, 12)
        v.setSpacing(4)

        top = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet("font-size: 22px; background: transparent; border: none;")
        lbl = QLabel(label)
        lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        top.addWidget(ico)
        top.addSpacing(6)
        top.addWidget(lbl)
        top.addStretch()
        v.addLayout(top)

        self.value_lbl = QLabel(value)
        self.value_lbl.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        v.addWidget(self.value_lbl)

        self.sub_lbl = QLabel("")
        self.sub_lbl.setFont(QFont("Arial", 9))
        self.sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        v.addWidget(self.sub_lbl)

    def update_value(self, value: str, sub: str = ""):
        self.value_lbl.setText(value)
        self.sub_lbl.setText(sub)


# ============================================================================
# Camera feed tile
# ============================================================================
class CameraTile(QFrame):
    """A single camera feed placeholder with a click-to-load behaviour."""

    def __init__(self, cam_id: str, location: str, parent=None):
        super().__init__(parent)
        self.cam_id    = cam_id
        self.location  = location
        self.image_path = None

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {INPUT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
            QFrame:hover {{ border: 1px solid {ACCENT_TEAL}; }}
            QLabel {{ color: {TEXT_MUTED}; background: transparent; border: none; }}
        """)
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(4)

        top = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {ACCENT_GREEN}; background: transparent; border: none; font-size: 12px;")
        top.addWidget(self.status_dot)
        cam_lbl = QLabel(f"{cam_id}  •  {location}")
        cam_lbl.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        cam_lbl.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        top.addWidget(cam_lbl)
        top.addStretch()
        v.addLayout(top)

        self.image_lbl = QLabel("📷  CLICK TO LOAD FEED")
        self.image_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_lbl.setFont(QFont("Arial", 11))
        v.addWidget(self.image_lbl, stretch=1)

        self.timestamp_lbl = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.timestamp_lbl.setFont(QFont("Consolas", 9))
        self.timestamp_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        v.addWidget(self.timestamp_lbl)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mousePressEvent = self._on_click

    def _on_click(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Load feed for {self.cam_id}",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )
        if file_path:
            self.set_image(file_path)

    def set_image(self, path: str):
        self.image_path = path
        pix = QPixmap(path)
        if not pix.isNull():
            scaled = pix.scaled(
                self.image_lbl.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_lbl.setPixmap(scaled)
            self.image_lbl.setText("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_path:
            self.set_image(self.image_path)

    def tick(self):
        """Update the timestamp — simulate live feed heartbeat."""
        self.timestamp_lbl.setText(datetime.now().strftime("%H:%M:%S"))
        # Tiny "blink" on the status dot for realism
        self.status_dot.setStyleSheet(
            f"color: {ACCENT_GREEN}; background: transparent; border: none; font-size: 12px;"
        )


# ============================================================================
# Member card (clickable in the members panel)
# ============================================================================
class MemberRow(QFrame):
    """One row in the members list."""

    def __init__(self, data: dict, on_click, parent=None):
        super().__init__(parent)
        self.data = data
        self.on_click = on_click

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {INPUT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
            }}
            QFrame:hover {{ border: 1px solid {ACCENT_PURPLE}; background-color: {PANEL_COLOR}; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        h = QHBoxLayout(self)
        h.setContentsMargins(10, 8, 10, 8)

        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 22px; background: transparent; border: none;")
        h.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(2)

        name = QLabel(data.get("name", data.get("username")))
        name.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        info.addWidget(name)

        sub = QLabel(f"Roll: {data.get('roll', '--')}  •  {data.get('branch', '--')}")
        sub.setFont(QFont("Arial", 9))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        info.addWidget(sub)

        h.addLayout(info, stretch=1)

        status_color = ACCENT_GREEN if data.get("status") == "Active" else ACCENT_DANGER
        status = QLabel(f"● {data.get('status', 'Active')}")
        status.setFont(QFont("Consolas", 9))
        status.setStyleSheet(f"color: {status_color}; background: transparent; border: none;")
        h.addWidget(status)

        self.mousePressEvent = self._click

    def _click(self, event):
        self.on_click(self.data)


# ============================================================================
# Admin Dashboard
# ============================================================================
class AdminDashboard(QMainWindow):
    """Top-level admin window."""

    def __init__(self, profile: dict):
        super().__init__()
        self.profile  = profile
        self.username = profile.get("username", "admin")
        self.all_members: list = []

        self.setWindowTitle(f"Sentinel Surveillance System — Admin ({self.username})")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {BG_COLOR}; }}
            QStatusBar  {{ background-color: {PANEL_COLOR}; color: {TEXT_MUTED};
                          border-top: 1px solid {BORDER_COLOR}; }}
            QLabel      {{ font-family: {FONT_FAMILY}; }}
            QListWidget {{
                background-color: {INPUT_COLOR};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
            }}
            QListWidget::item {{ padding: 4px; }}
            QListWidget::item:selected {{ background-color: {ACCENT_BLUE}; color: white; }}
        """)

        self._build_ui()
        self._refresh_all()

        # Periodic refresh (every 5s)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_all)
        self.refresh_timer.start(5000)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_header())

        body = QFrame()
        body.setStyleSheet(f"QFrame {{ background-color: {BG_COLOR}; border: none; }}")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(10, 10, 10, 10)
        body_layout.setSpacing(10)

        # Stats row
        self.stat_members = StatCard("Total Members", "0", ACCENT_PURPLE, "👥")
        self.stat_cameras = StatCard("Active Cameras", "4", ACCENT_TEAL,  "📹")
        self.stat_events  = StatCard("Events Today",   "0", ACCENT_BLUE,  "⚡")
        self.stat_online  = StatCard("Online Users",   "1", ACCENT_GREEN, "🟢")

        stats = QHBoxLayout()
        stats.setSpacing(10)
        stats.addWidget(self.stat_members)
        stats.addWidget(self.stat_cameras)
        stats.addWidget(self.stat_events)
        stats.addWidget(self.stat_online)
        body_layout.addLayout(stats)

        # Main split
        split = QHBoxLayout()
        split.setSpacing(10)

        # LEFT: members panel
        self._build_members_panel_into(split)

        # RIGHT: cameras + events
        self._build_right_panel_into(split)

        body_layout.addLayout(split, stretch=1)

        outer.addWidget(body, stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("●  Admin console ready")

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

    # ------------------------------------------------------------- header
    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QLabel {{ color: {TEXT_LIGHT}; background: transparent; border: none; }}
        """)
        h = QHBoxLayout(header)
        h.setContentsMargins(15, 8, 15, 8)

        h.addWidget(LogoCircle(40))
        h.addSpacing(8)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("SENTINEL  •  Admin Console")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title_box.addWidget(title)
        sub = QLabel(f"Logged in as {self.profile.get('name', self.username)}")
        sub.setFont(QFont("Arial", 9))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        title_box.addWidget(sub)
        h.addLayout(title_box)

        h.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(32)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_RED};
                color: white; border: none; border-radius: 5px;
                padding: 4px 16px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #e0414a; }}
        """)
        logout_btn.clicked.connect(self._logout)
        h.addWidget(logout_btn)

        outer = QWidget()
        ol = QVBoxLayout(outer)
        ol.setContentsMargins(0, 0, 0, 0)
        ol.setSpacing(0)
        ol.addWidget(header)
        strip = QFrame()
        strip.setFixedHeight(3)
        strip.setStyleSheet(f"background-color: {ACCENT_RED}; border: none;")
        ol.addWidget(strip)
        return outer

    # --------------------------------------------------------- members
    def _build_members_panel_into(self, parent_layout):
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        panel.setFixedWidth(330)
        v = QVBoxLayout(panel)
        v.setContentsMargins(15, 15, 15, 15)
        v.setSpacing(10)

        title = QLabel("Members Directory")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        v.addWidget(title)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search by name or roll…")
        self.search_box.setFixedHeight(34)
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {INPUT_COLOR};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QLineEdit:focus {{ border: 1px solid {ACCENT_BLUE}; }}
        """)
        self.search_box.textChanged.connect(self._filter_members)
        v.addWidget(self.search_box)

        # Scrollable list
        self.members_scroll = QScrollArea()
        self.members_scroll.setWidgetResizable(True)
        self.members_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {INPUT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
            QScrollBar:vertical {{
                background: {INPUT_COLOR};
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_COLOR};
                border-radius: 4px;
                min-height: 20px;
            }}
        """)
        self.members_container = QWidget()
        self.members_container.setStyleSheet("background-color: transparent; border: none;")
        self.members_layout = QVBoxLayout(self.members_container)
        self.members_layout.setContentsMargins(6, 6, 6, 6)
        self.members_layout.setSpacing(6)
        self.members_layout.addStretch()
        self.members_scroll.setWidget(self.members_container)
        v.addWidget(self.members_scroll, stretch=1)

        # Member detail panel (populated when row clicked)
        self.detail_box = QFrame()
        self.detail_box.setStyleSheet(f"""
            QFrame {{
                background-color: {INPUT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        dv = QVBoxLayout(self.detail_box)
        dv.setContentsMargins(10, 10, 10, 10)
        dv.setSpacing(4)

        self.detail_title = QLabel("Click a member to view details")
        self.detail_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.detail_title.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        self.detail_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dv.addWidget(self.detail_title)
        self.detail_body = QLabel("")
        self.detail_body.setFont(QFont("Arial", 9))
        self.detail_body.setWordWrap(True)
        self.detail_body.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent; border: none;")
        dv.addWidget(self.detail_body)
        v.addWidget(self.detail_box)

        parent_layout.addWidget(panel)

    # ----------------------------------------------------------- right
    def _build_right_panel_into(self, parent_layout):
        right = QFrame()
        right.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_COLOR};
                border: none;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(10)

        # Section title
        sec = QLabel("Live Camera Feeds  •  Surveillance Console")
        sec.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        sec.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        rv.addWidget(sec)

        # Camera grid (2x2)
        self.cam_grid = QGridLayout()
        self.cam_grid.setSpacing(8)

        self.cams = [
            CameraTile("CAM-01", "Main Entrance"),
            CameraTile("CAM-02", "Lobby"),
            CameraTile("CAM-03", "Server Room"),
            CameraTile("CAM-04", "Parking Lot"),
        ]
        for i, cam in enumerate(self.cams):
            self.cam_grid.addWidget(cam, i // 2, i % 2)
        rv.addLayout(self.cam_grid, stretch=3)

        # Tabs for events & activity
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {BORDER_COLOR};
                background-color: {PANEL_COLOR};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {INPUT_COLOR};
                color: {TEXT_MUTED};
                padding: 6px 14px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 10px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {PANEL_COLOR};
                color: {TEXT_LIGHT};
            }}
        """)

        # Activity tab
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {INPUT_COLOR};
                color: {TEXT_PRIMARY};
                border: none;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }}
        """)
        self.tabs.addTab(self.activity_log, "📋  Activity Log")

        # Events tab
        self.events_log = QTextEdit()
        self.events_log.setReadOnly(True)
        self.events_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {INPUT_COLOR};
                color: {TEXT_PRIMARY};
                border: none;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }}
        """)
        self.tabs.addTab(self.events_log, "⚡  Surveillance Events")

        rv.addWidget(self.tabs, stretch=2)

        parent_layout.addWidget(right, stretch=1)

    # --------------------------------------------------- data refresh
    def _refresh_all(self):
        """Reload members, stats, and event/activity panels."""
        self.all_members = users_db.get_all_members()
        self._render_members(self.all_members)

        # Stats
        self.stat_members.update_value(
            str(len(self.all_members)),
            f"{sum(1 for m in self.all_members if m.get('status') == 'Active')} active",
        )
        self.stat_cameras.update_value(str(len(self.cams)), "All feeds online")

        # Events today
        try:
            events = users_db.get_recent_events(100)
            today  = datetime.now().date()
            today_count = sum(1 for e in events
                              if datetime.fromisoformat(e["timestamp"]).date() == today)
        except Exception:
            today_count = 0
        self.stat_events.update_value(str(today_count), "last 24h")

        self.stat_online.update_value("1", "current session")

        # Logs
        self._render_activity_log()
        self._render_events_log()

        # Tick cameras
        for cam in self.cams:
            cam.tick()

    def _render_members(self, members: list):
        # Clear existing
        while self.members_layout.count():
            item = self.members_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if not members:
            empty = QLabel("No members registered yet.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"color: {TEXT_MUTED}; padding: 20px;")
            self.members_layout.addWidget(empty)
        else:
            for m in members:
                row = MemberRow(m, self._show_member_detail)
                self.members_layout.addWidget(row)

        self.members_layout.addStretch()

    def _filter_members(self, text: str):
        text = text.strip().lower()
        if not text:
            self._render_members(self.all_members)
            return
        filtered = [
            m for m in self.all_members
            if text in m.get("name", "").lower()
            or text in m.get("roll", "").lower()
            or text in m.get("username", "").lower()
        ]
        self._render_members(filtered)

    def _show_member_detail(self, data: dict):
        self.detail_title.setText(data.get("name", data.get("username")))
        self.detail_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.detail_title.setStyleSheet(f"color: {ACCENT_PURPLE}; font-weight: bold;")
        last = data.get("last_login") or "Never"
        body = (
            f"Username:  {data.get('username', '--')}\n"
            f"Roll/ID:   {data.get('roll', '--')}\n"
            f"Branch:    {data.get('branch', '--')}\n"
            f"Phone:     {data.get('phone', '--')}\n"
            f"Email:     {data.get('email', '--')}\n"
            f"Status:    {data.get('status', 'Active')}\n"
            f"Last seen: {last}"
        )
        self.detail_body.setText(body)

    def _render_activity_log(self):
        rows = users_db.get_recent_activity(50)
        if not rows:
            self.activity_log.setHtml(f"<i style='color:{TEXT_MUTED}'>No activity yet.</i>")
            return
        html_rows = []
        for r in rows:
            color = ACCENT_GREEN if "SUCCESS" in (r["action"] or "") else \
                    ACCENT_DANGER if "FAIL" in (r["action"] or "") else \
                    ACCENT_TEAL
            html_rows.append(
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{TEXT_MUTED}'>[{r['timestamp']}]</span> "
                f"<b style='color:{TEXT_LIGHT}'>{r['username']}</b> "
                f"<span style='color:{color}'>{r['action']}</span> "
                f"<span style='color:{TEXT_MUTED}'>— {r.get('details', '')}</span>"
                f"</div>"
            )
        self.activity_log.setHtml("<br>".join(html_rows))

    def _render_events_log(self):
        rows = users_db.get_recent_events(50)
        if not rows:
            self.events_log.setHtml(f"<i style='color:{TEXT_MUTED}'>No events recorded.</i>")
            return
        html_rows = []
        sev_color = {
            "info":    ACCENT_TEAL,
            "warning": ACCENT_DANGER,
            "error":   ACCENT_RED,
        }
        for r in rows:
            color = sev_color.get(r.get("severity", "info"), ACCENT_TEAL)
            html_rows.append(
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{TEXT_MUTED}'>[{r['timestamp']}]</span> "
                f"<b style='color:{TEXT_LIGHT}'>{r['camera_id']}</b> "
                f"<span style='color:{color}'>{r['event_type']}</span> "
                f"<span style='color:{TEXT_MUTED}'>— {r.get('location', '')} "
                f"· {r.get('description', '')}</span>"
                f"</div>"
            )
        self.events_log.setHtml("<br>".join(html_rows))

    # ----------------------------------------------------------- clock
    def _update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.status_bar.showMessage(f"●  Admin online  |  {now}  |  Logged in as {self.username}")

    # ----------------------------------------------------------- logout
    def _logout(self):
        users_db.log_activity(self.username, "LOGOUT")
        users_db.logout()          # <-- clears the token
        from login import LoginPage
        self.login_window = LoginPage()
        self.login_window.show()
        self.close()


# ============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    users_db.init_db()
    users_db.seed_demo_users()
    users_db.seed_demo_events()
    profile = users_db.get_user_profile("admin")
    win = AdminDashboard(profile)
    win.showMaximized()
    sys.exit(app.exec())
