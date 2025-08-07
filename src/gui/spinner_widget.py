#spinner_widget

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen

class Spinner(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)
        self.setFixedSize(36, 36)  # Adjustable size

    def rotate(self):
        self.angle = (self.angle + 15) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.blue, 4)
        painter.setPen(pen)
        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.drawArc(rect, self.angle * 16, 120 * 16)