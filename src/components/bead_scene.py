from PySide6 import QtCore, QtWidgets, QtGui
from PIL import Image
from src.colors.color_utils import srgb_to_lab
from src.colors.color_utils import compute_color_distance
from src.colors.bead_colors import PERLER_BEADS, PERLER_BEADS_MAP
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


def get_all_bead_matches(rgb):
    matches = []

    for bead in PERLER_BEADS:
        distance = compute_color_distance(srgb_to_lab(bead["rgb"]), srgb_to_lab(rgb))
        matches.append({**bead, "distance": distance})

    matches.sort(key=lambda match: match["distance"])
    return matches


class BeadWorkflow(QtWidgets.QWidget):
    bead_matches_obtained = Signal(object)
    bead_color_overridden = Signal(str, str)

    def __init__(self, image_loaded):
        super().__init__()
        self.bead_matches = None
        self.bead_data = None
        self.image_data = None
        self.bead_legend = None
        self.bead_color_overrides = {}
        self.layout = QtWidgets.QHBoxLayout(self)

        self.original_view = BeadView()
        self.bead_view = BeadView()

        bead_widget = QtWidgets.QWidget()
        bead_widget_layout = QtWidgets.QHBoxLayout(bead_widget)
        bead_widget_layout.addWidget(self.bead_view)
        bead_widget_layout.addWidget(BeadLegend(self.bead_matches_obtained, self.bead_color_overridden))
        bead_widget.setLayout(bead_widget_layout)
        image_loaded.connect(self.load_image)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.original_view, "Original")
        self.tabs.addTab(bead_widget, "Beads")
        self.layout.addWidget(self.tabs)

        self.bead_color_overridden.connect(self.replace_bead_color)

    @QtCore.Slot()
    def load_image(self, file_name):
        im = Image.open(file_name)
        pixels = list(im.getdata())
        width, height = im.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        self.image_data = pixels
        self.bead_matches = self.generate_bead_matches()
        self.bead_color_overrides = {}
        self.draw_image()

    def draw_image(self):
        self.original_view.draw_image(self.image_data)
        self.bead_data = []
        row_num = 0

        for row in self.image_data:
            self.bead_data.append([])
            for pixel in row:
                if pixel[3] == 255:
                    match = self.bead_matches.get(get_hex_key(pixel))["name"]
                    if self.bead_color_overrides.get(match) is not None:
                        match = self.bead_color_overrides.get(match)

                    self.bead_data[row_num].append(PERLER_BEADS_MAP[match]["rgb"] + [255])
                else:
                    self.bead_data[row_num].append([0, 0, 0, 0])
            row_num += 1

        self.bead_view.draw_image(self.bead_data)

        legend_entries = self.bead_matches.values()
        for entry in legend_entries:
            if self.bead_color_overrides.get(entry["name"]) is not None:
                entry["name"] = self.bead_color_overrides.get(entry["name"])
        self.bead_matches_obtained.emit(legend_entries)

        self.tabs.setCurrentIndex(1)

    def replace_bead_color(self, orig_bead_name, new_bead_name):
        print(f"{orig_bead_name} replaced by {new_bead_name}")
        filtered_overrides = {}

        # Get rid of any existing mappings to the original color, to prevent looping through override mappings.
        for key, value in self.bead_color_overrides.items():
            if value != orig_bead_name:
                filtered_overrides[key] = value
        self.bead_color_overrides = filtered_overrides
        self.bead_color_overrides[orig_bead_name] = new_bead_name
        self.draw_image()

    def generate_bead_matches(self):
        bead_matches = {}

        for row in self.image_data:
            for pixel in row:
                if pixel[3] == 255:
                    rgb = pixel[0:3]
                    key = get_hex_key(rgb)
                    if bead_matches.get(key) is None:
                        bead_matches[key] = {"name": get_closest_bead(rgb)["name"], "count": 1}
                    else:
                        bead_matches[key]["count"] += 1

        return bead_matches


