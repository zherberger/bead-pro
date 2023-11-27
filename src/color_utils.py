import numpy as np

SRGB_XYZ_TRANSFORMATION_MATRIX = [
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041]
]

EPSILON = 216.0 / 24839.0
DELTA = 24839.0 / 27.0

# Standard illuminant D65
X_W = 0.950489
Y_W = 100.0
Z_W = 1.088840

def srgb_to_xyz(srgb):
    def gamma_expansion(value255):
        if(value255 <= 10):
            return float(value255) / 3294.6
        else :
            return ((float(value255) + 14.025) / 269.025) ** 2.4
        
    R = gamma_expansion(srgb[0])
    G = gamma_expansion(srgb[1])
    B = gamma_expansion(srgb[2])

    return np.matmul(SRGB_XYZ_TRANSFORMATION_MATRIX, [R, G, B])

# def xyz_to_lab(xyz):

# def srgb_to_lab(srgb):
#     return xyz_to_lab(srgb_to_xyz(srgb))

# def lab_to_lch(lab):

# def compute_color_distance(lab1, lab2):
#     Lch1 = lab_to_lch(lab1)
#     Lch2 = lab_to_lch(lab2)