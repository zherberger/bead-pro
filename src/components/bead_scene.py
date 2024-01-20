from PySide6 import QtCore, QtWidgets, QtGui
from PIL import Image

class BeadScene(QtWidgets.QGraphicsView):
   def __init__(self, image_loaded):
      QtWidgets.QGraphicsView.__init__(self)
      self.setGeometry(QtCore.QRect(100, 100, 600, 250))
      self.scene = QtWidgets.QGraphicsScene(self)
      self.scene.setSceneRect(QtCore.QRectF())
      self.setScene(self.scene)
      image_loaded.connect(self.draw_image)

   @QtCore.Slot()
   def draw_image(self, file_name):
      print("Inside draw_image")
      print(file_name)
      im = Image.open(file_name)

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
