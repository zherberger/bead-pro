import sys
import random
import os
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Signal
from components.bead_scene import BeadWorkflow

class MainWindow(QtWidgets.QMainWindow):
   image_loaded = Signal(str)

   def __init__(self):
      super().__init__()

      self.setWindowTitle("BeadPro")
      main_widget = BeadWorkflow(self.image_loaded)
      self.setCentralWidget(main_widget)

      open_icon = QtGui.QIcon.fromTheme("document-open", QtGui.QIcon(":/resources/folder_open.png"))
      open_action = QtGui.QAction(open_icon, "&Open", self)
      open_action.triggered.connect(self.open_image)

      menu = self.menuBar()
      file_menu = menu.addMenu("&File")
      file_menu.addAction(open_action)

   @QtCore.Slot()
   def open_image(self):
      file_tuple = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "C:/", "Image Files (*.png)")
      
      # On image load, emit the image_loaded signal with the absolute path of the file, which can be picked up by other components (namely, the BeadScene)
      self.image_loaded.emit(file_tuple[0])

def window():
   app = QtWidgets.QApplication([])

   window = MainWindow()
   window.resize(800, 600)
   window.show()

   sys.exit(app.exec())

if __name__ == '__main__':
   window()