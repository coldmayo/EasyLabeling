from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMessageBox
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
        self.on_box_right_clicked = None
        self.on_before_draw = None   # called on mouse-press; return value is a "before" snapshot
        self.on_box_drawn = None     # called on mouse-release if a real box was drawn
        self._pre_draw_snapshot = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start = self.mapToScene(event.position().toPoint())
            self.end = self.start
            self._pre_draw_snapshot = self.on_before_draw() if self.on_before_draw else None
            self.current_rect = self.scene().addRect(QRectF(self.start, self.start), QPen(Qt.GlobalColor.red), QBrush(Qt.BrushStyle.NoBrush))
        elif event.button() == Qt.MouseButton.RightButton:
            click_point = self.mapToScene(event.position().toPoint())
            if self.on_box_right_clicked:
                for item in self.scene().items():
                    if isinstance(item, QGraphicsRectItem):
                        if item.rect().contains(click_point):
                            self.on_box_right_clicked(item)
                            break

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
                if self.on_box_drawn:
                    self.on_box_drawn(self._pre_draw_snapshot)
