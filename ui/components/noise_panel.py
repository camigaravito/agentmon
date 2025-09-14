from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage
import numpy as np

class NoisePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QLabel("Mapa de visitas", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(300, 300)
        self.label.setStyleSheet(
            "QLabel { background-color: #111; color: #aaa; border: 2px solid #333; border-radius: 4px; }"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.label)

    def set_gray(self, gray: np.ndarray):
        # Recibe un array 2D uint8 y lo dibuja como imagen
        if gray is None or gray.ndim != 2:
            return
        h, w = gray.shape
        # Expandir 2D -> RGB para QImage.Format_RGB888
        rgb = np.repeat(gray[:, :, None], 3, axis=2).copy()
        qimg = QImage(rgb.data.tobytes(), w, h, 3 * w, QImage.Format.Format_RGB888)
        if qimg.isNull():
            return
        pm = QPixmap.fromImage(qimg).scaled(
            QSize(300, 300),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label.setPixmap(pm)