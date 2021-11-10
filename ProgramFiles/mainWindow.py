import csv
import sqlite3 as sq

from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QImage, QIcon, QKeyEvent
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QColorDialog

from ProgramFiles.drawer import Drawer
from ProgramFiles.filter import Filters
from ProgramFiles.processing import ImageProcessing


class OtherPaint(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI_files/main_window.ui', self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.init_UI()

    def init_UI(self):
        with sq.connect('./Data/database.db') as con:
            cur = con.cursor()

            res = cur.execute("""
                        SELECT * FROM data
                        """).fetchall()[0]
            print(res)

        self.bColor = QColor(*map(int, res[0].split()))
        self.bSize = res[-1]

        self.init_program()

        self.changeObjectBrush()

        self.actionUndo.triggered.connect(self.drawer.mUndoStack.undo)
        self.actionRedo.triggered.connect(self.drawer.mUndoStack.redo)

        # активация функции сохранения
        self.actionSave.triggered.connect(self.save)
        self.actionClear.triggered.connect(self.clear)
        self.actioImageProcessing.triggered.connect(self.show_image_processing_window)
        self.actionFilter.triggered.connect(self.show_filter_window)

        self.brush_color.clicked.connect(self.change_color)
        self.brush_size_changer.valueChanged[int].connect(self.change_size)

        self.standartBrushObject.clicked.connect(self.changeObjectBrush)
        self.sprayBrushObject.clicked.connect(self.changeObjectSprayBrush)
        self.markerBrushObject.clicked.connect(self.changeObjectMarkerBrush)

        self.prevBrush.clicked.connect(self.show_prev_brush)
        self.nextBrush.clicked.connect(self.show_next_brush)

        self.rubberObject.clicked.connect(self.changeObjectRubber)
        self.fillObject.clicked.connect(self.changeObjectFill)
        self.textObject.clicked.connect(self.changeObjectText)
        self.pipetteObject.clicked.connect(self.changeObjectPipette)

        self.rectObject.clicked.connect(self.changeObjectRectangle)
        self.circleObject.clicked.connect(self.changeObjectCircle)
        self.triangleObject.clicked.connect(self.changeObjectTriangle)
        self.rhombObject.clicked.connect(self.changeObjectRhomb)
        self.lineObject.clicked.connect(self.changeObjectLine)

        self.text_size.valueChanged.connect(self.change_font_size)
        self.text_font.currentIndexChanged.connect(self.change_font)

        self.textBold.clicked.connect(self.selectBoldText)
        self.textItalic.clicked.connect(self.selectItalicText)
        self.textUnderlined.clicked.connect(self.selectUnderlinedText)
        self.textCrossed.clicked.connect(self.selectCrossedText)

    def show_image_processing_window(self):
        self.drawer.pixmap().save('./Images_processing/image.jpg')
        image_processing_dialog = ImageProcessing(self)
        image_processing_dialog.exec_()

    def show_filter_window(self):
        self.drawer.pixmap().save('./Images_processing/image.jpg')
        filers_dialog = Filters(self)
        filers_dialog.exec_()

    def can_undo_changed(self, enabled):
        self.actionUndo.setEnabled(enabled)

    def can_redo_changed(self, enabled):
        self.actionRedo.setEnabled(enabled)

    def check_is_brush(self, brush_type):
        if self.brush_selected:
            if brush_type == self.standartBrushObject:
                self.changeObjectBrush()
            elif brush_type == self.sprayBrushObject:
                self.changeObjectSprayBrush()
            elif brush_type == self.markerBrushObject:
                self.changeObjectMarkerBrush()

    def show_prev_brush(self):
        self.showing_page -= 1
        self.brushes.setCurrentWidget(self.brushes_pages[self.showing_page])
        self.nextBrush.setEnabled(True)
        if self.showing_page == 0:
            self.prevBrush.setDisabled(True)
        self.check_is_brush(self.brushes_to_change[self.showing_page])

    def show_next_brush(self):
        self.showing_page += 1
        self.brushes.setCurrentWidget(self.brushes_pages[self.showing_page])
        self.prevBrush.setEnabled(True)
        if self.showing_page == len(self.brushes_pages) - 1:
            self.nextBrush.setDisabled(True)
        self.check_is_brush(self.brushes_to_change[self.showing_page])

    def init_program(self):
        # вставка изображение в поле редактирования
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Все файлы (*)')

        if not fname:
            self.image = QImage(QSize(1920, 960), QImage.Format_ARGB32)
            self.image.fill(Qt.white)
        else:
            self.image = QImage(fname)

        self.drawer = Drawer(self.image.width(), self.image.height(), self)
        self.canvas_layout.addWidget(self.drawer, 1, 1, 1, 1)
        self.drawer.setImage(self.image)

        self.drawingObjects = [self.standartBrushObject, self.sprayBrushObject, self.markerBrushObject,
                               self.rectObject, self.circleObject, self.triangleObject,
                               self.rubberObject, self.lineObject, self.rhombObject, self.fillObject,
                               self.pipetteObject, self.textObject, self.textBold, self.textItalic,
                               self.textUnderlined, self.textCrossed]

        self.brush_color.setStyleSheet(f"background-color: rgb{self.bColor.getRgb()};"
                                       "border: none;")

        self.brushes_to_change = [self.standartBrushObject, self.sprayBrushObject, self.markerBrushObject]
        self.brush_selected = True

        self.disableDrawingText()

        self.brushes_pages = [self.standartBrushPage, self.sprayBrushPage, self.xBrushPage]
        self.showing_page = 0

        # Стандартная кисть
        self.standartBrushObject.setIcon(QIcon(r'./images/brush.png'))
        self.standartBrushObject.setIconSize(QSize(30, 30))

        # Спрей
        self.sprayBrushObject.setIcon(QIcon(r'./images/spray.png'))
        self.sprayBrushObject.setIconSize(QSize(30, 30))

        # Маркер
        self.markerBrushObject.setIcon(QIcon(r'./images/marker.png'))
        self.markerBrushObject.setIconSize(QSize(30, 30))

        # Ластик
        self.rubberObject.setIcon(QIcon(r'./images/rubber.png'))
        self.rubberObject.setIconSize(QSize(25, 25))

        # Заливка
        self.fillObject.setIcon(QIcon(r'./images/fill.png'))
        self.fillObject.setIconSize(QSize(25, 25))

        # Текст
        self.textObject.setIcon(QIcon(r'./images/text.png'))
        self.textObject.setIconSize(QSize(25, 25))

        # Пипетка
        self.pipetteObject.setIcon(QIcon(r'./images/pipette.png'))
        self.pipetteObject.setIconSize(QSize(25, 25))

        # Прямоугольник
        self.rectObject.setIcon(QIcon(r'./images/rect.png'))
        self.rectObject.setIconSize(QSize(25, 25))

        # Элепс
        self.circleObject.setIcon(QIcon(r'./images/circle.png'))
        self.circleObject.setIconSize(QSize(25, 25))

        # Треугольник
        self.triangleObject.setIcon(QIcon(r'./images/triangle.png'))
        self.triangleObject.setIconSize(QSize(25, 25))

        # Ромб
        self.rhombObject.setIcon(QIcon(r'./images/rhomb.png'))
        self.rhombObject.setIconSize(QSize(25, 25))

        # Линия
        self.lineObject.setIcon(QIcon(r'./images/line.png'))
        self.lineObject.setIconSize(QSize(25, 25))

        # Жирный шрифт
        self.textBold.setIcon(QIcon(r'./images/bold-text.png'))
        self.textBold.setIconSize(QSize(20, 20))
        self.bold_selected = False

        # Италик шрифт
        self.textItalic.setIcon(QIcon(r'./images/italic.png'))
        self.textItalic.setIconSize(QSize(20, 20))
        self.italic_selected = False

        # Подчёркнутый текст
        self.textUnderlined.setIcon(QIcon(r'./images/underline-text.png'))
        self.textUnderlined.setIconSize(QSize(20, 20))
        self.underlined_selected = False

        # Зачёркнутый текст
        self.textCrossed.setIcon(QIcon(r'./images/text-crossed.png'))
        self.textCrossed.setIconSize(QSize(20, 20))
        self.crossed_selected = False

        self.setStylesButtons(*self.drawingObjects)

        self.change_size(self.bSize)
        self.brush_size_changer.setValue(self.bSize)
        self.drawer.setColor(self.bColor)

    def update_database(self):
        with open('./Data/data.csv', 'w') as csvfile:
            color = self.bColor.getRgb()
            size = self.bSize
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([f'{color[0]} {color[1]} {color[2]}', size])

        with sq.connect('./Data/database.db') as con:
            cur = con.cursor()

            color = self.bColor.getRgb()
            cur.execute("""
                        UPDATE data
                        SET color = ?
                        """, (item_color := f'{color[0]} {color[1]} {color[2]}',))
            cur.execute("""
                        UPDATE data
                        SET size = ?
                        """, (item_color := self.bSize,))
            con.commit()

    def change_color(self):
        dialog = QColorDialog()
        self.bColor = dialog.getColor()
        self.drawer.setColor(self.bColor)
        self.brush_color.setStyleSheet(f"background-color: rgb{self.bColor.getRgb()};"
                                       "border: none;")
        self.update_database()

    def change_size(self, size):
        self.brush_size.setText(str(size))
        self.bSize = size
        self.drawer.setSize(self.bSize)
        self.update_database()

    def change_font(self):
        self.drawer.text_font = self.text_font.currentText()
        self.drawer.setTextFont()

    def change_font_size(self):
        self.drawer.text_size = self.text_size.value()
        self.drawer.setTextFont()

    def setStylesButtons(self, *buttons):
        for button in buttons:
            button.setStyleSheet("""
                                        QPushButton {
                                            border: 1px solid rgb(240, 240, 240);
                                            background: rgb(240, 240, 240);
                                        }
                                        QPushButton:hover {
                                            background: rgb(239, 246, 254);
                                            border: 1px solid rgb(170, 211, 254);
                                            border-radius: 3px;
                                        }
                                        """)

    def setStylesActiveButtons(self, *buttons):
        for button in buttons:
            button.setStyleSheet("""
                                QPushButton {
                                    border: 1px solid rgb(101, 166, 231);
                                    background-color: rgb(207, 230, 254);
                                    border-radius: 3px;
                                }
                            """)

    def disableDrawingText(self):
        self.text_font.setDisabled(True)
        self.text_size.setDisabled(True)
        self.textBold.setDisabled(True)
        self.textItalic.setDisabled(True)
        self.textUnderlined.setDisabled(True)
        self.textCrossed.setDisabled(True)

    def enableDrawingText(self):
        self.text_font.setEnabled(True)
        self.text_size.setEnabled(True)
        self.textBold.setEnabled(True)
        self.textItalic.setEnabled(True)
        self.textUnderlined.setEnabled(True)
        self.textCrossed.setEnabled(True)

    def changeObjectBrush(self):
        self.drawer.setObject('Кисть')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(*self.brushes_to_change)
        self.disableDrawingText()
        self.brush_selected = True

    def changeObjectSprayBrush(self):
        self.drawer.setObject('Спрей')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(*self.brushes_to_change)
        self.disableDrawingText()
        self.brush_selected = True

    def changeObjectMarkerBrush(self):
        self.drawer.setObject('Маркер')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(*self.brushes_to_change)
        self.disableDrawingText()
        self.brush_selected = True

    def changeObjectRubber(self):
        self.drawer.setObject('Ластик')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.rubberObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectFill(self):
        self.drawer.setObject('Заливка')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.fillObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectText(self):
        self.drawer.setObject('Текст')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.textObject)
        self.enableDrawingText()
        self.brush_selected = False

    def changeObjectPipette(self):
        self.drawer.setObject('Пипетка')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.pipetteObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectRectangle(self):
        self.drawer.setObject('Прямоугольник')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.rectObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectCircle(self):
        self.drawer.setObject('Круг')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.circleObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectTriangle(self):
        self.drawer.setObject('Треугольник')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.triangleObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectRhomb(self):
        self.drawer.setObject('Ромб')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.rhombObject)
        self.disableDrawingText()
        self.brush_selected = False

    def changeObjectLine(self):
        self.drawer.setObject('Линия')
        self.setStylesButtons(*self.drawingObjects)
        self.setStylesActiveButtons(self.lineObject)
        self.disableDrawingText()
        self.brush_selected = False

    def selectBoldText(self):
        if self.bold_selected:
            self.setStylesButtons(self.textBold)
            self.drawer.is_bold = False
            self.bold_selected = False
        else:
            self.setStylesActiveButtons(self.textBold)
            self.drawer.is_bold = True
            self.bold_selected = True
        self.drawer.setTextFont()

    def selectItalicText(self):
        if self.italic_selected:
            self.setStylesButtons(self.textItalic)
            self.drawer.is_italic = False
            self.italic_selected = False
        else:
            self.setStylesActiveButtons(self.textItalic)
            self.drawer.is_italic = True
            self.italic_selected = True
        self.drawer.setTextFont()

    def selectUnderlinedText(self):
        if self.underlined_selected:
            self.setStylesButtons(self.textUnderlined)
            self.drawer.is_underlined = False
            self.underlined_selected = False
        else:
            self.setStylesActiveButtons(self.textUnderlined)
            self.drawer.is_underlined = True
            self.underlined_selected = True
        self.drawer.setTextFont()

    def selectCrossedText(self):
        if self.crossed_selected:
            self.setStylesButtons(self.textCrossed)
            self.drawer.is_crossed = False
            self.crossed_selected = False
        else:
            self.setStylesActiveButtons(self.textCrossed)
            self.drawer.is_crossed = True
            self.crossed_selected = True
        self.drawer.setTextFont()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)

        if self.drawer.drawing_text:
            if event.key() == 16777220:
                self.drawer.text += '\n'
                self.drawer.rows += 1
            if event.text().lower() in self.drawer.can_type:
                self.drawer.text += event.text()
            elif event.key() == 16777219 and self.drawer.text != '|':
                self.drawer.text = self.drawer.text[:-1]

    def save(self):
        # сохранение результата
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        self.drawer.pixmap().save(filePath)

    def clear(self):
        self.drawer.clearDrawer()
