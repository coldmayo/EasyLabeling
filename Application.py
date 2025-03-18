from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = "arcs.png"
        self.setWindowTitle("Label Images")

        widg = QWidget()
        self.setCentralWidget(widg)

        layout = QVBoxLayout()
        self.im_label = QLabel()

        pixmap = QPixmap("arcs.png");
        if pixmap.isNull():
            print("Failed to load image")

        self.open_file_exp_button = QPushButton("Find Picture")
        self.open_file_exp_button.clicked.connect(self.open_file_exp) 

        self.im_label.setPixmap(pixmap)
        layout.addWidget(self.im_label)
        layout.addWidget(self.open_file_exp_button)
        widg.setLayout(layout)

    def update_image(self):
        pixmap = QPixmap(self.file_path)
        if pixmap.isNull():
            print("Failed to load image")
        else:
            self.im_label.setPixmap(pixmap)

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
