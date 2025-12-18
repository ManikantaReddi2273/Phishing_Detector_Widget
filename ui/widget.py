from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSlot
import time


class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.last_risk = "low"
        self.last_confidence = 0.0
        self.last_reasons = []
        self.last_update_time = 0

        self.details_label = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Phishing Guard")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_StyledBackground, True)

        # -------- Status --------
        self.status_label = QLabel("🟢 Safe")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold;")

        # -------- Buttons --------
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_status)

        self.info_btn = QPushButton("ⓘ")
        self.info_btn.setFixedSize(32, 28)
        self.info_btn.clicked.connect(self.toggle_details)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.pause_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.info_btn)

        # -------- Layout --------
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(self.status_label)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        # 🔑 IMPORTANT: height increased
        self.setFixedSize(220, 120)
        self.move(50, 50)

        self.apply_style("low", 0.0)

    # -------------------------
    # Pause / Resume
    # -------------------------
    def toggle_status(self):
        if self.pause_btn.text() == "Pause":
            self.pause_btn.setText("Resume")
            self.status_label.setText("⏸ Paused")
            self.setStyleSheet("background-color: #555; color: white;")
        else:
            self.pause_btn.setText("Pause")
            self.apply_style(self.last_risk, self.last_confidence)

    # -------------------------
    # UI update from service
    # -------------------------
    @pyqtSlot(str, float, list)
    def update_ui(self, risk_level, confidence, reasons):
        now = time.time()

        # Anti-flicker
        if self.last_risk in ("high", "medium") and risk_level == "low":
            if now - self.last_update_time < 3:
                return

        self.last_risk = risk_level
        self.last_confidence = confidence
        self.last_reasons = reasons
        self.last_update_time = now

        self.apply_style(risk_level, confidence)

    # -------------------------
    # Visual styles
    # -------------------------
    def apply_style(self, risk_level, confidence):
        if risk_level == "scanning":
            self.setStyleSheet("background-color: #424242; color: white;")
            self.status_label.setText("🔍 Scanning…")

        elif risk_level == "high":
            self.setStyleSheet("background-color: #b71c1c; color: white;")
            self.status_label.setText(f"🔴 Phishing ({int(confidence * 100)}%)")

        elif risk_level == "medium":
            self.setStyleSheet("background-color: #f9a825; color: black;")
            self.status_label.setText(f"🟡 Suspicious ({int(confidence * 100)}%)")

        else:
            self.setStyleSheet("background-color: #1b5e20; color: white;")
            self.status_label.setText("🟢 Safe")

        if self.details_label:
            self.details_label.hide()

    # -------------------------
    # Details panel (ⓘ)
    # -------------------------
    def toggle_details(self):
        if not self.last_reasons:
            return

        if self.details_label and self.details_label.isVisible():
            self.details_label.hide()
            return

        text = f"Risk: {self.last_risk.upper()}\n"
        text += f"Confidence: {int(self.last_confidence * 100)}%\n\n"

        for r in self.last_reasons:
            text += f"• {r}\n"

        self.details_label = QLabel(text, self)
        self.details_label.setStyleSheet("""
            background-color: #111;
            color: white;
            padding: 8px;
            border-radius: 6px;
            font-size: 11px;
        """)
        self.details_label.move(0, self.height())
        self.details_label.adjustSize()
        self.details_label.show()
