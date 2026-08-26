import sys
from PyQt6.QtWidgets import (
    QApplication, QSplashScreen, QProgressBar, QLabel
)
from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QPixmap, QFont, QColor, QPainter

import users_db
from theme import BG_COLOR, PANEL_COLOR, TEXT_LIGHT, TEXT_MUTED, ACCENT_RED


# ---------------------------------------------------------------------------
# Splash painting
# ---------------------------------------------------------------------------
def _build_splash_pixmap(w: int = 720, h: int = 420) -> QPixmap:
    """Draw the splash background programmatically (no external image)."""
    pix = QPixmap(w, h)
    pix.fill(QColor(BG_COLOR))

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Top red accent strip
    p.setBrush(QColor(ACCENT_RED))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(0, 0, w, 6)

    # Logo circle
    p.setBrush(QColor(ACCENT_RED))
    p.drawEllipse(w // 2 - 55, 70, 110, 110)
    p.setPen(QColor("white"))
    p.setFont(QFont("Arial", 48, QFont.Weight.Bold))
    p.drawText(pix.rect().adjusted(0, 70, 0, 0),
               Qt.AlignmentFlag.AlignCenter, "S")

    # Titles
    p.setPen(QColor(TEXT_LIGHT))
    p.setFont(QFont("Arial", 26, QFont.Weight.Bold))
    p.drawText(pix.rect().adjusted(0, 200, 0, 0),
               Qt.AlignmentFlag.AlignCenter, "SENTINEL")

    p.setFont(QFont("Arial", 14))
    p.drawText(pix.rect().adjusted(0, 240, 0, 0),
               Qt.AlignmentFlag.AlignCenter, "Surveillance System")

    p.setPen(QColor(TEXT_MUTED))
    p.setFont(QFont("Arial", 10))
    p.drawText(pix.rect().adjusted(0, 285, 0, 0),
               Qt.AlignmentFlag.AlignCenter, "v2.0  •  Secure Access Control")
    p.end()
    return pix


# ---------------------------------------------------------------------------
# Splash window
# ---------------------------------------------------------------------------
class SplashWindow(QSplashScreen):
    """Animated splash with status text and a red progress bar."""

    LOAD_STEPS = [
        (15,  "Mounting secure database..."),
        (30,  "Verifying user accounts..."),
        (50,  "Loading surveillance feeds..."),
        (70,  "Establishing secure channels..."),
        (90,  "Initializing dashboards..."),
        (100, "Ready."),
    ]

    def __init__(self):
        super().__init__(_build_splash_pixmap())
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        w, h = 720, 420

        # Status label
        self.status = QLabel("Initializing...", self)
        self.status.setGeometry(40, h - 75, w - 80, 25)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(
            f"color: {TEXT_MUTED}; background: transparent;"
            f"font-family: 'Consolas', monospace; font-size: 11px;"
        )

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setGeometry(80, h - 42, w - 160, 14)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {PANEL_COLOR};
                border: 1px solid #21262d;
                border-radius: 7px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_RED};
                border-radius: 7px;
            }}
        """)

        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._advance)
        self.timer.start(35)

    def _advance(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        for value, msg in self.LOAD_STEPS:
            if self.progress_value == value:
                self.status.setText(f"> {msg}")
                break
        if self.progress_value >= 100:
            self.timer.stop()
            QTimer.singleShot(450, self._launch_login)

    def _launch_login(self):
        from login import LoginPage
        self.login_window = LoginPage()
        self.login_window.show()
        self.finish(self.login_window)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sentinel Surveillance System")
    app.setStyle("Fusion")

    # --- Initialize persistence ---
    users_db.init_db()
    users_db.seed_demo_users()
    users_db.seed_demo_events()

    splash = SplashWindow()
    splash.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
