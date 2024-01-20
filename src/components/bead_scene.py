from PySide6 import QtCore, QtWidgets, QtGui
from PIL import Image
from color_utils import srgb_to_lab
from color_utils import compute_color_distance
from bead_colors import PERLER_BEADS

def get_hex_key(rgb):
    return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])

def get_closest_bead(rgb):
    min_distance = 100.0

    for bead in PERLER_BEADS:
        distance = compute_color_distance(srgb_to_lab(bead["rgb"]), srgb_to_lab(rgb))

        if distance < min_distance:
            min_distance = distance
            closest_match = bead

    return closest_match

class BeadWorkflow(QtWidgets.QWidget):
    def __init__(self, image_loaded):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)
        tabs = BeadTabs()
        self.layout.addWidget(tabs)
        scene = BeadScene(image_loaded, tabs.currentChanged)
        self.layout.addWidget(scene)

class BeadTabs(QtWidgets.QTabBar):
    def __init__(self):
        super().__init__()
        self.addTab("Original")
        self.addTab("Beads")

class BeadScene(QtWidgets.QGraphicsView):
    def __init__(self, image_loaded, tab_changed):
        QtWidgets.QGraphicsView.__init__(self)
        self.setGeometry(QtCore.QRect(100, 100, 600, 250))
        self.original_scene = QtWidgets.QGraphicsScene(self)
        self.original_scene.setSceneRect(QtCore.QRectF())
        self.bead_scene = QtWidgets.QGraphicsScene(self)
        self.bead_scene.setSceneRect(QtCore.QRectF())
        self.setScene(self.bead_scene)
        image_loaded.connect(self.load_image)
        tab_changed.connect(self.change_tab)

    @QtCore.Slot()
    def load_image(self, file_name):
        im = Image.open(file_name)

        pixels = list(im.getdata())
        width, height = im.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        self.image_data = pixels
        self.bead_matches = self.generate_bead_matches()
        self.draw_image("original")
        self.draw_image("bead")

    def draw_image(self, mode):
        WIDTH = 30
        HEIGHT = 30
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.PenStyle.NoPen)

        for i in range(len(self.image_data)):
            for j in range(len(self.image_data[0])):
                rgba = self.image_data[i][j]

                if mode == "original":
                    self.original_scene.addRect(j*WIDTH, i*HEIGHT, WIDTH, HEIGHT, pen, QtGui.QBrush(QtGui.QColor(rgba[0], rgba[1], rgba[2])))
                elif mode == "bead":
                    bead_match_color = self.bead_matches[get_hex_key(rgba)]["rgb"]
                    self.bead_scene.addRect(j*WIDTH, i*HEIGHT, WIDTH, HEIGHT, pen, QtGui.QBrush(QtGui.QColor(bead_match_color[0], bead_match_color[1], bead_match_color[2])))

    def generate_bead_matches(self):
        bead_matches = {}

        for row in self.image_data:
            for pixel in row:
                rgb = pixel[0:3]
                key = get_hex_key(rgb)

                if bead_matches.get(key) is None:
                    bead_matches[key] = get_closest_bead(rgb)

        return bead_matches
    
    def change_tab(self, index):
        self.setScene(self.original_scene if index == 0 else self.bead_scene)