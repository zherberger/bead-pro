from PySide6 import QtCore, QtWidgets, QtGui
from PIL import Image
from color_utils import srgb_to_lab
from color_utils import compute_color_distance
from bead_colors import PERLER_BEADS

def get_hex_key(rgb):
   print(rgb)
   return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])

def get_closest_bead(rgb):
   min_distance = 100.0

   for bead in PERLER_BEADS:
      distance = compute_color_distance(srgb_to_lab(bead["rgb"]), srgb_to_lab(rgb))

      if distance < min_distance:
         min_distance = distance
         closest_match = bead

   return closest_match

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
        im = Image.open(file_name)

        pixels = list(im.getdata())
        width, height = im.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        self.image_data = pixels
        self.bead_matches = self.generate_bead_matches()

        WIDTH = 30
        HEIGHT = 30
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.PenStyle.NoPen)
        for i in range(len(pixels)):
            for j in range(len(pixels[0])):
                rgba = pixels[i][j]
                self.scene.addRect(j*WIDTH, i*HEIGHT, WIDTH, HEIGHT, pen, QtGui.QBrush(QtGui.QColor(rgba[0], rgba[1], rgba[2])))

    def generate_bead_matches(self):
        bead_matches = {}

        for row in self.image_data:
            for pixel in row:
                rgb = pixel[0:3]
                key = get_hex_key(rgb)

                if bead_matches.get(key) is None:
                    bead_matches[key] = get_closest_bead(rgb)

        print(bead_matches)
        return bead_matches