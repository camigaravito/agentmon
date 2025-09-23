from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage
import numpy as np

class NoisePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(300, 300)
        self.label.setStyleSheet(
            "QLabel { background-color: #ffffff; color: #666; border: 1px solid #ccc; }"
        )
        self.label.setText("Mapa de visitas")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.label)

    def set_gray(self, gray: np.ndarray):
        if gray is None or gray.ndim != 2:
            return
        img = np.ascontiguousarray(gray)
        h, w = img.shape
        rgb = np.repeat(img[:, :, None], 3, axis=2)
        qimg = QImage(rgb.data.tobytes(), w, h, 3 * w, QImage.Format.Format_RGB888)
        if qimg.isNull():
            return
        pm = QPixmap.fromImage(qimg).scaled(
            QSize(300, 300),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label.setPixmap(pm)
        if self.label.text():
            self.label.setText("")