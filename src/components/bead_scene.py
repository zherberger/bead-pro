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
        self.layout = QtWidgets.QHBoxLayout(self)

        self.tabs = QtWidgets.QTabWidget()
        self.original_view = BeadView()
        self.bead_view = BeadView()
        self.tabs.addTab(self.original_view, "Original")
        self.tabs.addTab(self.bead_view, "Beads")
        self.layout.addWidget(self.tabs)

        self.bead_legend = BeadLegend([])
        self.layout.addWidget(self.bead_legend)

        image_loaded.connect(self.load_image)

    @QtCore.Slot()
    def load_image(self, file_name):
        im = Image.open(file_name)
        pixels = list(im.getdata())
        width, height = im.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        self.image_data = pixels
        self.bead_matches = self.generate_bead_matches()
        self.original_view.draw_image(self.image_data)
        bead_data = []
        rowNum = 0

        for row in self.image_data:
            bead_data.append([])
            for pixel in row:
                bead_data[rowNum].append(self.bead_matches.get(get_hex_key(pixel))["rgb"])
            rowNum += 1

        self.bead_view.draw_image(bead_data)

    def generate_bead_matches(self):
        bead_matches = {}

        for row in self.image_data:
            for pixel in row:
                rgb = pixel[0:3]
                key = get_hex_key(rgb)

                if bead_matches.get(key) is None:
                    bead_matches[key] = get_closest_bead(rgb)

        return bead_matches

class BeadLegend(QtWidgets.QWidget):
    def __init__(self, bead_colors):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)
        for bead in bead_colors:
            label = QtWidgets.QLabel(bead["name"])
            self.layout.addWidget(label)

        label = QtWidgets.QLabel("Hello World")
        self.layout.addWidget(label)

class BeadTabs(QtWidgets.QTabBar):
    def __init__(self):
        super().__init__()
        self.addTab("Original")
        self.addTab("Beads")

class BeadView(QtWidgets.QGraphicsView):
    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)
        self.setGeometry(QtCore.QRect(100, 100, 600, 250))
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(QtCore.QRectF())
        self.setScene(self.scene)
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.PenStyle.NoPen)
        self.PIXEL_WIDTH = 30
        self.PIXEL_HEIGHT = 30

    def draw_image(self, image_data):
        for i in range(len(image_data)):
            for j in range(len(image_data[0])):
                rgba = image_data[i][j]
                self.scene.addRect(j*self.PIXEL_WIDTH, i*self.PIXEL_HEIGHT, self.PIXEL_WIDTH, self.PIXEL_HEIGHT, self.pen, QtGui.QBrush(QtGui.QColor(rgba[0], rgba[1], rgba[2])))