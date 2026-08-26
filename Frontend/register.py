import re
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLineEdit,
    QMessageBox, QComboBox
)
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QFont, QPainter, QBrush, QColor

import users_db
from theme import (
    BG_COLOR, PANEL_COLOR, BORDER_COLOR, ACCENT_RED, TEXT_LIGHT,
    TEXT_MUTED, HOVER_BLUE, ACCENT_GREEN
)


# ---------------------------------------------------------------------------
# Logo helper (same as login)
# ---------------------------------------------------------------------------
class LogoCircle(QWidget):
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
# Register page
# ---------------------------------------------------------------------------
class RegisterPage(QMainWindow):
    """Form for new member registration."""

    BRANCHES = ["Select branch", "CSE", "IT", "ECE", "EEE",
                "MECH", "CIVIL", "AI&DS", "Other"]

    MIN_AGE = 13
    MAX_AGE = 120

    def __init__(self, login_window=None):
        super().__init__()
        self.login_window = login_window   # remembered so we can show it again
        self.setWindowTitle("Sentinel Surveillance System - Registration")
        self.resize(900, 880)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
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

        # Header
        root.addWidget(self._build_header())

        # Title
        title_holder = QWidget()
        title_holder.setStyleSheet("background: transparent; border: none;")
        tv = QVBoxLayout(title_holder)
        tv.setContentsMargins(30, 25, 30, 5)
        title = QLabel("SENTINEL SURVEILLANCE SYSTEM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        tv.addWidget(title)
        root.addWidget(title_holder)
        root.addSpacing(10)

        # "Registration Page" pill
        root.addWidget(self._build_pill())
        root.addSpacing(20)

        # Form panel
        form_holder = QWidget()
        form_holder.setStyleSheet("background: transparent; border: none;")
        fh = QHBoxLayout(form_holder)
        fh.setContentsMargins(20, 0, 20, 0)
        fh.addStretch()
        fh.addWidget(self._build_form_panel())
        fh.addStretch()
        root.addWidget(form_holder)
        root.addStretch()

        # Footer
        cr = QLabel("© 2026 Sentinel Surveillance System")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cr.setFont(QFont("Arial", 9))
        cr.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none; padding: 10px;")
        root.addWidget(cr)

    # ----------------------------------------------------------- header
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
        logo_lbl = QLabel("LOGO space")
        logo_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        logo_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
        ll.addSpacing(8)
        ll.addWidget(logo_lbl)
        h.addWidget(logo_holder)
        return header

    # -------------------------------------------------------------- pill
    def _build_pill(self):
        pill = QFrame()
        pill.setFixedHeight(45)
        pill.setFixedWidth(360)
        pill.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
        """)
        pv = QVBoxLayout(pill)
        pv.setContentsMargins(15, 5, 15, 5)
        lbl = QLabel("Registration Page")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; border: none;")
        pv.addWidget(lbl)

        holder = QWidget()
        holder.setStyleSheet("background: transparent; border: none;")
        h = QHBoxLayout(holder)
        h.addStretch()
        h.addWidget(pill)
        h.addStretch()
        return holder

    # ----------------------------------------------------------- form
    def _build_form_panel(self) -> QFrame:
        panel = QFrame()
        panel.setMaximumWidth(720)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
        """)
        pv = QVBoxLayout(panel)
        pv.setContentsMargins(35, 30, 35, 30)
        pv.setSpacing(14)

        # Form widgets
        self.username   = QLineEdit(); self.username.setPlaceholderText("Choose a unique username")
        self.name       = QLineEdit(); self.name.setPlaceholderText("Enter your full name")
        self.branch     = QComboBox()
        self.branch.addItems(self.BRANCHES)
        self.roll       = QLineEdit(); self.roll.setPlaceholderText("e.g. CS21B1045 or 58")
        self.age        = QLineEdit(); self.age.setPlaceholderText(
            f"e.g. 20 ({self.MIN_AGE}-{self.MAX_AGE})")
        self.mobile     = QLineEdit(); self.mobile.setPlaceholderText("e.g. +91-9876543210")
        self.email      = QLineEdit(); self.email.setPlaceholderText("e.g. you@example.com")
        self.password   = QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Choose a password (min 8 characters)")
        self.repassword = QLineEdit(); self.repassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.repassword.setPlaceholderText("Re-enter the password")

        fields = [
            ("Username (unique):",  self.username),
            ("Name:",               self.name),
            ("Branch:",             self.branch),
            ("Roll no:",            self.roll),
            ("Age:",                self.age),
            ("Mobile no:",          self.mobile),
            ("Email:",              self.email),
            ("Password:",           self.password),
            ("Re-enter Password:",  self.repassword),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)

        for i, (text, widget) in enumerate(fields):
            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if isinstance(widget, QLineEdit):
                widget.setFixedHeight(38)
                widget.setStyleSheet(self._input_style())
            else:
                widget.setFixedHeight(38)
                widget.setStyleSheet(self._combo_style())

            grid.addWidget(lbl,    i, 0)
            grid.addWidget(widget, i, 1)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        pv.addLayout(grid)
        pv.addSpacing(6)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.register_btn = QPushButton("Register")
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.setFixedSize(150, 42)
        self.register_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: white; border: none; border-radius: 6px;
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #2ea043; }}
            QPushButton:disabled {{ background-color: {BORDER_COLOR};
                                    color: {TEXT_MUTED}; }}
        """)
        self.register_btn.clicked.connect(self._on_register)
        btn_row.addWidget(self.register_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFixedSize(150, 42)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {HOVER_BLUE};
                border: 1px solid {HOVER_BLUE};
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {HOVER_BLUE}; color: white; }}
        """)
        back_btn.clicked.connect(self._on_back)
        btn_row.addWidget(back_btn)

        btn_row.addStretch()
        pv.addLayout(btn_row)
        return panel

    # --------------------------------------------------------- styles
    @staticmethod
    def _input_style():
        return f"""
            QLineEdit {{
                background-color: {BG_COLOR};
                color: {TEXT_LIGHT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {HOVER_BLUE}; }}
        """

    @staticmethod
    def _combo_style():
        return f"""
            QComboBox {{
                background-color: {BG_COLOR};
                color: {TEXT_LIGHT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox:focus {{ border: 1px solid {HOVER_BLUE}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: {PANEL_COLOR};
                color: {TEXT_LIGHT};
                selection-background-color: {HOVER_BLUE};
                border: 1px solid {BORDER_COLOR};
            }}
        """

    # --------------------------------------------------------- validate
    def _validate(self):
        u  = self.username.text().strip()
        n  = self.name.text().strip()
        b  = self.branch.currentText()
        r  = self.roll.text().strip()
        a  = self.age.text().strip()
        m  = self.mobile.text().strip()
        e  = self.email.text().strip()
        p  = self.password.text()
        rp = self.repassword.text()

        if not all([u, n, r, a, m, e, p, rp]):
            return False, "Please fill in all fields."
        if b == "Select branch":
            return False, "Please select a branch."
        if len(u) < 3:
            return False, "Username must be at least 3 characters."
        if len(u) > 32:
            return False, "Username must be 32 characters or fewer."
        if not re.match(r"^[A-Za-z0-9_]+$", u):
            return False, "Username may only contain letters, digits, or underscores."
        if not a.isdigit() or not (self.MIN_AGE <= int(a) <= self.MAX_AGE):
            return False, f"Age must be a whole number between {self.MIN_AGE} and {self.MAX_AGE}."
        if len(p) < 8:
            return False, "Password must be at least 8 characters."
        if p != rp:
            return False, "Passwords do not match."
        if not re.match(r"^[+]?[\d\s\-]{7,15}$", m):
            return False, "Please enter a valid mobile number."
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
            return False, "Please enter a valid email address."
        if users_db.username_exists(u):
            return False, f"Username '{u}' is already taken. Please choose another."

        return True, "OK"

    # --------------------------------------------------------- actions
    def _on_register(self):
        ok, msg = self._validate()
        if not ok:
            QMessageBox.warning(self, "Invalid input", msg)
            return

        username = self.username.text().strip()
        full_name = self.name.text().strip()

        # Disabled while the request is in flight, so a double-click can't
        # fire two registrations. finally: re-enables even on exception.
        self.register_btn.setEnabled(False)
        try:
            success = users_db.add_user(
                username = username,
                password = self.password.text(),
                # The server only accepts 'admin' or 'member'. Self-service
                # signups are always members; admins are pre-seeded.
                role     = "member",
                age      = int(self.age.text().strip()),
                name     = full_name,
                phone    = self.mobile.text().strip(),
                roll     = self.roll.text().strip(),
                branch   = self.branch.currentText(),
                email    = self.email.text().strip(),
            )
        finally:
            self.register_btn.setEnabled(True)

        if not success:
            QMessageBox.critical(
                self, "Registration failed",
                users_db.last_error or "Could not create the account.",
            )
            return

        users_db.log_activity(username, "REGISTER_SUCCESS",
                              f"New member: {full_name}")

        QMessageBox.information(
            self, "Registration Successful",
            f"Account '{username}' has been created!\n\n"
            f"You will now be redirected to the login page.",
        )
        self._on_back()

    def _on_back(self):
        """Return to the login page that opened us."""
        if self.login_window is not None:
            self.login_window.show()
        else:
            from login import LoginPage
            self.login_window = LoginPage()
            self.login_window.show()
        self.close()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    users_db.init_db()
    win = RegisterPage()
    win.show()
    sys.exit(app.exec())