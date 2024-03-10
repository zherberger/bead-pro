import color_utils
import bead_colors
import sys

perler_colors = bead_colors.PERLER_BEADS
matches = []
input_rgb = [int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])]


def get_distance(match):
    return match["distance"]


for bead in perler_colors:
    distance = color_utils.compute_color_distance(color_utils.srgb_to_lab(bead["rgb"]),
                                                  color_utils.srgb_to_lab(input_rgb))
    matches.append({"name": bead["name"], "distance": distance})

matches.sort(key=get_distance)

for match in matches:
    print(match)
