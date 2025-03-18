import sys
from PyQt6.QtGui import QPixmap, QScreen
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QDialog
from Application import *

def main(argc, argv):
    app = QApplication(argv)

    window = Application()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
