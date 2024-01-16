import sys
import random
import os
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Signal
from PIL import Image

class MyWidget(QtWidgets.QWidget):
   def __init__(self, parent):
      super().__init__()

      self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир", "Hewwo Wowwd", "Hello World"]

      self.button = QtWidgets.QPushButton("Click me!")
      self.button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
      self.label = QtWidgets.QLabel("Hello World",
                                   alignment=QtCore.Qt.AlignCenter)
      
      self.layout = QtWidgets.QVBoxLayout(self)
      self.layout.addWidget(self.label)
      self.layout.addWidget(self.button)

      self.button.clicked.connect(self.magic)
      parent.image_loaded.connect(self.show_image)

      scene = QtWidgets.QGraphicsScene()
      scene.setSceneRect(0, 0, 200, 200)
      text = scene.addText("Hello!")

      view = MyView()
      self.layout.addWidget(view)



   @QtCore.Slot()
   def magic(self):
      self.label.setText(random.choice(self.hello))

   @QtCore.Slot()
   def show_image(self, file_name):
      label = QtWidgets.QLabel(self)
      pixmap = QtGui.QPixmap(file_name)
      label.setPixmap(pixmap)
      self.layout.addWidget(label)

class MainWindow(QtWidgets.QMainWindow):
   image_loaded = Signal(str)

   def __init__(self):
      super().__init__()

      self.setWindowTitle("BeadPro")
      main_widget = MyWidget(self)
      self.setCentralWidget(main_widget)

      open_icon = QtGui.QIcon.fromTheme("document-open", QtGui.QIcon(":/resources/folder_open.png"))
      open_action = QtGui.QAction(open_icon, "&Open", self)
      open_action.triggered.connect(self.open_image)

      menu = self.menuBar()
      file_menu = menu.addMenu("&File")
      file_menu.addAction(open_action)

   @QtCore.Slot()
   def open_image(self):
      file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "C:/", "Image Files (*.png)")
      print(file_name)
      self.image_loaded.emit(file_name[0])

def window():
   app = QtWidgets.QApplication([])

   window = MainWindow()
   window.resize(800, 600)
   window.show()

   sys.exit(app.exec())

class MyView(QtWidgets.QGraphicsView):
   def __init__(self):
      QtWidgets.QGraphicsView.__init__(self)
      self.setGeometry(QtCore.QRect(100, 100, 600, 250))
      

      self.scene = QtWidgets.QGraphicsScene(self)
      self.scene.setSceneRect(QtCore.QRectF())
      self.scene.addText("Hello!")

      self.setScene(self.scene)

      cwd = os.getcwd()
      print(cwd)

      im = Image.open('Projects/bead-pro/resources/testimage.png')

      pixels = list(im.getdata())
      width, height = im.size
      pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]


      WIDTH = 30
      HEIGHT = 30
      pen = QtGui.QPen()
      pen.setStyle(QtCore.Qt.PenStyle.NoPen)
      for i in range(len(pixels)):
         for j in range(len(pixels[0])):
            rgba = pixels[i][j]
            self.scene.addRect(j*WIDTH, i*HEIGHT, WIDTH, HEIGHT, pen, QtGui.QBrush(QtGui.QColor(rgba[0], rgba[1], rgba[2])))

            


if __name__ == '__main__':
   window()