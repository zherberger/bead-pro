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
    closest_match = None

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

        self.original_view = BeadView()
        self.bead_view = BeadView()

        bead_widget = QtWidgets.QWidget()
        bead_widget_layout = QtWidgets.QHBoxLayout(bead_widget)
        bead_widget_layout.addWidget(self.bead_view)
        bead_widget_layout.addWidget(BeadLegend(self.bead_matches_obtained))
        bead_widget.setLayout(bead_widget_layout)
        image_loaded.connect(self.load_image)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.original_view, "Original")
        self.tabs.addTab(bead_widget, "Beads")
        self.layout.addWidget(self.tabs)

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

        self.bead_view.draw_image(bead_data)
        self.bead_matches_obtained.emit(self.bead_matches)
        self.tabs.setCurrentIndex(1)

    def generate_bead_matches(self):
        bead_matches = {}

        for row in self.image_data:
            for pixel in row:
                rgb = pixel[0:3]
                key = get_hex_key(rgb)

                if bead_matches.get(key) is None:
                    bead_matches[key] = get_closest_bead(rgb)
                    bead_matches[key]["count"] = 1
                else:
                    bead_matches[key]["count"] += 1

        return bead_matches


class BeadLegend(QtWidgets.QWidget):
    def __init__(self, bead_matches_obtained):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.bead_matches_obtained = bead_matches_obtained
        self.bead_matches_obtained.connect(self.populate_legend)

    @QtCore.Slot()
    def populate_legend(self, bead_matches):
        values = bead_matches.values()
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for bead in values:
            legend_entry = QtWidgets.QWidget()
            legend_entry_layout = QtWidgets.QHBoxLayout(legend_entry)
            legend_entry_layout.setSpacing(0)
            legend_entry_layout.setContentsMargins(0, 0, 0, 0)
            legend_entry_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            legend_entry.layout = legend_entry_layout

            pixmap = QtGui.QPixmap(15, 15)
            color = QtGui.QColor.fromRgb(bead["rgb"][0], bead["rgb"][1], bead["rgb"][2])
            pixmap.fill(color)
            name_label = QtWidgets.QLabel(f"{bead['name']} ({bead['count']})")
            name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            color_label = QtWidgets.QLabel()
            color_label.setPixmap(pixmap)
            color_label.setMargin(6)
            legend_entry.layout.addWidget(color_label)
            legend_entry.layout.addWidget(name_label)
            self.layout.addWidget(legend_entry)


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