import random
import sys

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt, QTimer, QRect, QLine, QRectF, QSizeF
from PyQt5.QtGui import QColor, QPen, QPixmap, QImage, QFont
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QLabel, QUndoCommand, QUndoStack, QFrame


# отлов ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class UndoCommand(QUndoCommand):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.mPrevImage = parent.main_image.copy()
        self.mCurrImage = parent.main_image.copy()

    def undo(self):
        self.mCurrImage = self.parent.main_image.copy()
        self.parent.main_image = self.mPrevImage
        self.parent.update()

    def redo(self):
        self.parent.main_image = self.mCurrImage
        self.parent.update()


class Drawer(QLabel):
    newPoint = pyqtSignal(QPoint)

    def __init__(self, w, h, mainWindow, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 1980, 1280)
        self.path = QPainterPath()

        # надо
        self._flag = False
        self.resolution_index = 0
        self.screen_resolution_data = [(1920 + i, 960 + i // 2) for i in range(0, 12100, 200)]
        self.resolution_main_id = 0

        # родитель холста
        self.mainWindow = mainWindow

        # содержание холста
        self.pix_map = QPixmap()
        self.main_image = QImage(QSize(*self.screen_resolution_data[self.resolution_main_id]),
                                 QImage.Format_ARGB32)
        self.image = self.main_image.scaled(*self.screen_resolution_data[self.resolution_index])

        # Undo / Redo команды
        self.mUndoStack = QUndoStack(self)
        self.mUndoStack.setUndoLimit(20)

        self.mUndoStack.canUndoChanged.connect(self.mainWindow.can_undo_changed)
        self.mUndoStack.canRedoChanged.connect(self.mainWindow.can_redo_changed)

        self.mainWindow.can_undo_changed(self.mUndoStack.canUndo())
        self.mainWindow.can_redo_changed(self.mUndoStack.canRedo())

        # размер холста
        self.w = w
        self.h = h

        # настройка кисти
        self.color = QColor(0, 0, 0)
        self.marker_color = QColor(0, 0, 0, 7)
        self.rubber_color = QColor(255, 255, 255)
        self.size = 3
        self.pen = QPen(self.color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.spray_pen = QPen(self.color, 1)
        self.marker_pen = QPen(self.marker_color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.rubber = QPen(self.rubber_color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.fill_pen = QPen(self.color, 1)

        # переменные для прорисовки
        self.paint = False
        self.last_point = None

        # объект для прорисовки
        self.object = 'Кисть'

        # переменные для прорисовки квадрата и круга
        self.first_pos = None
        self.destination = None

        # теушая позиция курсора
        self.cur_pos = None

        # переменные для прорисовки ромба
        self.rhombA = None
        self.rhombB = None
        self.rhombC = None
        self.rhombD = None

        # переменные для прорисовки треугольника
        self.A = None
        self.B = None
        self.C = None

        # переменные для заливки
        self.fill_position = None
        self.fill_pixels = []

        # переменные для прорисовки текста
        self.drawing_text = False
        self.coordinates = None
        self.text_size = 8
        self.text_font = 'Arial'
        self.font = QFont()
        self.is_bold = False
        self.is_italic = False
        self.is_underlined = False
        self.is_crossed = False
        self.can_type = '1234567890-=ёйцукенгшщзхъ\фывапролджэячсмитьбю.`qwertyuiop[]()asdfghjkl;\'zxcvbnm,./!@#$%^&*"№?_ '
        self.text_pen = QPen(self.color)
        self.rows = 0
        self.textRect = None
        self.text = ''

        # переменные для прорисовки спрея
        self.SPRAY_PARTICLES = 100

        # маркер для начала отрисовки
        self.clicked = False

        # координаты курсора всегда отслеживаются
        self.setMouseTracking(True)

    def setImage(self, image):
        self.pix_map = QPixmap.fromImage(image)
        self.main_image = image

    def set_pixmap(self, pixmap):
        self.pix_map = pixmap
        self.main_image = pixmap.toImage()

    def setPen(self):
        self.pen = QPen(self.color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.spray_pen = QPen(self.color, 1)
        self.marker_pen = QPen(self.marker_color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.rubber = QPen(self.rubber_color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.text_pen = QPen(self.color)
        self.fill_pen = QPen(self.color, 1)

    def setTextFont(self):
        self.font = QFont(self.text_font, self.text_size)
        self.font.setBold(self.is_bold)
        self.font.setItalic(self.is_italic)
        self.font.setUnderline(self.is_underlined)
        self.font.setStrikeOut(self.is_crossed)

    def setColor(self, color):
        mcolor = QColor(*color.getRgb())
        self.color = color
        mcolor.setAlpha(7)
        self.marker_color = mcolor
        self.setPen()

    def setSize(self, size):
        self.size = size
        self.setPen()

    def setObject(self, object):
        self.object = object

    def clearDrawer(self):
        self.main_image = QImage(QSize(self.w, self.h), QImage.Format_ARGB32)
        self.main_image.fill(Qt.white)
        self.pix_map = QPixmap.fromImage(self.main_image)
        self.update()

    def changeRhombSides(self):
        self.rhombA = QPoint(self.first_pos.x(), self.first_pos.y() + (self.destination.y() - self.first_pos.y()) // 2)
        self.rhombB = QPoint(self.first_pos.x() + (self.destination.x() - self.first_pos.x()) // 2, self.first_pos.y())
        self.rhombC = QPoint(self.destination.x(),
                             self.first_pos.y() + (self.destination.y() - self.first_pos.y()) // 2)
        self.rhombD = QPoint(self.first_pos.x() + (self.destination.x() - self.first_pos.x()) // 2,
                             self.destination.y())

    def pixmap(self):
        return self.pix_map

    def get_pixel(self, x, y, img):
        i = (x + (y * self.w)) * 4
        return img[i:i + 3]

    def get_cardinal_points(self, have_seen, center_pos):
        points = []
        cx, cy = center_pos
        for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            xx, yy = cx + x, cy + y
            if 0 <= xx < self.w and 0 <= yy < self.h and (xx, yy) not in have_seen:
                points.append((xx, yy))
                have_seen.add((xx, yy))
        return points

    def addPixelsToFill(self, x, y):
        img = self.main_image.bits().asstring(self.w * self.h * 4)

        target_color = self.get_pixel(x, y, img)
        have_seen = set()
        queue = [(x, y)]

        while queue:
            x, y = queue.pop()
            if self.get_pixel(x, y, img) == target_color:
                self.fill_pixels.append((x, y))
                queue.extend(self.get_cardinal_points(have_seen, (x, y)))

    def paintEvent(self, event):
        try:
            canvasPainter = QPainter(self)
            canvasPainter.drawImage(self.rect(), self.main_image)
            canvasPainter.setRenderHint(QPainter.HighQualityAntialiasing)

            if self.object == 'Заливка' and self.fill_position is not None:
                self.addPixelsToFill(self.fill_position.x(), self.fill_position.y())

            elif self.object == 'Текст' and self.drawing_text:
                canvasPainter.setPen(self.text_pen)
                canvasPainter.setFont(self.font)
                self.textRect = QRectF(self.coordinates, QSizeF(len(self.text) * self.text_size,
                                                                self.text_size + self.text_size * self.rows * 1.65 + 10))
                canvasPainter.drawText(self.textRect, Qt.AlignLeft, self.text[1:] + '|')

            elif self.clicked:
                if self.object == 'Ластик':
                    canvasPainter.setPen(self.rubber)
                elif self.object == 'Маркер':
                    canvasPainter.setPen(self.marker_pen)
                else:
                    canvasPainter.setPen(self.pen)

                if self.object == 'Прямоугольник' and self.first_pos is not None and self.destination is not None \
                    and self.first_pos != self.destination:
                    rect = QRect(self.first_pos, self.destination)
                    canvasPainter.drawRect(rect.normalized())

                elif self.object == 'Круг' and self.first_pos is not None and self.destination is not None \
                    and self.first_pos != self.destination:
                    rect = QRect(self.first_pos, self.destination)
                    canvasPainter.drawEllipse(rect.normalized())

                elif self.object == 'Линия' and self.first_pos is not None and self.destination is not None \
                    and self.first_pos != self.destination:
                    line = QLine(self.first_pos, self.destination)
                    canvasPainter.drawLine(line)

                elif self.object == 'Ромб' and self.first_pos is not None and self.destination is not None \
                    and self.first_pos != self.destination:
                    canvasPainter.drawPolygon(self.rhombA, self.rhombB, self.rhombC, self.rhombD)

                elif self.object == 'Треугольник' and self.A is not None and self.B is not None and self.C is not None:
                    canvasPainter.drawPolygon(QPoint(*self.A), QPoint(*self.B), QPoint(*self.C))

                elif (self.object == 'Ластик' or self.object == 'Кисть' or self.object == 'Маркер') \
                    and self.cur_pos is not None \
                    and self.cur_pos.x() != 0 and self.cur_pos.y() != 0:
                    canvasPainter.setPen(QPen(Qt.black, 1))
                    canvasPainter.drawEllipse(
                        QPoint(self.cur_pos.x(), self.cur_pos.y()),
                        self.size // 2, self.size // 2)

            else:
                canvasPainter.setPen(QPen(Qt.black, 1))
                if self.cur_pos is not None and (self.object == 'Кисть' or self.object == 'Ластик'
                                                 or self.object == 'Маркер') \
                    and self.cur_pos.x() != 0 and self.cur_pos.y() != 0:
                    canvasPainter.drawEllipse(
                        QPoint(self.cur_pos.x(), self.cur_pos.y()),
                        self.size // 2,
                        self.size // 2)

            self.update()
        except Exception as e:
            print(e)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked = True
            self.paint = True
            painter = QPainter(self.main_image)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            if self.object == 'Ластик':
                painter.setPen(self.rubber)
            elif self.object == 'Маркер':
                painter.setPen(self.marker_pen)
            else:
                painter.setPen(self.pen)

            if self.object == 'Пипетка':
                x, y = event.x(), event.y()
                pixel = self.main_image.pixel(x, y)
                color = QColor(pixel)
                self.mainWindow.brush_color.setStyleSheet(f"background-color: rgb{color.getRgb()};"
                                                          "border: none;")
                self.setColor(color)

            elif self.object == 'Кисть' or self.object == 'Ластик' or self.object == 'Маркер':
                self.lastPoint = event.pos()
                painter.drawPoint(self.lastPoint)

            elif self.object == 'Спрей':
                painter.setPen(self.spray_pen)

                for _ in range(self.size ** 2 // 8):
                    x0 = random.gauss(0, self.size)
                    y0 = random.gauss(0, self.size)
                    painter.drawPoint(event.x() + x0 // 2, event.y() + y0 // 2)

            elif self.object == 'Прямоугольник' or self.object == 'Круг' or self.object == 'Линия':
                self.first_pos = event.pos()
                self.destination = event.pos()

            elif self.object == 'Ромб':
                self.first_pos = event.pos()
                self.destination = event.pos()
                self.changeRhombSides()

            elif self.object == 'Треугольник':
                self.A = [event.x(), event.y()]
                self.B = [event.x(), event.y()]
                self.C = [event.x(), event.y()]

            elif self.object == 'Текст':
                if self.drawing_text:
                    painter.setPen(self.text_pen)
                    painter.setFont(self.font)
                    self.drawing_text = False
                    painter.drawText(self.textRect, self.text[1:])
                    self.text = ''
                else:
                    self.drawing_text = True
                    self.coordinates = event.pos()
                    self.text = '|'

            elif self.object == 'Заливка':
                self.fill_position = event.pos()

            self.cur_pos = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.paint:
            painter = QPainter(self.main_image)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            if self.object == 'Ластик':
                painter.setPen(self.rubber)
            elif self.object == 'Маркер':
                painter.setPen(self.marker_pen)
            else:
                painter.setPen(self.pen)

            if self.object == 'Кисть' or self.object == 'Ластик' or self.object == 'Маркер':
                painter.drawLine(self.lastPoint, event.pos())
                self.lastPoint = event.pos()

            elif self.object == 'Спрей':
                painter.setPen(self.spray_pen)

                for _ in range(self.size ** 2 // 8):
                    x0 = random.gauss(0, self.size)
                    y0 = random.gauss(0, self.size)
                    painter.drawPoint(event.x() + x0 // 2, event.y() + y0 // 2)

            elif self.object == 'Прямоугольник' or self.object == 'Круг' or self.object == 'Линия':
                self.destination = event.pos()

            elif self.object == 'Ромб':
                self.destination = event.pos()
                self.changeRhombSides()

            elif self.object == 'Треугольник':
                self.A[1] = event.y()
                self.B[0] = event.x() - (event.x() - self.A[0]) // 2
                self.C = [event.x(), event.y()]

            self.update()
        self.cur_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked = False
            self.make_undo_command()
            painter = QPainter(self.main_image)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            painter.setPen(self.pen)

            if self.object == 'Прямоугольник' and self.first_pos != self.destination:
                rect = QRect(self.first_pos, self.destination)
                painter.drawRect(rect.normalized())

            elif self.object == 'Круг' and self.first_pos != self.destination:
                ellipse = QRect(self.first_pos, self.destination)
                painter.drawEllipse(ellipse.normalized())

            elif self.object == 'Треугольник':
                painter.drawPolygon(QPoint(*self.A), QPoint(*self.B), QPoint(*self.C))

            elif self.object == 'Линия' and self.first_pos != self.destination:
                line = QLine(self.first_pos, self.destination)
                painter.drawLine(line)

            elif self.object == 'Ромб':
                painter.drawPolygon(self.rhombA, self.rhombB, self.rhombC, self.rhombD)

            elif self.object == 'Заливка' and self.fill_position is not None:
                painter.setPen(self.fill_pen)
                for pos in self.fill_pixels:
                    x, y = pos
                    painter.drawPoint(QPoint(x, y))
                self.fill_pixels = []

            self.A = None
            self.B = None
            self.C = None
            self.first_pos = None
            self.destination = None
            self.paint = False
            self.rhombA = None
            self.rhombB = None
            self.rhombC = None
            self.rhombD = None
            self.fill_position = None
            self.pix_map = QPixmap.fromImage(self.main_image)
            self.update()

    # Undo команда
    def make_undo_command(self):
        self.mUndoStack.push(UndoCommand(self))

    def scaleImage(self):
        if self.pix_map.isNull():
            return
        scaled = self.pix_map.scaled(self.w, self.h, Qt.KeepAspectRatioByExpanding)
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        if not self._flag:
            self._flag = True
            self.scaleImage()
            QTimer.singleShot(100, lambda: setattr(self, "_flag", False))
        super().resizeEvent(event)

    def sizeHint(self):
        return QSize(self.w, self.h)

    def __str__(self):
        return f'Drawer(color={self.color.getRgb()}, size={self.size}, object={self.object})'
