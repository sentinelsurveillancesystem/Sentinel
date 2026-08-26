import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QFileDialog, QPushButton, QStatusBar
)
from PyQt6.QtCore    import Qt, QTimer, QSize
from PyQt6.QtGui     import QPixmap, QFont

import users_db
from theme import (
    BG_COLOR, PANEL_COLOR, INPUT_COLOR, BORDER_COLOR, TEXT_PRIMARY,
    TEXT_LIGHT, TEXT_MUTED, ACCENT_BLUE, ACCENT_RED, ACCENT_GREEN,
    HOVER_BLUE, FONT_FAMILY
)


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================
class PlaceholderBox(QFrame):
    """A box that displays either a real image or a placeholder text."""

    def __init__(self, placeholder_text: str, clickable: bool = False,
                 accent: str = ACCENT_BLUE, parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self.clickable        = clickable
        self.image_path       = None
        self.accent           = accent

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {INPUT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
            QFrame:hover {{
                border: 1px solid {self.accent};
            }}
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel(placeholder_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Arial", 11))
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                background: transparent;
                border: none;
            }}
        """)
        self._layout.addWidget(self.label)

        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.mousePressEvent = self._on_click

    def _on_click(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {self.placeholder_text}",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        if file_path:
            self.set_image(file_path)

    def set_image(self, image_path: str):
        self.image_path = image_path
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size() - QSize(20, 20),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.label.setPixmap(scaled)
            self.label.setText("")

    def set_text(self, text: str):
        self.label.setPixmap(QPixmap())
        self.label.setText(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_path:
            self.set_image(self.image_path)


class ProfileCard(QFrame):
    """Card showing person profile information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
                background: transparent;
                border: none;
            }}
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(15, 15, 15, 15)
        self._layout.setSpacing(8)

        self.title = QLabel("Profile Information")
        self.title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title.setStyleSheet(f"color: {TEXT_LIGHT}; padding-bottom: 5px;")
        self._layout.addWidget(self.title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {BORDER_COLOR}; max-height: 1px; border: none;")
        self._layout.addWidget(line)

        self.name_label   = self._create_info_row("Name",     "--")
        self.phn_label    = self._create_info_row("Phone",    "--")
        self.roll_label   = self._create_info_row("Roll/ID",  "--")
        self.branch_label = self._create_info_row("Branch",   "--")
        self.email_label  = self._create_info_row("Email",    "--")
        self.role_label   = self._create_info_row("Role",     "--")
        self.status_label = self._create_info_row("Status",   "--")

        self._layout.addStretch()

    def _create_info_row(self, label_text: str, value: str) -> QLabel:
        row = QLabel(f"{label_text}: {value}")
        row.setFont(QFont("Arial", 10))
        row.setStyleSheet(f"color: {TEXT_PRIMARY}; padding: 3px 0;")
        self._layout.addWidget(row)
        return row

    def update_profile(self, name: str, phone: str, roll: str,
                       branch: str = "", email: str = "",
                       role: str = "Student", status: str = "Active"):
        self.name_label.setText(f"Name: {name}")
        self.phn_label.setText(f"Phone: {phone}")
        self.roll_label.setText(f"Roll/ID: {roll}")
        self.branch_label.setText(f"Branch: {branch}" if branch else "Branch: --")
        self.email_label.setText(f"Email: {email}" if email else "Email: --")
        self.role_label.setText(f"Role: {role}")
        self.status_label.setText(f"Status: {status}")


class LiveFeedWidget(QFrame):
    """Live camera feed widget that keeps a 16:9 aspect ratio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_path = None

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {INPUT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
            QFrame:hover {{
                border: 1px solid {ACCENT_BLUE};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("▶  LIVE FEED\n(Click to load video source)")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Consolas", 14))
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                background: transparent;
                border: none;
            }}
        """)
        self._layout.addWidget(self.label)

        self.mousePressEvent = self._on_click

        self.frame_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(1000)

    def _on_click(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Live Feed Source",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )
        if file_path:
            self.set_image(file_path)

    def set_image(self, image_path: str):
        self.image_path = image_path
        self._refresh_pixmap()

    def _refresh_pixmap(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.label.setPixmap(scaled)
            self.label.setText("")

    def _update_frame(self):
        self.frame_count += 1
        if self.image_path is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.label.setText(f"▶  LIVE FEED\n[{timestamp}]   Frame: {self.frame_count}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_path:
            self._refresh_pixmap()


# ============================================================================
# Member dashboard
# ============================================================================
class ControlRoomDashboard(QMainWindow):
    """Main dashboard shown to members."""

    def __init__(self, profile: dict = None):
        super().__init__()
        self.profile = profile or {}
        self.username = self.profile.get("username", "unknown")

        self.setWindowTitle(f"Sentinel Surveillance System — {self.username}")
        self.setMinimumSize(1100, 750)

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BG_COLOR};
            }}
            QStatusBar {{
                background-color: {PANEL_COLOR};
                color: {TEXT_MUTED};
                border-top: 1px solid {BORDER_COLOR};
            }}
            QLabel {{
                font-family: {FONT_FAMILY};
            }}
        """)

        self._build_ui()
        self._populate_from_profile()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer_layout = QVBoxLayout(central)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        outer_layout.addWidget(self._build_header())

        # Main container
        main_container = QFrame()
        main_container.setStyleSheet(f"QFrame {{ background-color: {BG_COLOR}; border: none; }}")
        main_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container_layout = QHBoxLayout(main_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)

        # ---- LEFT PANEL ----
        left_panel = QFrame()
        left_panel.setStyleSheet(f"QFrame {{ background-color: {BG_COLOR}; border: none; }}")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        self.photo_box = PlaceholderBox(
            placeholder_text="Passport Photo\n(Click to load)",
            clickable=True,
            accent=ACCENT_BLUE,
        )
        self.photo_box.setMinimumHeight(180)
        self.photo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.photo_box, stretch=2)

        self.profile_card = ProfileCard()
        left_layout.addWidget(self.profile_card, stretch=3)

        container_layout.addWidget(left_panel, stretch=1)

        # ---- RIGHT PANEL (Live Feed) ----
        right_panel = QFrame()
        right_panel.setStyleSheet(f"QFrame {{ background-color: {BG_COLOR}; border: none; }}")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.live_feed_holder = QFrame()
        self.live_feed_holder.setStyleSheet("background-color: transparent; border: none;")
        self.live_feed_holder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        holder_layout = QVBoxLayout(self.live_feed_holder)
        holder_layout.setContentsMargins(0, 0, 0, 0)
        holder_layout.setSpacing(0)

        self.live_feed_container = QFrame()
        self.live_feed_container.setStyleSheet("background-color: transparent; border: none;")
        self.live_feed_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container_v = QVBoxLayout(self.live_feed_container)
        container_v.setContentsMargins(0, 0, 0, 0)
        container_v.setSpacing(0)

        self.live_feed = LiveFeedWidget()
        self.live_feed.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        container_v.addWidget(self.live_feed)

        holder_layout.addWidget(self.live_feed_container, alignment=Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.live_feed_holder, stretch=1)

        container_layout.addWidget(right_panel, stretch=2)

        outer_layout.addWidget(main_container, stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("●  System Ready  •  All Cameras Online")

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

    # ----------------------------------------------------------- header
    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QLabel {{ color: {TEXT_LIGHT}; background: transparent; border: none; }}
        """)
        h = QHBoxLayout(header)
        h.setContentsMargins(15, 8, 15, 8)

        title = QLabel("SENTINEL  •  Member Dashboard")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        h.addWidget(title)

        user_lbl = QLabel(f"👤  {self.profile.get('name', self.username)}")
        user_lbl.setFont(QFont("Arial", 10))
        user_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        h.addStretch()
        h.addWidget(user_lbl)

        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(30)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_RED};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 4px 14px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #e0414a; }}
        """)
        logout_btn.clicked.connect(self._logout)
        h.addSpacing(10)
        h.addWidget(logout_btn)

        # Red accent strip just below header
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(header)
        strip = QFrame()
        strip.setFixedHeight(3)
        strip.setStyleSheet(f"background-color: {ACCENT_RED}; border: none;")
        outer_layout.addWidget(strip)
        return outer

    # -------------------------------------------------- aspect ratio
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adjust_live_feed_aspect()

    def _adjust_live_feed_aspect(self):
        if not hasattr(self, "live_feed_container"):
            return
        available_w = self.live_feed_holder.width()
        available_h = self.live_feed_holder.height()
        if available_w <= 0 or available_h <= 0:
            return
        target_ratio = 16 / 9
        target_w = available_w
        target_h = int(target_w / target_ratio)
        if target_h > available_h:
            target_h = available_h
            target_w = int(target_h * target_ratio)
        self.live_feed_container.setFixedSize(target_w, target_h)

    # ------------------------------------------------------- data
    def _populate_from_profile(self):
        p = self.profile
        self.profile_card.update_profile(
            name   = p.get("name", "--"),
            phone  = p.get("phone", "--"),
            roll   = p.get("roll", "--"),
            branch = p.get("branch", ""),
            email  = p.get("email", ""),
            role   = p.get("role", "Student"),
            status = p.get("status", "Active"),
        )

    def _update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.status_bar.showMessage(f"●  Online  |  {now}")

    # ------------------------------------------------------- logout
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
    win = ControlRoomDashboard({
        "name": "Demo User", "phone": "+91-0000000000",
        "roll": "00", "branch": "CSE", "email": "demo@x.com",
        "role": "Student", "status": "Active", "username": "demo",
    })
    win.showMaximized()
    sys.exit(app.exec())
