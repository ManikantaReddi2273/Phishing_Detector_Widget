from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSlot, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QRegion, QPen
import time


class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.last_risk = "low"
        self.last_confidence = 0.0
        self.last_reasons = []
        self.last_update_time = 0

        self.details_label = None
        self.current_risk = "low"

        # Dragging state
        self._drag_active = False
        self._drag_offset = None

        # Hover state
        self._hovered = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Phishing Guard")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # ---------- Status ----------
        self.status_label = QLabel("🟢 Safe")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold;")

        # ---------- Buttons ----------
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_status)

        self.info_btn = QPushButton("ⓘ")
        self.info_btn.setFixedSize(34, 34)
        self.info_btn.clicked.connect(self.toggle_details)
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 17px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.08);
            }
        """)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.pause_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.info_btn)

        # ---------- Layout ----------
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        # 🔵 IMPORTANT: make widget square
        self.setFixedSize(160, 160)
        self.move(50, 50)

        # Apply circular mask
        self.apply_circular_mask()

        self.apply_style("low", 0.0)

    # -------------------------
    # 🔵 Circular mask
    # -------------------------
    def apply_circular_mask(self):
        radius = self.width()
        region = QRegion(QRect(0, 0, radius, radius), QRegion.Ellipse)
        self.setMask(region)

    # -------------------------
    # Hover support
    # -------------------------
    def enterEvent(self, event):
        self._hovered = True
        try:
            self.setCursor(Qt.OpenHandCursor)
        except Exception:
            pass
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        try:
            self.setCursor(Qt.ArrowCursor)
        except Exception:
            pass
        self.update()
        super().leaveEvent(event)

    # -------------------------
    # Drag support
    # -------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            # don't start dragging when clicking on buttons or controls
            if child and isinstance(child, QPushButton):
                super().mousePressEvent(event)
                return

            self._drag_active = True
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if getattr(self, "_drag_active", False) and (event.buttons() & Qt.LeftButton):
            try:
                new_pos = event.globalPos() - self._drag_offset
                self.move(new_pos)
            except Exception:
                pass
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if getattr(self, "_drag_active", False):
            self._drag_active = False
            self._drag_offset = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # -------------------------
    # 🎨 Paint background circle
    # -------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color_map = {
            "low": QColor("#1b5e20"),
            "medium": QColor("#f9a825"),
            "high": QColor("#b71c1c"),
            "scanning": QColor("#424242")
        }

        painter.setBrush(color_map.get(self.current_risk, QColor("#1b5e20")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())

        # subtle hover highlight (ring)
        if getattr(self, "_hovered", False):
            pen = QPen(QColor(255, 255, 255, 60))
            pen.setWidth(6)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            inset = 6
            painter.drawEllipse(self.rect().adjusted(inset, inset, -inset, -inset))

    # -------------------------
    # Pause / Resume
    # -------------------------
    def toggle_status(self):
        if self.pause_btn.text() == "Pause":
            self.pause_btn.setText("Resume")
            self.status_label.setText("⏸ Paused")
            self.current_risk = "scanning"
            self.update()
        else:
            self.pause_btn.setText("Pause")
            self.apply_style(self.last_risk, self.last_confidence)

    # -------------------------
    # UI update from service
    # -------------------------
    @pyqtSlot(str, float, list)
    def update_ui(self, risk_level, confidence, reasons):
        now = time.time()

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
        self.current_risk = risk_level

        if risk_level == "scanning":
            self.status_label.setText("🔍 Scanning…")

        elif risk_level == "high":
            self.status_label.setText(f"🔴 Phishing ({int(confidence * 100)}%)")

        elif risk_level == "medium":
            self.status_label.setText(f"🟡 Suspicious ({int(confidence * 100)}%)")

        else:
            self.status_label.setText("🟢 Safe")

        self.update()  # repaint circle

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

        self.details_label = QLabel(text)
        self.details_label.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.details_label.setStyleSheet("""
            background-color: #111;
            color: white;
            padding: 8px;
            border-radius: 8px;
            font-size: 11px;
        """)
        self.details_label.adjustSize()

        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.details_label.move(pos)
        self.details_label.show()
