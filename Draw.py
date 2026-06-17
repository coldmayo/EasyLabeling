from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF

class DrawingView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.drawing = False
        self.start = QPointF()
        self.end = QPointF()
        self.current_rect = None
        self.on_box_clicked = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start = self.mapToScene(event.position().toPoint())
            self.end = self.start
            self.current_rect = self.scene().addRect(QRectF(self.start, self.start), QPen(Qt.GlobalColor.red), QBrush(Qt.BrushStyle.NoBrush))

    def mouseMoveEvent(self, event):
        if self.drawing and self.current_rect:
            self.end = self.mapToScene(event.position().toPoint())
            rect = QRectF(self.start, self.end).normalized()
            self.current_rect.setRect(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

            # If start ~ end, it's a click not a drag — find the box under cursor
            delta = self.end - self.start
            is_click = abs(delta.x()) < 5 and abs(delta.y()) < 5

            if is_click:
                # Remove the tiny accidental rect that was created on press
                if self.current_rect:
                    self.scene().removeItem(self.current_rect)
                    self.current_rect = None

                # Find which existing rect contains the click point
                if self.on_box_clicked:
                    for item in self.scene().items():
                        if isinstance(item, QGraphicsRectItem):
                            if item.rect().contains(self.start):
                                self.on_box_clicked(item)
                                break
            else:
                self.current_rect = None
