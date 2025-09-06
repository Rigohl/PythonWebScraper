import math

from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget


class RobotFaceWidget(QWidget):
    """Enhanced humanoid/transformer robot face with advanced animations.
    The face reacts to activity level (0..1) via eye glow, facial expressions,
    and transformer-inspired metallic elements.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._activity = 0.0
        self._phase = 0.0
        self._blink_phase = 0.0
        self._pulse_phase = 0.0
        self._expression_state = "neutral"  # neutral, thinking, alert
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)
        self.setMinimumHeight(220)

        # Random blink timing
        self._next_blink = 100 + (hash(str(self)) % 50)
        self._blink_counter = 0
        self._is_blinking = False
        self._blink_duration = 10

        # Transformer panel segments
        self._segments = []
        for i in range(8):
            self._segments.append(0.2 + (hash(str(i)) % 100) / 200.0)

    def set_activity(self, value: float):
        self._activity = max(0.0, min(1.0, value))

        # Update expression based on activity
        if self._activity < 0.3:
            self._expression_state = "neutral"
        elif self._activity < 0.7:
            self._expression_state = "thinking"
        else:
            self._expression_state = "alert"

        self.update()

    def _tick(self):
        self._phase = (self._phase + 0.05) % (2 * math.pi)
        self._pulse_phase = (self._pulse_phase + 0.03) % (2 * math.pi)

        # Blink logic
        self._blink_counter += 1
        if self._blink_counter >= self._next_blink:
            self._is_blinking = True
            self._blink_phase = 0
            self._blink_counter = 0
            self._next_blink = 70 + (hash(str(self._phase)) % 50)

        if self._is_blinking:
            self._blink_phase += 0.2
            if self._blink_phase >= math.pi:
                self._is_blinking = False

        # Update transformer panels
        for i in range(len(self._segments)):
            self._segments[i] = (
                0.2 + 0.3 * (math.sin(self._phase * (0.5 + i * 0.2) + i) + 1) / 2
            )

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        face_r = int(min(w, h) * 0.4)

        # Create metallic background gradient
        bg_gradient = QLinearGradient(
            cx - face_r, cy - face_r, cx + face_r, cy + face_r
        )
        bg_gradient.setColorAt(0.0, QColor(40, 45, 60))
        bg_gradient.setColorAt(0.4, QColor(65, 75, 95))
        bg_gradient.setColorAt(0.6, QColor(50, 60, 80))
        bg_gradient.setColorAt(1.0, QColor(30, 35, 50))

        # Face plate - more humanoid with transformer elements
        p.setBrush(bg_gradient)
        p.setPen(QPen(QColor(100, 150, 220, 200), 2))

        # More humanoid face shape (less rectangular, more oval)
        face_path = QPainterPath()
        face_path.addRoundedRect(
            QRectF(cx - face_r, cy - face_r * 1.1, face_r * 2, face_r * 2.2),
            face_r * 0.5,
            face_r * 0.4,
        )
        p.drawPath(face_path)

        # Transformer plate segments/lines
        p.setPen(QPen(QColor(120, 180, 255, 150), 1))

        # Horizontal plates
        for i in range(4):
            y_pos = cy - face_r * 0.7 + i * face_r * 0.5
            line_width = face_r * (1.0 + 0.3 * math.sin(self._phase * 0.5 + i))
            p.drawLine(
                int(cx - line_width / 2),
                int(y_pos),
                int(cx + line_width / 2),
                int(y_pos),
            )

        # Vertical tech lines
        for i in range(5):
            x_offset = (i - 2) * face_r * 0.4
            height = face_r * self._segments[i % len(self._segments)]
            p.drawLine(
                int(cx + x_offset),
                int(cy - height / 2),
                int(cx + x_offset),
                int(cy + height / 2),
            )

        # Eyes - more human-like with advanced glow effects
        eye_offset_x = face_r * 0.35
        eye_y = cy - face_r * 0.2
        eye_r = face_r * 0.18

        # Eye shape computation with blinking
        if self._is_blinking:
            eye_squeeze = math.sin(self._blink_phase) * eye_r * 0.8
        else:
            eye_squeeze = 0

        # Expression affects eye position
        if self._expression_state == "thinking":
            left_eye_lift = -eye_r * 0.2
            right_eye_lift = eye_r * 0.1
        elif self._expression_state == "alert":
            left_eye_lift = 0
            right_eye_lift = 0
        else:  # neutral
            left_eye_lift = 0
            right_eye_lift = 0

        # Advanced eye glow effect
        pulse = (math.sin(self._pulse_phase) + 1) / 2  # 0..1
        glow = int(120 + (135 * (0.5 * self._activity + 0.5 * pulse)))
        eye_color_outer = QColor(0, glow, 255, 180)
        eye_color_inner = QColor(100, 200, 255, 255)

        # Left eye with glow
        eye_gradient = QRadialGradient(
            cx - eye_offset_x, eye_y + left_eye_lift, eye_r * 1.5
        )
        eye_gradient.setColorAt(0.0, eye_color_inner)
        eye_gradient.setColorAt(0.5, eye_color_outer)
        eye_gradient.setColorAt(1.0, QColor(0, 0, 100, 0))

        # Draw eye glow
        p.setBrush(eye_gradient)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(
            int(cx - eye_offset_x - eye_r * 1.5),
            int(eye_y + left_eye_lift - eye_r * 1.5),
            int(eye_r * 3),
            int(eye_r * 3),
        )

        # Right eye with glow
        eye_gradient = QRadialGradient(
            cx + eye_offset_x, eye_y + right_eye_lift, eye_r * 1.5
        )
        eye_gradient.setColorAt(0.0, eye_color_inner)
        eye_gradient.setColorAt(0.5, eye_color_outer)
        eye_gradient.setColorAt(1.0, QColor(0, 0, 100, 0))

        p.setBrush(eye_gradient)
        p.drawEllipse(
            int(cx + eye_offset_x - eye_r * 1.5),
            int(eye_y + right_eye_lift - eye_r * 1.5),
            int(eye_r * 3),
            int(eye_r * 3),
        )

        # Actual eyes (more oval/human-like)
        p.setBrush(eye_color_inner)
        p.setPen(QPen(QColor(150, 220, 255), 1))

        # Left eye with blink
        p.drawEllipse(
            int(cx - eye_offset_x - eye_r / 2),
            int(eye_y + left_eye_lift - eye_r / 2 + eye_squeeze),
            int(eye_r),
            int(eye_r - eye_squeeze * 2),
        )

        # Right eye with blink
        p.drawEllipse(
            int(cx + eye_offset_x - eye_r / 2),
            int(eye_y + right_eye_lift - eye_r / 2 + eye_squeeze),
            int(eye_r),
            int(eye_r - eye_squeeze * 2),
        )

        # Eye pupils (follow activity level)
        p.setBrush(QColor(0, 0, 40))
        pupil_r = eye_r * 0.4

        # Pupil positions follow activity - more dynamic
        pupil_x_offset = eye_r * 0.2 * math.sin(self._phase * 0.5)
        pupil_y_offset = eye_r * 0.1 * math.sin(self._phase * 0.7 + 1)

        # Left pupil
        p.drawEllipse(
            int(cx - eye_offset_x - pupil_r / 2 + pupil_x_offset),
            int(eye_y + left_eye_lift - pupil_r / 2 + pupil_y_offset),
            int(pupil_r),
            int(pupil_r),
        )

        # Right pupil
        p.drawEllipse(
            int(cx + eye_offset_x - pupil_r / 2 + pupil_x_offset),
            int(eye_y + right_eye_lift - pupil_r / 2 + pupil_y_offset),
            int(pupil_r),
            int(pupil_r),
        )

        # Mouth / status bar - more humanoid with expressions
        mouth_y = cy + face_r * 0.3
        mouth_w = face_r * 1.1
        mouth_h = face_r * 0.18

        # Expression affects mouth shape
        if self._expression_state == "thinking":
            mouth_h *= 0.7
            mouth_curve = 8
        elif self._expression_state == "alert":
            mouth_h *= 1.2
            mouth_curve = 12
        else:  # neutral
            mouth_curve = 10

        # Mouth background with metallic effect
        mouth_gradient = QLinearGradient(
            cx - mouth_w / 2, mouth_y, cx + mouth_w / 2, mouth_y
        )
        mouth_gradient.setColorAt(0.0, QColor(30, 40, 55))
        mouth_gradient.setColorAt(0.5, QColor(20, 25, 40))
        mouth_gradient.setColorAt(1.0, QColor(30, 40, 55))

        p.setBrush(mouth_gradient)
        p.setPen(QPen(QColor(0, 120, 180, 200), 2))
        p.drawRoundedRect(
            int(cx - mouth_w / 2),
            int(mouth_y - mouth_h / 2),
            int(mouth_w),
            int(mouth_h),
            mouth_curve,
            mouth_curve,
        )

        # Activity meter inside mouth (energy level visualization)
        activity_gradient = QLinearGradient(
            cx - mouth_w / 2, mouth_y, cx + mouth_w / 2, mouth_y
        )
        activity_gradient.setColorAt(0.0, QColor(0, 140, 200))
        activity_gradient.setColorAt(0.5, QColor(0, 180, 240))
        activity_gradient.setColorAt(1.0, QColor(100, 220, 255))

        p.setBrush(activity_gradient)
        p.setPen(Qt.PenStyle.NoPen)

        fill_w = mouth_w * (0.05 + 0.95 * self._activity)
        p.drawRoundedRect(
            int(cx - mouth_w / 2),
            int(mouth_y - mouth_h / 2),
            int(fill_w),
            int(mouth_h),
            mouth_curve - 2,
            mouth_curve - 2,
        )

        # Add pulsing energy lines in the mouth
        if self._activity > 0.3:
            p.setPen(QPen(QColor(200, 240, 255, 150), 1))
            line_count = int(3 + self._activity * 4)
            for i in range(line_count):
                x_pos = cx - mouth_w / 2 + fill_w * i / line_count
                p.drawLine(
                    int(x_pos),
                    int(mouth_y - mouth_h * 0.4),
                    int(x_pos),
                    int(mouth_y + mouth_h * 0.4),
                )

        # Forehead plate - transformer inspired
        plate_w = face_r * 1.4
        plate_h = face_r * 0.3
        plate_y = cy - face_r * 0.7

        p.setBrush(QColor(45, 60, 80))
        p.setPen(QPen(QColor(100, 160, 220), 1.5))
        p.drawRoundedRect(
            int(cx - plate_w / 2),
            int(plate_y - plate_h / 2),
            int(plate_w),
            int(plate_h),
            8,
            8,
        )

        # Plate details
        p.setPen(QPen(QColor(0, 140, 220), 1))
        segment_width = plate_w / 7
        for i in range(1, 7):
            x = cx - plate_w / 2 + i * segment_width
            p.drawLine(
                int(x),
                int(plate_y - plate_h * 0.4),
                int(x),
                int(plate_y + plate_h * 0.4),
            )

        # Plate glowing elements
        for i in range(3):
            led_x = cx - plate_w * 0.35 + i * plate_w * 0.35
            led_y = plate_y
            led_size = plate_h * 0.3
            led_color = QColor(
                0, 180, 255, 100 + int(155 * ((math.sin(self._phase * 2 + i) + 1) / 2))
            )

            p.setBrush(led_color)
            p.setPen(QPen(QColor(100, 200, 255), 1))
            p.drawEllipse(
                int(led_x - led_size / 2),
                int(led_y - led_size / 2),
                int(led_size),
                int(led_size),
            )

        # Title with metallic gradient
        title_gradient = QLinearGradient(0, 0, w, 0)
        title_gradient.setColorAt(0.0, QColor(100, 180, 220))
        title_gradient.setColorAt(0.5, QColor(160, 220, 250))
        title_gradient.setColorAt(1.0, QColor(100, 180, 220))

        p.setPen(title_gradient)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(
            0,
            4,
            w,
            24,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            "HYBRID BRAIN INTERFACE",
        )

        p.end()