class BeadLegend(QtWidgets.QWidget):
    def __init__(self, bead_matches_obtained, bead_color_overridden):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.bead_matches_obtained = bead_matches_obtained
        self.bead_matches_obtained.connect(self.populate_legend)
        self.bead_color_overridden = bead_color_overridden

    @QtCore.Slot()
    def populate_legend(self, bead_matches):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        bead_color_counts = {}

        for bead_match in bead_matches:
            if bead_color_counts.get(bead_match["name"]) is None:
                bead_color_counts[bead_match["name"]] = bead_match["count"]
            else:
                bead_color_counts[bead_match["name"]] += bead_match["count"]

        sorted_color_counts = list(bead_color_counts.items())
        sorted_color_counts.sort(key=lambda x: x[1], reverse=True)

        for entry in sorted_color_counts:
            self.layout.addWidget(BeadLegendEntry(entry[0], entry[1], self.bead_color_overridden))


class BeadLabel(QtWidgets.QWidget):
    def __init__(self, bead_name, count=None):
        super().__init__()
        self.bead = PERLER_BEADS_MAP[bead_name]
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        pixmap = QtGui.QPixmap(15, 15)
        color = QtGui.QColor.fromRgb(self.bead["rgb"][0], self.bead["rgb"][1], self.bead["rgb"][2])
        pixmap.fill(color)
        name_label = QtWidgets.QLabel(f"{self.bead['name']} {'(' + str(count) + ')' if count is not None else ''}")
        name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        color_label = QtWidgets.QLabel()
        color_label.setPixmap(pixmap)
        color_label.setMargin(6)
        self.layout.addWidget(color_label)
        self.layout.addWidget(name_label)


class BeadAction(QtWidgets.QWidgetAction):
    def __init__(self, bead_name, parent=None):
        super().__init__(parent)
        self.bead_name = bead_name
        self.setDefaultWidget(BeadLabel(bead_name))

    def identify(self):
        print(self.bead_name)


class BeadLegendEntry(BeadLabel):
    def __init__(self, bead_name, count=None, bead_color_overridden=None):
        super().__init__(bead_name, count)
        self.bead_color_overridden = bead_color_overridden

    def get_bead_choices(self):
        matches = get_all_bead_matches(self.bead["rgb"])
        actions = []

        for i in range(10):
            action = BeadAction(matches[i]["name"])
            actions.append(action)
        return actions

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        choices = self.get_bead_choices()
        for choice in choices:
            menu.addAction(choice)
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is not None and self.bead_color_overridden is not None:
            self.bead_color_overridden.emit(self.bead["name"], action.bead_name)


class BeadView(QtWidgets.QGraphicsView):
    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)
        self.setGeometry(QtCore.QRect(100, 100, 600, 250))
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(QtCore.QRectF())
        self.setScene(self.scene)
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.PenStyle.NoPen)
        self.PIXEL_WIDTH = 16
        self.PIXEL_HEIGHT = 16
        self.BACKGROUND_PIXEL_WIDTH = 8
        self.BACKGROUND_PIXEL_HEIGHT = 8

    def draw_image(self, image_data):
        self.draw_transparency(image_data)

        for i in range(len(image_data)):
            for j in range(len(image_data[0])):
                rgba = image_data[i][j]
                if rgba is not None and rgba[3] == 255:
                    self.scene.addRect(j * self.PIXEL_WIDTH, i * self.PIXEL_HEIGHT, self.PIXEL_WIDTH, self.PIXEL_HEIGHT,
                                       self.pen, QtGui.QBrush(QtGui.QColor(rgba[0], rgba[1], rgba[2])))

    def draw_transparency(self, image_data):
        for i in range(2 * len(image_data)):
            for j in range(2 * len(image_data[0])):
                if (i + j) % 2 == 0:
                    self.scene.addRect(j * self.BACKGROUND_PIXEL_WIDTH, i * self.BACKGROUND_PIXEL_HEIGHT,
                                       self.BACKGROUND_PIXEL_WIDTH, self.BACKGROUND_PIXEL_HEIGHT, self.pen,
                                       QtGui.QBrush(QtGui.QColor(200, 200, 200)))
                else:
                    self.scene.addRect(j * self.BACKGROUND_PIXEL_WIDTH, i * self.BACKGROUND_PIXEL_HEIGHT,
                                       self.BACKGROUND_PIXEL_WIDTH, self.BACKGROUND_PIXEL_HEIGHT, self.pen,
                                       QtGui.QBrush(QtGui.QColor(144, 144, 144)))
