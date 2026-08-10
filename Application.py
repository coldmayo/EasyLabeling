from PyQt6.QtWidgets import QApplication, QGraphicsRectItem, QGraphicsScene, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QGraphicsView, QDialog, QComboBox, QFormLayout, QDialogButtonBox, QGraphicsPixmapItem, QGraphicsTextItem
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush, QKeySequence, QShortcut
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
        self.file_path = None
        self.setWindowTitle("Label Images")

        self.json_path = "data.json"

        self.undo_stack = []
        self.redo_stack = []

        self.box_labels = {}

        widg = QWidget()
        self.setCentralWidget(widg)

        layout = QVBoxLayout()
        self.image = QGraphicsScene()
        self.view = DrawingView(self.image)
        self.view.on_box_clicked = self.box_clicked
        self.view.on_before_draw = self._snapshot
        self.view.on_box_drawn = self.commit_draw
        self.view.on_box_right_clicked = self.delete_box
        self.update_image()

        placeholder_text = self.image.addText("Please select an image using the 'Find Picture' button.")
        placeholder_text.setDefaultTextColor(QColor("gray"))
        # Center the text loosely in the initial view area
        placeholder_text.setPos(50, 50)

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

        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)

        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo)

        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self.redo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)


        #self.check_plot_button = QPushButton("Check bbox with Matplotlib")
        #self.check_plot_button.clicked.connect(self.test_bbox)

        layout.addWidget(self.view)
        layout.addWidget(self.open_file_exp_button)
        #layout.addWidget(self.show_bbox_button)
        #layout.addWidget(self.check_plot_button)
        layout.addWidget(self.save_to_json)
        layout.addWidget(self.clear_rects_button)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.redo_button)

        layout.addWidget(exit_button)

        widg.setLayout(layout)

    def load_existing_annotations(self):
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        image_id = None
        for ims in data.get("images", []):
            if ims["file_name"] == self.file_path:
                image_id = ims["id"]
                break

        if image_id is None:
            return

        category_mapping = {1: "alpha", 2: "beta", 3: "muon"}

        for annot in data.get("annotations", []):
            if annot["image_id"] == image_id:
                bbox = annot["bbox"]  # [x, y, width, height]
                cat_id = annot["category_id"]
                label_str = category_mapping.get(cat_id, "alpha")

                rect_item = self.image.addRect(
                    QRectF(bbox[0], bbox[1], bbox[2], bbox[3]),
                    QPen(QColor("blue"), 2),
                    QBrush(Qt.BrushStyle.NoBrush)
                )
                
                # Make the rect item selectable/interactable if needed
                rect_item.setAcceptHoverEvents(True)

                # Store the label in your tracking dictionary
                self.box_labels[id(rect_item)] = label_str

                # Add the text label below the box
                text_item = QGraphicsTextItem(label_str, rect_item)
                text_item.setPos(bbox[0], bbox[1] + bbox[3])
                text_item.setDefaultTextColor(QColor("magenta"))

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
            self.push_undo()

            label = popup.get_label()
            print("BBox:", bbox, "Label:", label)

            self.box_labels[id(box)] = label
            self.saved_anns = False

            for child in box.childItems():
                if isinstance(child, QGraphicsTextItem):
                    self.image.removeItem(child)

            text_item = QGraphicsTextItem(label, box)
            text_item.setPos(rect.x(), rect.y() + rect.height())
            text_item.setDefaultTextColor(QColor("magenta"))

    def delete_box(self, box):
        confirm = QMessageBox.question(
            self,
            "Delete Box",
            "Delete this bounding box?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.push_undo()

        for child in box.childItems():
            if isinstance(child, QGraphicsTextItem):
                self.image.removeItem(child)

        self.box_labels.pop(id(box), None)
        self.image.removeItem(box)
        self.saved_anns = False


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

    def _snapshot(self):
        boxes = []
        for item in self.image.items():
            if isinstance(item, QGraphicsRectItem):
                rect = item.rect()
                boxes.append({
                    "x": rect.x(), "y": rect.y(),
                    "w": rect.width(), "h": rect.height(),
                    "pen": QPen(item.pen()),
                    "brush": QBrush(item.brush()),
                    "label": self.box_labels.get(id(item), "alpha"),
                })
        return boxes

    def _restore(self, snapshot):
        for item in list(self.image.items()):
            if isinstance(item, QGraphicsRectItem):
                self.image.removeItem(item)

        self.box_labels = {}
        for b in snapshot:
            rect_item = self.image.addRect(
                QRectF(b["x"], b["y"], b["w"], b["h"]), b["pen"], b["brush"]
            )
            self.box_labels[id(rect_item)] = b["label"]
            text_item = QGraphicsTextItem(b["label"], rect_item)
            text_item.setPos(b["x"], b["y"] + b["h"])
            text_item.setDefaultTextColor(QColor("magenta"))

    def push_undo(self):
        self.undo_stack.append(self._snapshot())
        self.redo_stack.clear()

    def commit_draw(self, pre_draw_snapshot):
        if pre_draw_snapshot is None:
            return
        self.undo_stack.append(pre_draw_snapshot)
        self.redo_stack.clear()
        self.saved_anns = False

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self._snapshot())
        prev_state = self.undo_stack.pop()
        self._restore(prev_state)
        self.saved_anns = False

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self._snapshot())
        next_state = self.redo_stack.pop()
        self._restore(next_state)
        self.saved_anns = False

    def dataForImg(self):   # do we have data on this image in the dataset already?
        if not self.file_path:
            return False
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
        proceed = False

        if self.saved_anns or self.dataForImg() or self.heard_warning or self.file_path is None:
            proceed = True

        elif has_tracks and self.file_path is not None:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Unsaved Annotations")
            msg.setText("Yo, you forgot to save your annotations before switching to a new file.")

            save_btn = msg.addButton("Save to File", QMessageBox.ButtonRole.AcceptRole)
            ignore_btn = msg.addButton("Ignore", QMessageBox.ButtonRole.RejectRole)

            msg.exec()

            # Handle user choice inline
            if msg.clickedButton() == save_btn:
                self.save_coco_json() # Use the app's native save method directly
                proceed = True
            elif msg.clickedButton() == ignore_btn:
                proceed = True

        else:
            reply = QMessageBox.question(
                self,
                "No Tracks Labeled",
                "You haven't labeled any tracks on this image yet. Switch pictures anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                proceed = True

        if proceed:
            file_path, _ = file_dia.getOpenFileName(
                self,
                "Select an Image",
                "Images (*.png *.jpg *.bmp);;All Files (*)"
            )

            if file_path:
                self.file_path = file_path
                self.update_image()
                self.box_labels = {}
                self.heard_warning = False
                self.saved_anns = False
                self.undo_stack = []
                self.redo_stack = []
                self._last_state = []
                self.load_existing_annotations()

    def clear_drawings(self):
        self.push_undo()
        for item in self.image.items():
            if not isinstance(item, QGraphicsPixmapItem):
                self.box_labels.pop(id(item), None)
                self.image.removeItem(item)
