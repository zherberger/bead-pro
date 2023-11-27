import color_utils
import sys

print(color_utils.srgb_to_xyz([int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])]))