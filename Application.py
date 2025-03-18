from PyQt6.QtWidgets import QApplication, QGraphicsRectItem, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QGraphicsView
from PyQt6.QtGui import QPixmap

from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF

from Draw import *

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = "arcs.png"
        self.setWindowTitle("Label Images")

        widg = QWidget()
        self.setCentralWidget(widg)

        layout = QVBoxLayout()
        self.image = QGraphicsScene()
        self.view = DrawingView(self.image)
        self.update_image()

        self.open_file_exp_button = QPushButton("Find Picture")
        self.open_file_exp_button.clicked.connect(self.open_file_exp)
        self.show_bbox_button = QPushButton("Show bbox")
        self.show_bbox_button.clicked.connect(self.print_bbox)
        self.clear_rects_button = QPushButton("Clear boxes")
        self.clear_rects_button.clicked.connect(self.clear_drawings)

        layout.addWidget(self.view)
        layout.addWidget(self.open_file_exp_button)
        layout.addWidget(self.show_bbox_button)
        layout.addWidget(self.clear_rects_button)
        widg.setLayout(layout)

    def print_bbox(self):
        bounds = self.rect_bounds()
        print(bounds)

    def rect_bounds(self):
        bounds = []
        for i in self.image.items():
            if isinstance(i, QGraphicsRectItem):
                rect = i.rect()

                bounds.append([rect.x(), rect.y(), rect.width(), rect.height()])
        return bounds

    def update_image(self):
        pixmap = QPixmap(self.file_path)
        if pixmap.isNull():
            print("Failed to load image")
        else:
            self.image.clear()
            self.image.addPixmap(pixmap)

    def open_file_exp(self):
        file_dia = QFileDialog()
        file_path, _ = file_dia.getOpenFileName(
            self,
            "Select an Image"
            "Images (*.png *.jpg *.bmp);;All Files (*)"
        )

        if file_path:
            self.file_path = file_path
            self.update_image()

    def clear_drawings(self):
        for item in self.image.items():
            if not isinstance(item, QGraphicsPixmapItem):
                self.image.removeItem(item)
