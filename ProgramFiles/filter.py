from PyQt5 import uic
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QDialog

from PIL import Image, ImageFilter

import numpy as np


class Filters(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('UI_files/filters.ui', self)
        self.init_UI()

    def init_UI(self):
        self.blackAndWhite.clicked.connect(self.black_and_white_filter)
        self.negative.clicked.connect(self.negative_filter)
        self.blue.clicked.connect(self.blue_filter)
        self.blur.clicked.connect(self.blur_filter)
        self.emboss.clicked.connect(self.emboss_filter)

    def black_and_white_filter(self):
        img = Image.open("./Images_processing/image.jpg")
        img = img.convert('L')
        img.save("./Images_processing/image1.jpg")
        self.parent.drawer.setImage(QImage("./Images_processing/image1.jpg"))

    def negative_filter(self):
        img = np.array(Image.open("./Images_processing/image.jpg"))
        img = 255 - img
        img = Image.fromarray(img)
        img.save("./Images_processing/image1.jpg")
        self.parent.drawer.setImage(QImage("./Images_processing/image1.jpg"))

    def blue_filter(self):
        img = np.copy(Image.open("./Images_processing/image.jpg"))
        img[..., 2] = 255
        img = Image.fromarray(img)
        img.save("./Images_processing/image1.jpg")
        self.parent.drawer.setImage(QImage("./Images_processing/image1.jpg"))

    def blur_filter(self):
        img = Image.open("./Images_processing/image.jpg")
        img2 = img.filter(ImageFilter.BLUR)
        img2.save("./Images_processing/image1.jpg")
        self.parent.drawer.setImage(QImage("./Images_processing/image1.jpg"))

    def emboss_filter(self):
        img = Image.open("./Images_processing/image.jpg")
        img2 = img.filter(ImageFilter.EMBOSS)
        img2.save("./Images_processing/image1.jpg")
        self.parent.drawer.setImage(QImage("./Images_processing/image1.jpg"))
