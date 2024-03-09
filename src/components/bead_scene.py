from PySide6 import QtCore, QtWidgets, QtGui
from PIL import Image
from src.colors.color_utils import srgb_to_lab
from src.colors.color_utils import compute_color_distance
from src.colors.bead_colors import PERLER_BEADS
from PySide6.QtCore import Signal


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
    bead_matches_obtained = Signal(object)

    def __init__(self, image_loaded):
        super().__init__()
        self.bead_matches = None
        self.image_data = None
        self.bead_legend = None
        self.layout = QtWidgets.QHBoxLayout(self)

        self.tabs = QtWidgets.QTabWidget()
        self.original_view = BeadView()
        self.bead_view = BeadView()
        self.tabs.addTab(self.original_view, "Original")
        self.tabs.addTab(self.bead_view, "Beads")
        self.layout.addWidget(self.tabs)

        self.bead_matches_obtained.connect(self.update_legend)

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
        row_num = 0

        for row in self.image_data:
            bead_data.append([])
            for pixel in row:
                bead_data[row_num].append(self.bead_matches.get(get_hex_key(pixel))["rgb"])
            row_num += 1
        self.bead_matches_obtained.emit(self.bead_matches)
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

    def update_legend(self, bead_matches):
        values = bead_matches.values()
        if self.bead_legend is not None:
            self.layout.removeWidget(self.bead_legend)
        bead_legend = QtWidgets.QWidget()
        bead_legend.layout = QtWidgets.QVBoxLayout(bead_legend)

        for bead in values:
            widget = QtWidgets.QWidget()
            widget.layout = QtWidgets.QHBoxLayout(widget)
            pixmap = QtGui.QPixmap(15, 15)
            color = QtGui.QColor.fromRgb(bead["rgb"][0], bead["rgb"][1], bead["rgb"][2])
            pixmap.fill(color)
            name_label = QtWidgets.QLabel(bead["name"])
            color_label = QtWidgets.QLabel()
            color_label.setPixmap(pixmap)
            widget.layout.addWidget(color_label)
            widget.layout.addWidget(name_label)
            bead_legend.layout.addWidget(widget)

        self.bead_legend = bead_legend
        self.layout.addWidget(self.bead_legend)


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
                self.scene.addRect(j * self.PIXEL_WIDTH, i * self.PIXEL_HEIGHT, self.PIXEL_WIDTH, self.PIXEL_HEIGHT,
                                   self.pen, QtGui.QBrush(QtGui.QColor(rgba[0], rgba[1], rgba[2])))