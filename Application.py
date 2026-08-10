from PyQt6.QtWidgets import QApplication, QGraphicsRectItem, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QGraphicsView, QDialog, QComboBox, QFormLayout, QDialogButtonBox, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF

import json
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from Draw import *

# classes:
# 1: alpha
# 2: beta
# 3: muon

def datasetInfo(imageData, annotData):
    return {"categories": [{"id": 1,"name": "alpha"}, {"id": 2, "name": "beta"}, {"id": 3, "name": "muon"}],"images": imageData,"annotations": annotData}

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

class NoTracksWarning(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("No Tracks Labeled")

        layout = QVBoxLayout()

        warning = QLabel("You haven't labeled any tracks on this image yet. Switch pictures anyway?")
        layout.addWidget(warning)

        switch_btn = QPushButton("Switch Anyway")
        switch_btn.clicked.connect(self.accept)
        layout.addWidget(switch_btn)

        go_back_btn = QPushButton("Go Back")
        go_back_btn.clicked.connect(self.reject)
        layout.addWidget(go_back_btn)

        self.setLayout(layout)


class SaveTheData(QDialog):
    def __init__(self, imgdata, annotdata):
        super().__init__()

        self.json_path = "data.json"
        self.imgdata = imgdata
        self.annotdata = annotdata

        self.setWindowTitle("Warning...")

        layout = QVBoxLayout()

        warning = QLabel("Yo, you forgot to save your annotations before switching to a new file")
        layout.addWidget(warning)

        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

        ignore_btn = QPushButton("Ignore")
        ignore_btn.clicked.connect(self.accept)
        layout.addWidget(ignore_btn)

        self.setLayout(layout)

    def save_and_close(self):
        return self.save_coco_json(self.imgdata, self.annotdata)

    def save_coco_json(self, imgd, ad):
        with open(self.json_path, 'w') as f:
            json_o = json.dump(datasetInfo(imgd, ad), f)
        return self.accept()

class LabelPopup(QDialog):
    def __init__(self, bbox):
        super().__init__()

        self.setWindowTitle("Label Bounding Box")
        
        self.bbox = bbox
        self.label = None

        layout = QFormLayout()

        self.coords = QLabel(
            f"x={bbox[0]}, y={bbox[1]}, "
            f"w={bbox[2]}, h={bbox[3]}"
        )

        self.combo = QComboBox()
        self.combo.addItems(["alpha", "beta", "muon"])

        layout.addRow("Coordinates:", self.coords)
        layout.addRow("Label:", self.combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
            #QDialogButtonBox.StandardButton.
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.setLayout(layout)


    def get_label(self):
        return self.combo.currentText()

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = "CuntSweep.png"
        self.setWindowTitle("Label Images")

        self.json_path = "data.json"

        self.box_labels = {}

        widg = QWidget()
        self.setCentralWidget(widg)

        layout = QVBoxLayout()
        self.image = QGraphicsScene()
        self.view = DrawingView(self.image)
        self.view.on_box_clicked = self.box_clicked
        self.update_image()

        self.open_file_exp_button = QPushButton("Find Picture")
        self.open_file_exp_button.clicked.connect(self.open_file_exp)
        self.saved_anns = False
        self.heard_warning = False
        
        # self.show_bbox_button = QPushButton("Select bbox")
        # self.show_bbox_button.clicked.connect(self.enable_selection)

        exit_button = QPushButton("Exit App")
        exit_button.clicked.connect(self.close)
        
        self.clear_rects_button = QPushButton("Clear boxes")
        self.clear_rects_button.clicked.connect(self.clear_drawings)

        self.save_to_json = QPushButton("Save Data")
        self.save_to_json.clicked.connect(self.save_coco_json)

        #self.check_plot_button = QPushButton("Check bbox with Matplotlib")
        #self.check_plot_button.clicked.connect(self.test_bbox)

        layout.addWidget(self.view)
        layout.addWidget(self.open_file_exp_button)
        #layout.addWidget(self.show_bbox_button)
        #layout.addWidget(self.check_plot_button)
        layout.addWidget(self.save_to_json)
        layout.addWidget(self.clear_rects_button)

        layout.addWidget(exit_button)

        widg.setLayout(layout)

    def test_bbox(self):
        bbox, labels = self.rect_bounds()
        img = mpimg.imread(self.file_path)
        imgplot = plt.imshow(img)

        for i in bbox:
            plt.plot(*bbox_to_rect(i), color='purple')
        plt.show()

    def data_for_save(self):
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
        for d, l in data:
            annotData.append({"id": j, "category_id": l, "bbox": d, "iscrowd": 0, "image_id":i, "area":d[2]*d[2]})
            j += 1
        return imageData, annotData

    def save_coco_json(self):
        imageData, annotData = self.data_for_save()

        with open(self.json_path, 'w') as f:
            json_o = json.dump(datasetInfo(imageData, annotData), f)

        self.saved_anns = True

    def print_bbox(self):
        bounds = self.rect_bounds()
        print(bounds)

    def enable_selection(self):
        self.selecting = True
        for item in self.image.items():
            if isinstance(item, QGraphicsRectItem):
                item.setAcceptHoverEvents(True)
                item.mousePressEvent = lambda event, box=item: self.box_clicked(event, box)

    def box_clicked(self, box):

        rect = box.rect()
        bbox = [rect.x(), rect.y(), rect.width(), rect.height()]

        popup = LabelPopup(bbox)

        if popup.exec():
            label = popup.get_label()
            print("BBox:", bbox, "Label:", label)

            self.box_labels[id(box)] = label

    def rect_bounds(self):
        results = []
        category = {"alpha": 1, "beta": 2, "muon": 3}
        for i in self.image.items():
            if isinstance(i, QGraphicsRectItem):
                rect = i.rect()
                bbox = [rect.x(), rect.y(), rect.width(), rect.height()]
                label_str = self.box_labels.get(id(i), "alpha")  # default alpha
                label_id = category[label_str]
                results.append((bbox, label_id))
        return results

    def update_image(self):
        pixmap = QPixmap(self.file_path)
        if pixmap.isNull():
            print("Failed to load image")
        else:
            self.image.clear()
            self.image.addPixmap(pixmap)

    def dataForImg(self):   # do we have data on this image in the dataset already?
        try:
            with open(self.json_path, 'r') as f:
                old_data = json.load(f)
            for ims in old_data["images"]:
                if ims["file_name"] == self.file_path:
                    return True
            return False

        except FileNotFoundError:
            return False

    def open_file_exp(self):
        file_dia = QFileDialog()
        has_tracks = len(self.rect_bounds()) > 0

        if self.saved_anns == True or self.dataForImg() == True or self.heard_warning == True:
            proceed = True
        elif has_tracks:
            # tracks were drawn but not saved yet - warn before losing them
            imgd, ad = self.data_for_save()
            warn = SaveTheData(imgd, ad)
            warn.exec()
            # Save and Ignore both call accept(), so either way we move on
            proceed = True
        else:
            # no tracks drawn on this image at all - confirm before switching
            warn = NoTracksWarning()
            proceed = warn.exec() == QDialog.DialogCode.Accepted

        if proceed:
            file_path, _ = file_dia.getOpenFileName(
                self,
                "Select an Image"
                "Images (*.png *.jpg *.bmp);;All Files (*)"
            )

            if file_path:
                self.file_path = file_path
                self.update_image()
                self.box_labels = {}
                self.heard_warning = False
                self.saved_anns = False


    def clear_drawings(self):
        for item in self.image.items():
            if not isinstance(item, QGraphicsPixmapItem):
                self.box_labels.pop(id(item), None)
                self.image.removeItem(item)
