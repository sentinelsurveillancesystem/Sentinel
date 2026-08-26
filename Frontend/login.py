import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QMessageBox
)
from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QFont, QPainter, QColor, QBrush

import users_db
from theme import (
    BG_COLOR, PANEL_COLOR, BORDER_COLOR, ACCENT_RED, TEXT_LIGHT,
    TEXT_MUTED, HOVER_BLUE, ACCENT_BLUE, ACCENT_PURPLE
)


# ---------------------------------------------------------------------------
# Logo helper
# ---------------------------------------------------------------------------
class LogoCircle(QWidget):
    """Round red logo with a white 'S'."""
    def __init__(self, diameter: int = 60, parent=None):
        super().__init__(parent)
        self.setFixedSize(diameter, diameter)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(ACCENT_RED)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())
        p.setPen(QColor("white"))
        p.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "S")


# ---------------------------------------------------------------------------
# Login Page
# ---------------------------------------------------------------------------
class LoginPage(QMainWindow):
    """Two-pane login (admin / member) with role-card highlight."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentinel Surveillance System - Login")
        self.resize(1000, 760)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.dashboard_window = None
        self.register_window  = None

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Red accent strip
        strip = QFrame()
        strip.setFixedHeight(4)
        strip.setStyleSheet(f"background-color: {ACCENT_RED}; border: none;")
        root.addWidget(strip)

        root.addWidget(self._build_header())

        # Title block
        title_holder = QWidget()
        title_holder.setStyleSheet("background: transparent; border: none;")
        tv = QVBoxLayout(title_holder)
        tv.setContentsMargins(30, 25, 30, 5)

        title = QLabel("SENTINEL SURVEILLANCE SYSTEM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        tv.addWidget(title)

        subtitle = QLabel("Login Page")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        tv.addWidget(subtitle)
        root.addWidget(title_holder)
        root.addSpacing(20)

        # Role selection cards
        cards_row = QWidget()
        cards_row.setStyleSheet("background: transparent; border: none;")
        cards = QHBoxLayout(cards_row)
        cards.setContentsMargins(60, 0, 60, 0)
        cards.setSpacing(40)
        cards.addStretch()
        cards.addWidget(self._make_role_card("admin",  "Admin",   ACCENT_BLUE,   "👤"))
        cards.addWidget(self._make_role_card("member", "Members", ACCENT_PURPLE, "👥"))
        cards.addStretch()
        root.addWidget(cards_row)
        root.addSpacing(15)

        # Two login forms
        lower = QFrame()
        lower.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border-top: 1px solid {BORDER_COLOR};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)
        ll = QHBoxLayout(lower)
        ll.setContentsMargins(60, 25, 60, 25)
        ll.setSpacing(40)
        ll.addWidget(self._make_login_box("admin",  "Admin Login",
                                          ACCENT_BLUE,
                                          "Access Whole System"))
        ll.addWidget(self._make_login_box("member", "Member Login",
                                          ACCENT_PURPLE,
                                          "Personal surveillance dashboard"))
        root.addWidget(lower)
        root.addStretch()

        
        # Footer w/ register button
        footer_row = QWidget()
        footer_row.setStyleSheet("background: transparent; border: none;")
        fr = QHBoxLayout(footer_row)
        fr.setContentsMargins(30, 0, 30, 10)
        reg_btn = QPushButton("+ Register New Member Here")
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setFixedHeight(36)
        reg_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {HOVER_BLUE};
                border: 1px solid {HOVER_BLUE};
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {HOVER_BLUE}; color: white; }}
        """)
        reg_btn.clicked.connect(self._open_register)
        fr.addStretch()
        fr.addWidget(reg_btn)
        fr.addStretch()
        root.addWidget(footer_row)

        cr = QLabel("© 2026 Sentinel Surveillance System  •  v1.0")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cr.setFont(QFont("Arial", 9))
        cr.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none; padding: 5px;")
        root.addWidget(cr)

    # ------------------------------------------------------------ header
    def _build_header(self):
        header = QFrame()
        header.setStyleSheet(f"background-color: {PANEL_COLOR}; border-bottom: 1px solid {BORDER_COLOR};")
        header.setFixedHeight(90)
        h = QHBoxLayout(header)
        h.setContentsMargins(30, 10, 30, 10)

        welcome = QLabel("WELCOME")
        welcome.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        welcome.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        h.addWidget(welcome)
        h.addStretch()

        logo_holder = QFrame()
        logo_holder.setStyleSheet("background: transparent; border: none;")
        ll = QHBoxLayout(logo_holder)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.addWidget(LogoCircle(60))
        logo_lbl = QLabel("SENTINEL")
        logo_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        logo_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        ll.addSpacing(8)
        ll.addWidget(logo_lbl)
        h.addWidget(logo_holder)
        return header

    # ------------------------------------------------------------ cards
    def _make_role_card(self, key: str, label: str, color: str, emoji: str) -> QFrame:
        card = QFrame()
        card.setFixedSize(220, 180)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
            QFrame:hover {{ border: 1px solid {color}; }}
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(15, 15, 15, 15)
        v.setSpacing(10)

        icon = QLabel(emoji)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background: transparent; border: none; font-size: 56px;")
        v.addWidget(icon)

        btn = QPushButton(label)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white; border: none; border-radius: 6px;
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {HOVER_BLUE}; }}
        """)
        btn.clicked.connect(lambda _, r=key: self._highlight_form(r))
        v.addWidget(btn)
        return card

    # ----------------------------------------------------- login box
    def _make_login_box(self, key: str, title: str, color: str, note: str) -> QFrame:
        box = QFrame()
        box.setObjectName(f"loginBox_{key}")
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
        """)
        v = QVBoxLayout(box)
        v.setContentsMargins(25, 25, 25, 25)
        v.setSpacing(12)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        v.addWidget(title_lbl)

        note_lbl = QLabel(f"→ {note}")
        note_lbl.setFont(QFont("Arial", 10))
        note_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        v.addWidget(note_lbl)
        v.addSpacing(8)

        # Username
        ul = QLabel("Username")
        ul.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        v.addWidget(ul)
        username = QLineEdit()
        username.setPlaceholderText("Enter username")
        username.setFixedHeight(38)
        username.setStyleSheet(self._input_style())
        v.addWidget(username)

        # Password
        pl = QLabel("Password")
        pl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        v.addWidget(pl)
        password = QLineEdit()
        password.setPlaceholderText("Enter password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setFixedHeight(38)
        password.setStyleSheet(self._input_style())
        v.addWidget(password)

        v.addSpacing(8)

        login_btn = QPushButton(f"Login as {title.split()[0]}")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setFixedHeight(40)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white; border: none; border-radius: 6px;
                font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {HOVER_BLUE}; }}
            QPushButton:disabled {{ background-color: {BORDER_COLOR};
                                    color: {TEXT_MUTED}; }}
        """)
        login_btn.clicked.connect(lambda _, r=key, u=username, p=password,
                                  b=login_btn: self._do_login(r, u, p, b))
        v.addWidget(login_btn)
        return box

    # ------------------------------------------------------ helpers
    @staticmethod
    def _input_style():
        return f"""
            QLineEdit {{
                background-color: {PANEL_COLOR};
                color: {TEXT_LIGHT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {HOVER_BLUE}; }}
        """

    def _highlight_form(self, role: str):
        """Flash a colored border around the chosen role's login box."""
        self.activateWindow()
        target = f"loginBox_{role}"
        for w in self.findChildren(QFrame):
            if w.objectName() == target:
                w.setStyleSheet(f"""
                    QFrame {{
                        background-color: {BG_COLOR};
                        border: 2px solid {HOVER_BLUE};
                        border-radius: 10px;
                    }}
                """)
                QTimer.singleShot(
                    1500,
                    lambda ww=w: ww.setStyleSheet(f"""
                        QFrame {{
                            background-color: {BG_COLOR};
                            border: 1px solid {BORDER_COLOR};
                            border-radius: 10px;
                        }}
                    """),
                )
        QMessageBox.information(
            self, "Select Role",
            f"Please enter your {role} credentials below."
        )

    # ------------------------------------------------------ auth
    def _do_login(self, role: str, user_widget: QLineEdit,
                  pass_widget: QLineEdit, button: QPushButton):
        username = user_widget.text().strip()
        # NOT .strip() — register.py sends the password exactly as typed,
        # so stripping here would silently break any password that begins
        # or ends with a space.
        password = pass_widget.text()

        if not username or not password:
            QMessageBox.warning(self, "Missing fields",
                                "Please enter both username and password.")
            return

        # Guard against a double-click firing two login requests.
        button.setEnabled(False)
        try:
            user = users_db.authenticate(username, password)
        finally:
            button.setEnabled(True)

        if not user:
            QMessageBox.critical(
                self, "Login failed",
                users_db.last_error or "Invalid username or password.",
            )
            users_db.log_activity(username or "?", "LOGIN_FAILED")
            return

        if user["role"] != role:
            users_db.log_activity(user["username"], "LOGIN_WRONG_PORTAL",
                                  f"Tried the {role} portal")
            QMessageBox.warning(
                self, "Wrong portal",
                f"This account is not a {role}. Use the correct login box.",
            )
            return

        users_db.log_activity(user["username"], "LOGIN_SUCCESS")
        # authenticate() already returned the full profile — re-fetching it
        # is a second round trip that can fail and hand None to the
        # dashboard.
        self._open_dashboard(user)

    # ------------------------------------------------- navigation
    def _open_dashboard(self, profile: dict):
        """Route to the correct dashboard based on role."""
        if profile["role"] == "admin":
            from admin_dashboard import AdminDashboard
            self.dashboard_window = AdminDashboard(profile)
        else:
            from dashboard import ControlRoomDashboard
            self.dashboard_window = ControlRoomDashboard(profile)
        self.dashboard_window.show()
        self.close()

    def _open_register(self):
        from register import RegisterPage
        self.register_window = RegisterPage(self)  # pass self so back works
        self.register_window.show()
        self.hide()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    users_db.init_db()
    win = LoginPage()
    win.show()
    sys.exit(app.exec())