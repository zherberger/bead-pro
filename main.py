import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):
   def __init__(self):
      super().__init__()

      self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

      self.button = QtWidgets.QPushButton("Click me!")
      self.button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
      self.label = QtWidgets.QLabel("Hello World",
                                   alignment=QtCore.Qt.AlignCenter)
      
      self.layout = QtWidgets.QVBoxLayout(self)
      self.layout.addWidget(self.label)
      self.layout.addWidget(self.button)

      self.button.clicked.connect(self.magic)

   @QtCore.Slot()
   def magic(self):
      self.label.setText(random.choice(self.hello))

class MainWindow(QtWidgets.QMainWindow):
   def __init__(self):
      super().__init__()

      self.setWindowTitle("BeadPro")
      self.setCentralWidget(MyWidget())

      open_icon = QtGui.QIcon.fromTheme("document-open", QtGui.QIcon(":/resources/folder_open.png"))
      open_action = QtGui.QAction(open_icon, "&Open", self)
      open_action.triggered.connect(self.open_file)

      menu = self.menuBar()
      file_menu = menu.addMenu("&File")
      file_menu.addAction(open_action)

   @QtCore.Slot()
   def open_file(self):
      fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "C:/", "Image Files (*.png)")
      print(fileName)

def window():
   app = QtWidgets.QApplication([])

   window = MainWindow()
   window.resize(800, 600)
   window.show()

   sys.exit(app.exec())

if __name__ == '__main__':
   window()