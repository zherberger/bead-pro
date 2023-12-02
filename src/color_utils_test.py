import color_utils
import sys

xyz = color_utils.srgb_to_xyz([int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])])
lab = color_utils.xyz_to_lab(xyz)

print("XYZ: ", xyz)
print("LAB: ", lab)