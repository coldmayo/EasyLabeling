# Set up

```bash
# clone this github repo
$ git clone https://github.com/coldmayo/EasyLabeling.git
# enter into the project directory
$ cd EasyLabeling
# make a python virtual envirenment
$ python -m venv .venv
# Activate the virtual envirenment
$ source .venv/bin/activate   # Linux
$ .venv\Scripts\activate.bat   # Windows (cmd)
$ .venv\Scripts\Activate.ps1   # Windows (PowerShell)
# install all required packages via requirements.txt
$ pip install -r requirements.txt
# You can run the application by running the main.py file
$ python main.py
```

# How to use

This is labeling software that will work for our Object Detection model.
You are drawing bounding boxes (bboxes) for a training set, they indicate where the object of interest (in our case, particle tracks) are.
The data being collected is going to be used for training.

To make a bbox all you have to do is click and drag to make a box. If you want to customize a class label click on/in the annotation and select from the dropdown menu. The options are as follows:
- alpha
- beta
- muon

Take a look at LabelingNotes.pdf to see how to tell the difference between these types.

If you would like to delete a box you can right click it or use the undo/redo buttons. If there are no tracks in the image, it's ok to save and move onto the next image.

Make sure you save your progress, if you don't and try to move to another image a pop-up menu will show.
When you open an image via the Find Picture button, the software automatically checks if it has been annotated previously. If existing annotations are found in your local `data.json` file, they will automatically render on the screen alongside their class labels, allowing you to resume work seamlessly.

### Keyboard Shortcuts
* Undo Last Action: `Ctrl + Z`
* Redo Action: `Ctrl + Shift + Z` or `Ctrl + Y`

If you find any bugs make an issue or submit a Pull Request on GitHub!
