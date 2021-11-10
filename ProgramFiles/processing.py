from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtWidgets import QDialog

from PIL import Image

import numpy as np


class ImageProcessing(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('UI_files/image_processing.ui', self)
        self.init_UI()

    def init_UI(self):
        self.pixmap = QPixmap('./Images_processing/image.jpg')
        self.initial_pixmap = QPixmap('./Images_processing/image.jpg')
        self.opacity = 1
        self.rd = 0
        self.gd = 0
        self.bd = 0
        self.lighting = 0

        self.redChannel.valueChanged[int].connect(self.change_red_channel)
        self.greenChannel.valueChanged[int].connect(self.change_green_channel)
        self.blueChannel.valueChanged[int].connect(self.change_blue_channel)
        self.alphaChannel.valueChanged[int].connect(self.change_alpha_channel)
        self.lightChannel.valueChanged[int].connect(self.change_lighting)

    def change_pixels(self):
        img1 = np.copy(Image.open("./Images_processing/image.jpg")).astype(np.int32)
        img = np.clip(img1, -520, 520)
        img[..., 0] += self.rd + self.lighting
        img[..., 1] += self.gd + self.lighting
        img[..., 2] += self.bd + self.lighting
        img = np.where(img <= 255, img, 255)
        img = np.where(img >= 0, img, 0)
        img = np.clip(img, 0, 255)
        img = Image.fromarray(img.astype(np.uint8))
        img.save("./Images_processing/image1.jpg")

        pixmap = QPixmap().fromImage(QImage("./Images_processing/image1.jpg"))
        new_pix = QPixmap(self.pixmap.size())
        new_pix.fill(QtCore.Qt.transparent)
        painter = QPainter(new_pix)
        painter.setOpacity(self.opacity)
        painter.drawPixmap(QtCore.QPoint(), pixmap)
        painter.end()
        self.pixmap = new_pix
        self.parent.drawer.set_pixmap(new_pix)


    def change_red_channel(self, value):
        self.rd = value
        self.change_pixels()

    def change_green_channel(self, value):
        self.gd = value
        self.change_pixels()

    def change_blue_channel(self, value):
        self.bd = value
        self.change_pixels()

    def change_alpha_channel(self, value):
        self.opacity = value * 0.01
        self.change_pixels()

    def change_lighting(self, value):
        self.lighting = value
        self.change_pixels()
