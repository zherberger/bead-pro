import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Signal

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

if __name__ == '__main__':
   window()