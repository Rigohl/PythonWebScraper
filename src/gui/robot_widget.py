from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget
import math

class RobotFaceWidget(QWidget):
    """Simple animated robot face placeholder with future hooks.
    The face reacts subtly to activity level (0..1) via eye glow.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._activity = 0.0
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(60)
        self.setMinimumHeight(180)

    def set_activity(self, value: float):
        self._activity = max(0.0, min(1.0, value))
        self.update()

    def _tick(self):
        self._phase = (self._phase + 0.05) % (2*math.pi)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        face_r = int(min(w, h) * 0.4)

        # Face background
        p.setBrush(QColor(20, 35, 46))
        p.setPen(QPen(QColor(70, 120, 140), 2))
        p.drawRoundedRect(int(cx - face_r), int(cy - face_r), int(2*face_r), int(2*face_r), 18, 18)

        # Eyes
        eye_offset_x = face_r * 0.45
        eye_y = cy - face_r * 0.2
        eye_r = face_r * 0.18
        pulse = (math.sin(self._phase) + 1)/2  # 0..1
        glow = int(120 + (135 * (0.3*self._activity + 0.7*pulse)))
        eye_color = QColor(0, glow, 255)
        p.setBrush(eye_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - eye_offset_x - eye_r/2), int(eye_y - eye_r/2), int(eye_r), int(eye_r))
        p.drawEllipse(int(cx + eye_offset_x - eye_r/2), int(eye_y - eye_r/2), int(eye_r), int(eye_r))

        # Mouth / status bar
        mouth_y = cy + face_r * 0.3
        mouth_w = face_r * 1.1
        mouth_h = face_r * 0.18
        p.setBrush(QColor(10, 20, 25))
        p.setPen(QPen(QColor(0, 120, 160), 2))
        p.drawRoundedRect(int(cx - mouth_w/2), int(mouth_y - mouth_h/2), int(mouth_w), int(mouth_h), 8, 8)

        # Activity meter inside mouth
        p.setBrush(QColor(0, 180, 200))
        p.setPen(Qt.PenStyle.NoPen)
        fill_w = mouth_w * (0.05 + 0.95*self._activity)
        p.drawRoundedRect(int(cx - mouth_w/2), int(mouth_y - mouth_h/2), int(fill_w), int(mouth_h), 6, 6)

        # Title
        p.setPen(QColor(100, 220, 230))
        font = QFont("Consolas", 10, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(0, 4, w, 24, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "HYBRID BRAIN INTERFACE")

        p.end()
