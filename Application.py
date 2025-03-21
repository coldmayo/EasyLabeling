from PyQt6.QtWidgets import QApplication, QGraphicsRectItem, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QGraphicsView
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF

import json
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from Draw import *

def datasetInfo(imageData, annotData):
    return {"categories": [{"id": 1,"name": "track"}],"images": imageData,"annotations": annotData}

def bbox_to_rect(bboxparam):
    # Convert the bounding box to 4 lines in matplotlib to visualize it. boundingbox=[min_x,min_y,max_x,max_y]
    #in matplotlib line=start_x,end_x,start_y,end_y
    #so line by line: lowerline=[x1,x2],[y1,y1] #upperline=[x1,x2],[y2,y2] #leftsideline=[x1,x1],[y1,y2] #rightsideline=[x2,x2],[y1,y2]
        y1=bboxparam[1]
        y2=bboxparam[3]+y1
        x1=bboxparam[0]
        x2=bboxparam[2]+x1
        boxlines=[x1,x2],[y1,y1],[x1,x2],[y2,y2],[x1,x1],[y1,y2],[x2,x2],[y1,y2]
        #to visualize use: matplotlib.plot(*bbox_to_rect(boundingbox),color='green')  on the same plot where imshow shows the mask
        return boxlines

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = "CuntSweep.png"
        self.setWindowTitle("Label Images")

        self.json_path = "data.json"

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

        self.save_to_json = QPushButton("Save Data")
        self.save_to_json.clicked.connect(self.save_coco_json)

        #self.check_plot_button = QPushButton("Check bbox with Matplotlib")
        #self.check_plot_button.clicked.connect(self.test_bbox)

        layout.addWidget(self.view)
        layout.addWidget(self.open_file_exp_button)
        layout.addWidget(self.show_bbox_button)
        #layout.addWidget(self.check_plot_button)
        layout.addWidget(self.save_to_json)
        layout.addWidget(self.clear_rects_button)
        widg.setLayout(layout)

    def test_bbox(self):
        bbox = self.rect_bounds()
        img = mpimg.imread(self.file_path)
        imgplot = plt.imshow(img)

        for i in bbox:
            plt.plot(*bbox_to_rect(i), color='purple')
        plt.show()

    def save_coco_json(self):
        image = Image.open(self.file_path)
        w, h = image.size
        data = self.rect_bounds()
        annotData = []
        imageData = []

        last_im_id = 0
        last_a_id = 0

        try:
            with open(self.json_path, 'r') as f:
                old_data = json.load(f)
            for ims in old_data["images"]:
                last_im_id = ims["id"]
                imageData.append(ims)

            for annot in old_data["annotations"]:
                last_a_id = annot["id"]
                annotData.append(annot)

            i = last_im_id + 1
            j = last_a_id + 1

        except FileNotFoundError:
            i = 0; j = 0
            print("making file...")
        
        
        imageData.append({"id": i, "width": w, "height": h, "file_name":self.file_path})
        for d in data:
            annotData.append({"id": j, "category_id":1, "bbox": d, "iscrowd": 0, "image_id":i, "area":d[2]*d[2]})
            j += 1
        print("done")
        with open(self.json_path, 'w') as f:
            json_o = json.dump(datasetInfo(imageData, annotData), f)

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
