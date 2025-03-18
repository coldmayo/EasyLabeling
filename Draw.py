from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF

class DrawingView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.drawing = False
        self.start = QPointF()
        self.current_rect = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start = self.mapToScene(event.position().toPoint())
            self.current_rect = self.scene().addRect(QRectF(self.start, self.start), QPen(Qt.GlobalColor.red), QBrush(Qt.BrushStyle.NoBrush))

    def mouseMoveEvent(self, event):
        if self.drawing and self.current_rect:
            end_point = self.mapToScene(event.position().toPoint())
            rect = QRectF(self.start, end_point).normalized()
            self.current_rect.setRect(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.current_rect = None
